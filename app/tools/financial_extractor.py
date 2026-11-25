
import re
from pathlib import Path
from typing import Any

import fitz
from bs4 import BeautifulSoup
from langchain_core.tools import tool


METRIC_PATTERNS = {
    "net_profit_inr_crore": [
        r"(?:Net profit|Profit for the period)\s*[:|]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+)"
    ],
    "operating_margin_pct": [
        r"Operating margin\s*[:|]?\s*([\d.]+)\s*%"
    ],
    "net_margin_pct": [
        r"Net margin\s*[:|]?\s*([\d.]+)\s*%"
    ],
    "tcv_usd_billion": [
        r"(?:TCV|Total Contract Value)\s*[:|]?\s*US?\$?\s*([\d.]+)\s*(?:billion|bn)"
    ],
    "annualized_ai_revenue_usd_billion": [
        r"(?:Annualized AI Revenue|AI services revenue)\s*[:|]?\s*US?\$?\s*([\d.]+)\s*(?:billion|bn)"
    ],
}


def extract_text(path: str) -> str:
    p = Path(path)

    if p.suffix.lower() == ".pdf":
        with fitz.open(path) as doc:
            return "\n".join(page.get_text("text") for page in doc)

    raw = p.read_text(encoding="utf-8", errors="ignore")

    if p.suffix.lower() in {".html", ".htm"}:
        return BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)

    return raw


def extract_revenue_from_lines(text: str) -> str | None:
    lines = text.splitlines()

    for i, line in enumerate(lines):
        heading = line.strip().lower()

        if heading in {"revenue from operations", "revenue"}:
            for next_line in lines[i + 1:i + 10]:
                numbers = re.findall(r"[\d,]+", next_line)

                for number in numbers:
                    value = int(number.replace(",", ""))
                    if value >= 1000:
                        return str(value)

    pattern = (
        r"revenue(?:\s+from\s+operations)?"
        r"\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).replace(",", "")

    return None


def extract_metrics_from_text(
    text: str,
    source: str = "document"
) -> dict[str, Any]:

    clean = re.sub(r"\s+", " ", text)

    out = {
        "source": source,
        "metrics": {}
    }

    revenue = extract_revenue_from_lines(text)

    if revenue:
        out["metrics"]["revenue_inr_crore"] = revenue

    for key, patterns in METRIC_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, clean, re.IGNORECASE)

            if match:
                out["metrics"][key] = match.group(1).replace(",", "")
                break

    return out


@tool
def financial_data_extractor_tool(document_paths: list[str]) -> dict:
    """Extract financial metrics from quarterly reports."""

    results = []

    for path in document_paths:
        try:
            text = extract_text(path)
            results.append(extract_metrics_from_text(text, path))

        except Exception as exc:
            results.append({
                "source": path,
                "error": str(exc),
                "metrics": {}
            })

    return {"documents": results}
