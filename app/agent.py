
import json
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.schemas import ForecastResponse
from app.tools.financial_extractor import financial_data_extractor_tool
from app.tools.qualitative_rag import qualitative_analysis_tool


MASTER_PROMPT = """
You are a cautious corporate financial research analyst.

Use ONLY the supplied financial metrics and transcript evidence.
Never invent facts, management guidance, dates or numeric forecasts.

IMPORTANT FINANCIAL RULES:
1. Use the supplied calculated growth percentages.
2. Do not confuse financial amounts with growth percentages.
3. Clearly distinguish reported figures from calculated figures.
4. Include revenue and net profit trends.
5. Use only comparable periods.

MANAGEMENT OUTLOOK:
1. Extract management's actual statements about revenue growth,
   business demand, AI revenue and monetization, deal pipeline,
   geopolitical risks, margins, project completions, new project
   ramp-ups and upcoming quarter outlook.
2. Distinguish management statements from analyst questions.
3. Do not leave management_outlook empty when relevant evidence exists.

FORECAST:
1. Provide a cautious qualitative outlook for the upcoming quarter.
2. Explain opportunities, risks and assumptions.
3. Never manufacture numerical revenue or profit guidance.
4. Set confidence based on the quality and quantity of evidence.

EVIDENCE:
Cite the actual source filenames in evidence_notes.
Do not cite sources that were not supplied.

Return valid JSON matching the supplied schema.
"""


def _json_safe(value):
    return json.dumps(value, ensure_ascii=False, default=str)


def _calculate_growth(prior, latest):
    try:
        prior_value = float(prior)
        latest_value = float(latest)

        if prior_value == 0:
            return None

        return round(
            ((latest_value - prior_value) / prior_value) * 100,
            2
        )

    except (TypeError, ValueError):
        return None


def _build_financial_analysis(financial):
    documents = financial.get("documents", [])

    if len(documents) < 2:
        raise ValueError(
            "At least two financial reports are required."
        )

    prior_doc = documents[-2]
    latest_doc = documents[-1]

    prior_metrics = prior_doc.get("metrics", {})
    latest_metrics = latest_doc.get("metrics", {})

    revenue_growth = _calculate_growth(
        prior_metrics.get("revenue_inr_crore"),
        latest_metrics.get("revenue_inr_crore")
    )

    profit_growth = _calculate_growth(
        prior_metrics.get("net_profit_inr_crore"),
        latest_metrics.get("net_profit_inr_crore")
    )

    return {
        "documents": documents,
        "sequential_comparison": {
            "prior_period": Path(prior_doc["source"]).name,
            "latest_period": Path(latest_doc["source"]).name,

            "revenue": {
                "prior_value_inr_crore":
                    prior_metrics.get("revenue_inr_crore"),
                "latest_value_inr_crore":
                    latest_metrics.get("revenue_inr_crore"),
                "growth_percentage": revenue_growth
            },

            "net_profit": {
                "prior_value_inr_crore":
                    prior_metrics.get("net_profit_inr_crore"),
                "latest_value_inr_crore":
                    latest_metrics.get("net_profit_inr_crore"),
                "growth_percentage": profit_growth
            }
        }
    }


def run_forecast(task, quarter_files, transcript_files, periods):

    # Step 1: Extract financial information
    financial = financial_data_extractor_tool.invoke({
        "document_paths": quarter_files
    })

    # Step 2: Calculate financial growth
    financial_analysis = _build_financial_analysis(financial)

    # Step 3: Prepare management analysis question
    question = (
        "Find management's actual statements about revenue growth, "
        "business demand, AI revenue and monetization, deal pipeline, "
        "geopolitical risks, margins, project completions, "
        "new project ramp-ups and upcoming quarter outlook. "
        "Distinguish management statements from analyst questions. "
        "User task: " + task
    )

    # Step 4: Retrieve transcript evidence
    qualitative = qualitative_analysis_tool.invoke({
        "question": question,
        "transcript_paths": transcript_files
    })

    # Step 5: Connect to local Ollama model
    llm = ChatOpenAI(
        model="qwen3:8b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=0
    )

    # Step 6: Prepare forecasting prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", MASTER_PROMPT),
        (
            "human",
            "Periods: {periods}\n"
            "Task: {task}\n"
            "Financial analysis with calculated growth: {financial}\n"
            "Transcript evidence: {qualitative}\n"
            "Return the complete structured forecast JSON."
        )
    ])

    # Step 7: Generate structured forecast
    chain = prompt | llm.with_structured_output(ForecastResponse)

    result = chain.invoke({
        "periods": ", ".join(periods),
        "task": task,
        "financial": _json_safe(financial_analysis),
        "qualitative": _json_safe(qualitative)
    })

    output = result.model_dump()

    # Step 8: Add mathematically calculated growth percentages
    comparison = financial_analysis["sequential_comparison"]

    for metric in output["financial_trends"]:
        name = metric["name"].lower()

        if "revenue" in name:
            metric["growth_percentage"] = (
                comparison["revenue"]["growth_percentage"]
            )

        elif "profit" in name:
            metric["growth_percentage"] = (
                comparison["net_profit"]["growth_percentage"]
            )

    # Step 9: Collect source filenames for evidence
    sources = set()

    for document in financial.get("documents", []):
        sources.add(Path(document["source"]).name)

    for evidence in qualitative.get("evidence", []):
        source = evidence.get("source")

        if source:
            sources.add(Path(source).name)

    output["evidence_notes"] = list(
        dict.fromkeys(
            output.get("evidence_notes", []) + sorted(sources)
        )
    )

    # Step 10: Return final forecast
    return output
