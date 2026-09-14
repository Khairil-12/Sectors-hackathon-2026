# Product Requirements Document (PRD)

## Project Title: AI IDX Investment Research Copilot

---

## 1. Executive Summary

### 1.1 Product Overview

**AI IDX Investment Research Copilot** is an intelligent conversational and analytical copilot for Indonesia Stock Exchange (IDX) equity research. The system bridges natural language user queries with raw market data supplied by the Sectors Financial API (`https://api.sectors.app`), leveraging **Groq Cloud** with structured JSON output enforcement to guarantee schema-compliant, hallucination-free financial synthesis.

### 1.2 Tech Stack Architecture

- **Backend Framework:** Python 3.11+, Django 5.x / Django REST Framework (DRF)
- **LLM Provider:** Groq Cloud (`https://api.groq.com/openai/v1`) using the OpenAI Python SDK
- **Data Source:** Sectors Financial API v2 (IDX Endpoints)
- **Output Format:** Strict JSON schema via Groq Structured Outputs (`json_schema`)
- **Database:** PostgreSQL (production) / SQLite (development)
- **Cache & Async Layer:** Django Cache (API credit conservation)

---

## 2. Problem Statement & Target Audience

### 2.1 Problem Statement

- Retail and institutional investors struggle to synthesize fragmented IDX data (fundamentals, broker flow, foreign flow, technical momentum, corporate actions).
- Existing LLM financial bots hallucinate numbers, prices, and dates because they lack rigid schema bindings to authoritative real-time APIs.
- Sectors API consumption incurs credit costs per request; unoptimized queries waste API quota.

### 2.2 Target Audience

- Retail Stock Investors in IDX looking for fundamental and bandarmology/broker data.
- Financial Analysts conducting rapid preliminary equity screens and comparisons.
- Hackathon evaluators requiring a robust end-to-end AI agent implementation.

---

## 3. System Architecture & Request Lifecycle

```
[ User Input (NL Query) ]
          │
          ▼
[ Django View / REST API ]
          │
          ▼
[ Step 1: Intent Extraction Agent (Groq + Structured Output) ]
  - Parse ticker(s), date range, metrics, analytical mode
  - Output: IntentPayload (JSON)
          │
          ▼
[ Step 2: Sectors API Gateway & Dispatcher (Python/Requests) ]
  - Check Django cache for valid non-expired payload
  - Fetch: /v2/company/, /v2/daily/, /v2/broker-summary/, /v2/foreign-flow/, etc.
  - Handle rate limits (429), not-founds (404), empty payloads
          │
          ▼
[ Step 3: Synthesis & Copilot Analysis Agent (Groq + Structured Output) ]
  - Inject real Sectors API data into prompt context
  - Generate structured research report (Bullish, Bearish, Valuation, Flow, Citations)
  - Output: ResearchReportPayload (JSON)
          │
          ▼
[ Django Serialization & HTTP Response (JSON/UI render) ]
```

---

## 4. Groq Cloud & LLM Integration Specification

### 4.1 Client Configuration

```python
import os
from openai import OpenAI

groq_client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
```

### 4.2 Agent 1: Intent & Query Parser (Structured Output)

#### Schema Definition

```python
INTENT_PARSER_SCHEMA = {
    "type": "object",
    "properties": {
        "analysis_type": {
            "type": "string",
            "enum": ["single_stock", "comparison", "screener", "broker_flow", "macro_sector", "news_filings"]
        },
        "symbols": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of 4-letter IDX symbols in uppercase without .JK suffix, e.g. ['BBCA', 'BMRI']"
        },
        "sector_slug": {
            "type": "string",
            "description": "Kebab-case slug if sector query, e.g. 'banks', 'basic-materials'"
        },
        "date_range": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "YYYY-MM-DD"},
                "end": {"type": "string", "description": "YYYY-MM-DD"}
            },
            "required": ["start", "end"],
            "additionalProperties": False
        },
        "required_endpoints": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "company_report",
                    "quarterly_financials",
                    "daily_transaction",
                    "broker_summary_top",
                    "foreign_flow",
                    "news",
                    "corporate_actions",
                    "sector_report",
                    "screener"
                ]
            }
        },
        "user_goal_summary": {"type": "string"}
    },
    "required": ["analysis_type", "symbols", "required_endpoints", "user_goal_summary"],
    "additionalProperties": False
}
```

### 4.3 Agent 2: Financial Synthesis Copilot (Structured Output)

#### Schema Definition

```python
COPILOT_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "analyzed_symbols": {
            "type": "array",
            "items": {"type": "string"}
        },
        "fundamental_analysis": {
            "type": "object",
            "properties": {
                "valuation_verdict": {"type": "string", "enum": ["undervalued", "fair", "overvalued", "inconclusive"]},
                "pe_pb_commentary": {"type": "string"},
                "revenue_profit_trend": {"type": "string"},
                "segment_insights": {"type": "string"}
            },
            "required": ["valuation_verdict", "pe_pb_commentary", "revenue_profit_trend"],
            "additionalProperties": False
        },
        "flow_and_momentum": {
            "type": "object",
            "properties": {
                "foreign_flow_sentiment": {"type": "string", "enum": ["strong_inflow", "mild_inflow", "neutral", "outflow"]},
                "net_foreign_amount_idr": {"type": "number"},
                "top_broker_action": {"type": "string"},
                "price_trend_summary": {"type": "string"}
            },
            "required": ["foreign_flow_sentiment", "price_trend_summary", "top_broker_action"],
            "additionalProperties": False
        },
        "bullish_drivers": {
            "type": "array",
            "items": {"type": "string"}
        },
        "bearish_risks": {
            "type": "array",
            "items": {"type": "string"}
        },
        "catalysts_and_news": {
            "type": "array",
            "items": {"type": "string"}
        },
        "data_citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_endpoint": {"type": "string"},
                    "as_of_date": {"type": "string"},
                    "key_datapoints": {"type": "string"}
                },
                "required": ["source_endpoint", "as_of_date", "key_datapoints"],
                "additionalProperties": False
            }
        },
        "disclaimer": {"type": "string"}
    },
    "required": [
        "title",
        "summary",
        "analyzed_symbols",
        "fundamental_analysis",
        "flow_and_momentum",
        "bullish_drivers",
        "bearish_risks",
        "data_citations",
        "disclaimer"
    ],
    "additionalProperties": False
}
```

---

## 5. Sectors API Integration Scope (IDX)

| Domain               | Sectors Endpoint                          | Usage in Copilot                                  |
| -------------------- | ----------------------------------------- | ------------------------------------------------- |
| **Screener**         | `GET /v2/screener/?q=...` or `?where=...` | Natural language screening & structured queries   |
| **Fundamentals**     | `GET /v2/company/{symbol}/`               | Financial ratios, overview, peer comps            |
| **Quarterly**        | `GET /v2/quarterly/{symbol}/`             | Quarterly earnings & balance sheet progression    |
| **Segments**         | `GET /v2/company-segments/{symbol}/`      | Revenue/cost breakdown by business unit           |
| **Transactions**     | `GET /v2/daily/{symbol}/`                 | 90-day price, volume, market cap historicals      |
| **Brokers**          | `GET /v2/broker-summary/{symbol}/top/`    | Institutional vs retail accumulation/distribution |
| **Foreign Flow**     | `GET /v2/foreign-flow/{symbol}/`          | Daily foreign institutional net inflow/outflow    |
| **Corporate Action** | `GET /v2/corporate-actions/{symbol}/`     | Dividends, splits, rights issues                  |
| **News & Filings**   | `GET /v2/news/` & `GET /v2/filings/`      | Insider transactions and regulatory announcements |
| **Suspensions**      | `GET /v2/suspensions/`                    | Risk checks on compliance / trade suspension      |

---

## 6. Functional Requirements

### FR-1: Natural Language Financial Querying

- The system shall accept unstructured natural language prompts in Indonesian and English (e.g., _"Bandingkan BBCA dan BMRI dalam 30 hari terakhir, cek foreign flow dan valuasinya"_).
- The intent parser shall extract exact 4-letter IDX symbols, timeframes, and required Sectors API endpoints.

### FR-2: API Fetcher & Rate Limit / Error Handling

- The system shall execute Sectors API requests using API keys passed via `Authorization` header.
- The system shall reject invalid symbols before querying.
- The system shall handle Sectors status codes:
  - `400`: Clean user feedback without credit consumption.
  - `404`: Gracefully communicate missing symbol data.
  - `429`: Exponential backoff with queue fallback.
  - `5xx`: Fallback message without crashing user session.

### FR-3: Rigorous Financial Synthesis

- Groq Cloud LLM shall generate reports strictly conforming to `COPILOT_REPORT_SCHEMA`.
- The LLM must not invent metrics; all numbers must be grounded in the injected Sectors API payload.
- In every report, the system must output a dual perspective (Bullish vs Bearish) and explicit data citations with endpoint names and data timestamps.

### FR-4: Mandatory Regulatory Disclaimer

- Every output must append a regulatory disclaimer: _"Bukan rekomendasi beli atau jual. Analisis dihasilkan secara otomatis oleh AI berdasarkan data Sectors API untuk tujuan edukasi."_

---

## 7. Non-Functional Requirements

- **Latency:** End-to-end request processing under 4.0 seconds (utilizing Groq's high-throughput inference).
- **Security:** API keys (`GROQ_API_KEY`, `SECTORS_API_KEY`) loaded exclusively from environment variables; zero leak to client responses.
- **Cost Optimization:** Django caching for duplicate API calls within standard market trading hours (15-minute TTL on daily quotes, 24-hour TTL on company reports). Configure Django's cache backend through `CACHES`; use the local-memory backend for development and a production-ready shared backend only when deployment requires cross-process cache sharing.
- **Data Integrity:** Strict validation using Pydantic / JSON Schema before data reaches the view layer.

---

## 8. Django Project Structure

Django serves HTML templates and JSON endpoints. Tailwind compiles source CSS into Django static files. Browser code never receives `GROQ_API_KEY` or `SECTORS_API_KEY`.

```
Sectors-hackathon-2026/
├── manage.py
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── src/
│   └── research/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py                 # Prompt, symbol, date, watchlist forms
│       ├── models.py                # Saved reports, watchlist, query history
│       ├── urls.py
│       ├── views.py                 # HTML pages and JSON/API views
│       ├── serializers.py           # API response serialization
│       ├── schemas.py               # Groq JSON schemas and validation
│       ├── services/
│       │   ├── __init__.py
│       │   ├── groq_client.py       # Groq structured-output client
│       │   ├── sectors_api.py       # Sectors Financial API client
│       │   ├── cache.py             # Django cache keys, TTLs, and helpers
│       │   └── orchestrator.py      # Intent, data fetching, and synthesis flow
│       ├── templates/
│       │   └── research/
│       │       ├── workspace.html
│       │       ├── report.html
│       │       ├── comparison.html
│       │       ├── screener.html
│       │       ├── dashboard.html
│       │       ├── watchlist.html
│       │       └── saved_reports.html
│       └── tests/
│           ├── test_schemas.py
│           ├── test_sectors_api.py
│           └── test_views.py
├── templates/
│   ├── base.html                # Global document shell and Tailwind assets
│   └── components/
│       ├── app_shell.html
│       ├── sidebar.html
│       ├── mobile_header.html
│       ├── prompt_composer.html
│       ├── quick_prompt_chip.html
│       ├── loading_stepper.html
│       ├── metric_card.html
│       ├── stock_badge.html
│       ├── data_freshness_badge.html
│       ├── report_section.html
│       ├── bullish_card.html
│       ├── risk_card.html
│       ├── citation_accordion.html
│       ├── data_table.html
│       ├── pagination.html
│       ├── empty_state.html
│       ├── error_alert.html
│       ├── skeleton_card.html
│       └── disclaimer.html
├── static/
│   ├── src/
│   │   └── input.css             # Tailwind source entrypoint
│   ├── dist/
│   │   └── app.css               # Compiled CSS; generated during build
│   └── js/
│       ├── workspace.js           # Prompt submission and progress states
│       ├── report.js              # Report interactions and citations
│       └── navigation.js          # Sidebar, mobile menu, and UI state
├── frontend/
│   └── icons/                     # Optional local icon assets
└── docs/
    ├── API-doc.md
    └── PRD.md
```

### 8.1 Tailwind Build Scripts

`package.json` shall provide development and production CSS commands:

```json
{
  "scripts": {
    "dev": "tailwindcss -i ./static/src/input.css -o ./static/dist/app.css --watch",
    "build": "tailwindcss -i ./static/src/input.css -o ./static/dist/app.css --minify"
  }
}
```

`settings.py` shall configure Django template discovery and static files:

```python
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
```

Use `{% load static %}` and `{% static 'dist/app.css' %}` in `templates/base.html`. Tailwind content scanning shall include:

```javascript
export default {
  content: [
    "./templates/**/*.html",
    "./src/research/templates/**/*.html",
    "./static/**/*.js"
  ]
}
```

### 8.2 UI Route Map

| Route | View | Template | Purpose |
|---|---|---|---|
| `/` | `workspace` | `research/workspace.html` | Submit natural-language research requests |
| `/report/<id>/` | `report_detail` | `research/report.html` | View structured research report |
| `/compare/` | `comparison` | `research/comparison.html` | Compare multiple IDX symbols |
| `/screener/` | `screener` | `research/screener.html` | Search and filter IDX companies |
| `/dashboard/` | `dashboard` | `research/dashboard.html` | Market and watchlist overview |
| `/watchlist/` | `watchlist` | `research/watchlist.html` | Manage tracked symbols |
| `/saved-reports/` | `saved_reports` | `research/saved_reports.html` | Browse saved analyses |

JSON endpoints may be placed under `/api/` and must keep credentials server-side. Use Django CSRF protection for browser POST requests.

---

## 9. Implementation Reference Code (Django + Groq + Sectors)

### `src/research/services/groq_client.py`

```python
import os
import json
from openai import OpenAI
from research.schemas import INTENT_PARSER_SCHEMA, COPILOT_REPORT_SCHEMA

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def parse_user_intent(user_prompt: str) -> dict:
    response = client.responses.create(
        model="openai/gpt-oss-120b",
        instructions="You are an IDX financial intent parser. Extract tickers, date ranges, and needed Sectors API endpoints.",
        input=user_prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "idx_intent_parser",
                "schema": INTENT_PARSER_SCHEMA
            }
        }
    )
    return json.loads(response.output_text)

def generate_copilot_report(user_prompt: str, context_data: dict) -> dict:
    instructions = (
        "You are the AI IDX Investment Research Copilot. Analyze the provided IDX financial data context. "
        "Strictly cite real numbers from the context. Provide balanced bullish drivers and bearish risks. "
        "Adhere strictly to the requested JSON schema."
    )
    prompt_input = f"User Request: {user_prompt}\n\nIDX Context Data:\n{json.dumps(context_data, default=str)}"

    response = client.responses.create(
        model="openai/gpt-oss-120b",
        instructions=instructions,
        input=prompt_input,
        text={
            "format": {
                "type": "json_schema",
                "name": "idx_copilot_report",
                "schema": COPILOT_REPORT_SCHEMA
            }
        }
    )
    return json.loads(response.output_text)
```

---

## 10. UI/UX Requirements

### 10.1 UI Technology

- Use Tailwind CSS for all styling and responsive layout.
- Use Django templates for server-rendered pages.
- Use Django static files for compiled CSS and frontend assets.
- Use semantic HTML, keyboard navigation, visible focus states, and accessible labels.
- Use a responsive, mobile-first layout.
- Do not expose `GROQ_API_KEY` or `SECTORS_API_KEY` in templates, JavaScript, or browser requests.

### 10.2 Visual Direction

- Product style: professional financial terminal with approachable AI assistant behavior.
- Default theme: dark navy/slate interface with high-contrast cards and restrained accent colors.
- Primary accent: blue for actions and selected states.
- Positive data: green.
- Negative data and risk: red.
- Neutral or unavailable data: amber/gray.
- Use tabular numerals for prices, percentages, IDR values, and dates.
- Avoid decorative charts that imply precision beyond available API data.

### 10.3 Application Shell

Every authenticated page shall include:

- Desktop sidebar with product name, New Analysis, Dashboard, Watchlist, Saved Reports, and Settings.
- Mobile top bar with menu toggle and New Analysis action.
- Main content area with maximum readable width.
- User menu with logout action.
- Global status area for API errors, rate limits, stale data, and loading progress.

### 10.4 Primary Screens

#### A. Research Workspace

Purpose: primary chat and analysis workflow.

Components:

- Prompt textarea with placeholder: `Contoh: Bandingkan BBCA dan BMRI untuk 30 hari terakhir.`
- Quick prompt chips: `Analisis saham`, `Bandingkan saham`, `Cari saham`, `Cek foreign flow`, `Ringkasan market`.
- Symbol input with uppercase normalization and validation.
- Date range selector with presets: `1D`, `7D`, `30D`, `90D`, `Custom`.
- Analysis mode selector: Single Stock, Comparison, Screener, Broker Flow, Sector, News & Filings.
- Submit button showing disabled/loading state during analysis.
- Progress stepper: Understanding request, Fetching IDX data, Preparing analysis.
- Conversation history with user prompts and assistant reports.

Interaction requirements:

- Enter submits only when no modifier key is pressed; Shift+Enter creates a new line.
- Preserve the prompt when validation or API errors occur.
- Disable duplicate submissions while a request is running.
- Show endpoint-level loading status when multiple Sectors API requests run.
- Allow canceling a request when the backend supports request cancellation.

#### B. Research Report

Display structured report sections in this order:

1. Report title, analyzed symbols, and data timestamp.
2. Executive summary.
3. Valuation and fundamental analysis.
4. Price trend and momentum.
5. Foreign flow and broker activity.
6. Bullish drivers.
7. Bearish risks.
8. Catalysts, news, and corporate actions.
9. Data citations.
10. Mandatory disclaimer.

Each report shall include:

- Metric cards for relevant values such as revenue trend, profit trend, market cap, net foreign flow, and latest price.
- Bullish drivers in green-accented cards.
- Bearish risks in red-accented cards.
- Confidence or data completeness state: Complete, Partial, or Insufficient data.
- `Save report`, `Copy summary`, and `New analysis` actions.
- Expandable citation rows showing endpoint, symbol, date range, and key datapoints.

#### C. Stock Comparison View

- Show one column per symbol on desktop.
- Stack symbol cards vertically on mobile.
- Use aligned metric rows for fair comparison.
- Highlight the better or worse value only when metric direction is known.
- Mark unavailable values as `N/A`, never as zero.
- Include a neutral comparison summary rather than an automatic winner when data is incomplete.

#### D. Screener Results

- Show filter summary above results.
- Render results in a responsive table on desktop and cards on mobile.
- Include symbol, company name, sector, market cap, selected valuation metrics, and relevant growth metrics.
- Support sorting and pagination where returned by the API.
- Provide `Analyze` action per company.
- Display empty-result state with a suggestion to broaden filters.

#### E. Watchlist and Dashboard

- Show saved symbols with latest available close, daily change, market cap, foreign flow, and latest report date.
- Show stale-data badge when cached data exceeds its intended TTL.
- Allow removing symbols without page reload where possible.
- Dashboard widgets: Watchlist, Market Movers, Most Traded, Foreign Flow, and Recent Reports.
- Widgets must show source date and loading/error state.

#### F. Saved Reports

- List reports by title, symbols, created date, and last data date.
- Support search, filtering, opening, and deletion.
- Require deletion confirmation.
- Store report JSON and rendered summary separately only when needed; avoid duplicating API payloads unnecessarily.

### 10.5 Component Requirements

Create reusable Tailwind components for:

- `AppShell`
- `Sidebar`
- `MobileHeader`
- `PromptComposer`
- `QuickPromptChip`
- `LoadingStepper`
- `MetricCard`
- `StockBadge`
- `DataFreshnessBadge`
- `ReportSection`
- `BullishCard`
- `RiskCard`
- `CitationAccordion`
- `EmptyState`
- `ErrorAlert`
- `SkeletonCard`
- `DataTable`
- `Pagination`
- `Disclaimer`

Components shall support loading, empty, error, and partial-data states where applicable.

### 10.6 Tailwind Design Tokens

Define project tokens in `tailwind.config.js` or the project Tailwind configuration:

```javascript
export default {
  theme: {
    extend: {
      colors: {
        brand: {
          500: "#3b82f6",
          600: "#2563eb"
        },
        surface: {
          900: "#0f172a",
          950: "#020617"
        }
      },
      boxShadow: {
        panel: "0 10px 30px rgba(2, 6, 23, 0.25)"
      }
    }
  }
}
```

Use existing Tailwind utilities before adding custom CSS. Keep custom CSS limited to typography, chart primitives, and browser-specific fixes.

### 10.7 Responsive Breakpoints

- Mobile: below `640px`; single-column layout and stacked report sections.
- Tablet: `640px` to `1024px`; collapsible sidebar and two-column cards where space permits.
- Desktop: above `1024px`; persistent sidebar, multi-column dashboard, and comparison tables.
- Wide desktop: above `1280px`; constrain report reading width while allowing dashboard grids to expand.

### 10.8 Accessibility

- Meet WCAG 2.1 AA target for text and interactive controls.
- Use native buttons, links, inputs, tables, and headings.
- Provide labels for every form control.
- Do not communicate state using color alone.
- Add `aria-live="polite"` to analysis progress and result status regions.
- Ensure modal, dropdown, sidebar, and accordion keyboard behavior.
- Maintain visible `:focus-visible` indicators.
- Respect `prefers-reduced-motion`.

### 10.9 UI States and Error Messages

| State | Required UI |
|---|---|
| Initial | Empty workspace with example prompts |
| Loading | Skeleton report cards and progress stepper |
| Success | Structured report with citations and timestamp |
| Partial data | Warning badge listing unavailable endpoints |
| Empty result | Explanation and query refinement action |
| Invalid input | Inline field error; preserve entered values |
| `401` / `403` | Authentication or permission message without exposing secrets |
| `404` | Resource-not-found message with symbol correction hint |
| `429` | Rate-limit message and retry guidance |
| `5xx` | Temporary service error and retry action |

### 10.10 Frontend Acceptance Criteria

1. User can submit a natural-language query from mobile and desktop.
2. Loading state appears immediately and prevents duplicate submissions.
3. Successful reports render every required structured section.
4. Every displayed metric has a source date or an explicit unavailable state.
5. API errors are understandable and do not expose credentials or raw secrets.
6. Comparison layout remains readable at `375px` viewport width.
7. Keyboard users can complete an analysis without a mouse.
8. Saved reports and watchlist actions provide confirmation feedback.
9. Tailwind build produces no unused page-specific styling that duplicates existing utilities.

---

## 11. Success Metrics & Evaluation Criteria

1. **Schema Compliance:** 100% of Groq responses pass JSON schema validation.
2. **Data Grounding:** 0 hallucinated stock prices or ticker symbols (verified via citation check).
3. **Execution Speed:** Intent parsing + Sectors fetch + Groq synthesis completed in < 4 seconds.
4. **Credit Efficiency:** Zero redundant calls for identical queries via caching.
5. **Usability:** Balanced Bull/Bear thesis generated across diverse IDX sectors (Banking, Energy, Consumer, Tech).
