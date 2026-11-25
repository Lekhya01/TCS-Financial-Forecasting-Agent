# TCS Financial Forecasting Agent

## Project Overview

The TCS Financial Forecasting Agent is a FastAPI-based application that analyzes recent quarterly financial reports and earnings-call transcripts to generate a qualitative business outlook for Tata Consultancy Services (TCS).

It combines financial metric extraction, Retrieval-Augmented Generation (RAG), and a locally hosted Large Language Model (LLM) to produce an evidence-informed forecast.

## Key Features

- Extracts quarterly revenue and net profit from financial reports.
- Calculates quarter-over-quarter growth percentages.
- Uses FAISS for transcript-based semantic retrieval.
- Uses LangChain to coordinate the analysis workflow.
- Uses Ollama with the Qwen3 8B model for local LLM inference.
- Generates structured forecasts using Pydantic schemas.
- Stores forecast requests and results in MySQL.
- Exposes REST API endpoints through FastAPI.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM | Ollama – Qwen3 8B |
| LLM orchestration | LangChain |
| Document extraction | PyMuPDF, BeautifulSoup |
| Embeddings | Sentence Transformers |
| Vector database | FAISS |
| Database | MySQL |
| Data validation | Pydantic |

## Project Structure

```text
TCS_Financial_Forecasting_Agent/
│
├── app/
│   ├── main.py
│   ├── agent.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   └── tools/
│       ├── financial_extractor.py
│       └── qualitative_rag.py
│
├── data/
│   ├── documents/
│   ├── vectorstore/
│   └── sample_metrics.json
│
├── scripts/
│   └── fetch_documents.py
│
├── docs/
│   └── sources.json
│
├── .env
└── requirements.txt
```

## Data Sources

The project currently uses the following documents:

- `tcs_q1_fy27_financial_report.pdf`
- `tcs_q2_fy27_financial_report.pdf`
- `tcs_q1_fy27_transcript.html`
- `tcs_q2_fy27_transcript.html`

## Financial Analysis

The application compares Q1 FY27 and Q2 FY27 financial metrics.

| Metric | Q1 FY27 | Q2 FY27 | QoQ Growth |
|---|---:|---:|---:|
| Revenue (₹ crore) | 72,275 | 73,188 | 1.26% |
| Net Profit (₹ crore) | 13,420 | 13,934 | 3.83% |

Growth is calculated using:

`((Latest Quarter - Previous Quarter) / Previous Quarter) × 100`

## Forecasting Workflow

1. Load quarterly financial reports and earnings-call transcripts.
2. Extract financial metrics from the reports.
3. Calculate sequential quarterly growth.
4. Split transcript content into text chunks.
5. Generate embeddings and retrieve relevant transcript evidence using FAISS.
6. Send the financial analysis and retrieved evidence to the local LLM.
7. Generate a structured qualitative outlook.
8. Store the request and forecast result in MySQL.
9. Return the result through the FastAPI endpoint.

## Setup and Execution

### Prerequisites

- Python
- MySQL
- Ollama
- Qwen3 8B model

### Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configure the database

Create a MySQL database named `tcs_forecast` and configure the database connection in your private `.env` file.

Do not upload `.env` or expose database passwords.

### Prepare the LLM

Install Ollama and download the model:

```powershell
ollama pull qwen3:8b
```

Ensure the Ollama service is running before starting the API.

### Start the FastAPI application

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Health check

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

### Generate a forecast

```powershell
$body = @{
    task = "Analyze TCS Q1 FY27 and Q2 FY27 financial performance and generate a Q3 FY27 qualitative outlook."
    quarters = @("Q1 FY27", "Q2 FY27")
    include_market_data = $false
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://127.0.0.1:8000/forecast" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 600
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks application health |
| POST | `/forecast` | Generates a qualitative financial outlook |

## Current Output

The application successfully generated a Q3 FY27 qualitative outlook using Q1 FY27 and Q2 FY27 data.

The response includes:

- Executive summary
- Financial trends
- Management outlook
- Business opportunities
- Potential risks
- Forecast assumptions
- Confidence level
- Evidence source filenames

## Limitations

- The current forecast is qualitative, not a numerical prediction of future revenue or profit.
- Market data integration is not currently implemented.
- The generated management analysis should be checked against the original transcript passages.
- Source filenames are recorded, but precise page-level citations are not currently generated.
- Financial figures should be independently verified against the original reports before business use.

## Disclaimer

This project is developed for educational and technical demonstration purposes. It does not provide investment advice or represent an official TCS forecast.