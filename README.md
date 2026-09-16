# Sectors Copilot: AI IDX Investment Research Copilot

AI IDX Investment Research Copilot is an intelligent conversational equity research platform tailored for the Indonesia Stock Exchange (IDX). The platform translates natural language market inquiries into real-time financial insights by orchestrating the Sectors Financial API with Groq Cloud large language models under strict JSON schema constraints.

---

## Key Features

- **Natural Language Intent Parsing**: Automatically detects IDX ticker symbols (e.g., `BBCA`, `BBRI`, `ASII`), analytical mode, date ranges, and relevant financial endpoints from conversational prompts.
- **Strict Schema Enforcement**: Guarantees zero hallucinations on numeric metrics and stock tickers by enforcing structured JSON output validation at both intent extraction and synthesis stages.
- **Multi-Endpoint Financial Aggregation**: Consolidates company overviews, quarterly financials, daily transactions, foreign flow analysis, top broker summaries (bandarmologi), news sentiment, and corporate actions.
- **Deep Valuation and Momentum Synthesis**: Generates balanced fundamental evaluations, bullish drivers, bearish risks, valuation verdicts, and market momentum analysis with explicit data citations.
- **Built-in Stock Screener and Multi-Ticker Comparison**: Provides dedicated interfaces for comparative analysis and company filtering across market capitalization, PE ratios, and dividend yields.
- **Cache-Optimized Execution**: Utilizes Django's caching layer to eliminate duplicate API requests and conserve Sectors API credits.
- **Modern Responsive UI**: Built with Django server-rendered templates, HTMX 2.0 dynamic updates, and a Tailwind CSS v4 dark financial theme.

---

## Tech Stack

- **Backend Framework**: Python 3.12+, Django 5.1.6
- **Package & Environment Manager**: Astral uv
- **AI / LLM Orchestration**: Groq Cloud API (`openai/gpt-oss-120b`) with Structured Outputs (`response_format: json_schema`)
- **Financial Market Data**: Sectors Financial API v2 (`https://api.sectors.app`)
- **Frontend & Dynamic Interactions**: Django Templates, HTMX 2.0, Tailwind CSS v4 (via `@tailwindcss/cli`), `django-browser-reload`
- **Database**: SQLite (isolated in `database/` for local development) / PostgreSQL (production-ready)
- **Data Validation & Schemas**: Pydantic 2.11, Python standard library

---

## System Architecture

### Request Lifecycle & Multi-Agent Orchestration

```
[ User Natural Language Query ]
               │
               ▼
[ Django Workspace View / Form Validation ]
               │
               ▼
[ Step 1: Intent Extraction (Groq + INTENT_PARSER_SCHEMA) ]
  • Parses target IDX tickers (e.g. BBCA, BMRI)
  • Resolves date range (1D, 7D, 30D, 90D)
  • Identifies required Sectors API endpoints
               │
               ▼
[ Step 2: Sectors API Gateway & Cache Dispatcher ]
  • Checks Django cache for unexpired endpoint payloads
  • Dispatches parallel/sequential calls to Sectors API v2:
    - /v2/company/report/{symbol}/
    - /v2/quarterly-financial/{symbol}/
    - /v2/daily/{symbol}/
    - /v2/most-traded/
    - /v2/broker-summary/
    - /v2/news/
               │
               ▼
[ Step 3: Synthesis & Research Generation (Groq + COPILOT_REPORT_SCHEMA) ]
  • Ingests raw structured market data
  • Enforces validation on valuation verdict, drivers, risks, and citations
               │
               ▼
[ Step 4: Storage & Presentation ]
  • Persists report payload into SavedReport model
  • Renders responsive research report with citations and metric cards
```

---

## Directory Structure

```
Sectors-hackathon-2026/
├── config/                          # Core Django project configuration
│   ├── __init__.py
│   ├── asgi.py                      # ASGI entrypoint
│   ├── settings.py                  # Project settings (database, cache, apps, keys)
│   ├── urls.py                      # Global URL routing
│   └── wsgi.py                      # WSGI entrypoint
├── database/                        # Local database storage (git-ignored)
│   └── db.sqlite3
├── docs/                            # Reference documentation
│   └── sectors_api_docs/            # Sectors Financial API v2 endpoint references
├── src/                             # Application source code
│   └── research/                    # Main equity research application
│       ├── migrations/              # Database schema migrations
│       ├── services/                # Business logic and external integrations
│       │   ├── cache.py             # TTL-based response caching utilities
│       │   ├── groq_client.py       # Groq API client with JSON schema enforcement
│       │   ├── orchestrator.py      # Multi-step analysis workflow coordinator
│       │   └── sectors_api.py       # Sectors Financial API wrapper functions
│       ├── templates/research/      # Application-specific templates
│       │   ├── comparison.html      # Multi-ticker comparison view
│       │   ├── dashboard.html       # Research dashboard
│       │   ├── report.html          # Full structured research report
│       │   ├── saved_reports.html   # Historical report manager
│       │   ├── screener.html        # Stock screening table and filters
│       │   ├── watchlist.html       # User ticker watchlist
│       │   └── workspace.html       # Primary conversational chat interface
│       ├── tests/                   # Automated unit and integration test suite
│       │   ├── test_schemas.py      # JSON schema validation tests
│       │   ├── test_sectors_api.py  # API client and cache unit tests
│       │   └── test_views.py        # HTTP view and routing tests
│       ├── admin.py                 # Django admin registrations
│       ├── apps.py                  # App configuration (ResearchConfig)
│       ├── forms.py                 # Form definitions
│       ├── models.py                # Database models (SavedReport, WatchlistItem)
│       ├── schemas.py               # JSON schema definitions for Groq
│       ├── serializers.py           # Serialization helpers
│       ├── urls.py                  # Research URL route definitions
│       └── views.py                 # HTTP view controllers
├── static/                          # Static assets
│   ├── dist/                        # Compiled CSS output (app.css)
│   └── src/                         # Input styles (input.css)
├── templates/                       # Base layouts and reusable UI partials
│   ├── components/                  # Header, sidebar, metric card components
│   └── base.html                    # Base HTML layout with Tailwind & HTMX
├── .env.template                    # Template for environment configuration
├── .gitignore                       # Git ignore rules
├── manage.py                        # Django management script
├── package.json                     # Node.js dependencies and build scripts
├── PRD.md                           # Product Requirements Document
├── pyproject.toml                   # Python project metadata and dependencies
├── tailwind.config.js               # Tailwind CSS theme configuration
└── uv.lock                          # Locked Python dependency graph
```

---

## Prerequisites

Ensure the following tools and accounts are set up before running the project:

- **Python**: Version `3.12` or higher
- **uv**: Modern, high-performance Python package installer and resolver ([Installation Guide](https://github.com/astral-sh/uv))
- **Node.js**: Version `20.x` or higher and `npm` (for Tailwind CSS v4 compilation)
- **Groq API Key**: Obtainable from [Groq Cloud Console](https://console.groq.com/)
- **Sectors Financial API Key**: Obtainable from [Sectors App](https://sectors.app/)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Khairil-12/Sectors-hackathon-2026.git
cd Sectors-hackathon-2026
```

### 2. Configure Environment Variables

Copy `.env.template` to `.env` and provide your API keys:

```bash
# Windows (PowerShell)
Copy-Item .env.template .env

# Linux / macOS
cp .env.template .env
```

Edit `.env` with your active credentials:

```ini
GROQ_API_KEY=gsk_your_actual_groq_api_key
SECTORS_API_KEY=your_actual_sectors_api_key
DJANGO_SECRET_KEY=your-secure-django-secret-key
```

### 3. Install Python Dependencies

Synchronize Python virtual environment and dependencies using `uv`:

```bash
uv sync
```

### 4. Install Frontend Dependencies and Build Styles

Install Node.js packages and compile Tailwind CSS:

```bash
npm install
npm run tailwind:build
```

### 5. Apply Database Migrations

Initialize the SQLite database located inside `database/`:

```bash
uv run python manage.py migrate
```

### 6. Run Test Suite

Verify that all schemas, API wrappers, and Django views pass system checks:

```bash
uv run python manage.py test
```

### 7. Start Local Development Servers

Run the Tailwind asset compiler and Django web server concurrently:

```bash
npm run dev
```

Alternatively, you can run the two processes in separate terminal windows:

```bash
# Terminal 1: Watch and rebuild Tailwind styles
npm run tailwind:watch

# Terminal 2: Run Django development server
uv run python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to access the application.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | - | API key for Groq Cloud LLM inference. |
| `SECTORS_API_KEY` | Yes | - | API key for Sectors Financial IDX data access. |
| `DJANGO_SECRET_KEY` | Yes | Insecure dev key | Django cryptographic signing key. |
| `DEBUG` | No | `True` (dev) / `False` (prod) | Enables Django debug mode. Set `False` in production. |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1,testserver` | Comma-separated list of permitted host headers. Never `*` in production. |
| `DATABASE_ENGINE` | No | `django.db.backends.sqlite3` | Database backend engine. |
| `DJANGO_CACHE_BACKEND` | No | `localmemory` | Cache backend: `localmemory`, `redis`, or `db`. |
| `DJANGO_CACHE_LOCATION` | No | `unique-cache` | Cache instance identifier or connection string. |
| `DJANGO_CACHE_TIMEOUT` | No | `300` | Default cache TTL in seconds. |

---

## Available Scripts and Commands

### Python & Django Operations (via uv)

| Command | Description |
|---|---|
| `uv sync` | Synchronize Python packages from `pyproject.toml` and `uv.lock`. |
| `uv run python manage.py check` | Run system consistency and configuration checks. |
| `uv run python manage.py migrate` | Apply database migrations to `database/db.sqlite3`. |
| `uv run python manage.py makemigrations` | Generate new database migration files. |
| `uv run python manage.py test` | Execute the full test suite (14+ automated tests). |
| `uv run python manage.py createsuperuser` | Create a Django administrative account. |
| `uv run python manage.py runserver` | Launch the local development server at `127.0.0.1:8000`. |

### Node.js & Frontend Operations

| Command | Description |
|---|---|
| `npm run dev` | Launch both Tailwind watcher and Django server concurrently. |
| `npm run build` | Minify and compile production CSS bundle (`static/dist/app.css`). |
| `npm run build:prod` | Build CSS bundle and run Django `collectstatic`. |
| `npm run tailwind:watch` | Watch `./static/src/input.css` and recompile to `./static/dist/app.css`. |
| `npm run tailwind:build` | Minify and compile production CSS bundle. |
| `npm run django:run` | Start Django server through npm script runner. |

### Production Deployment Build

For automated deployment pipelines (Render, Railway, Fly.io, Linux VPS, Docker):

```bash
# Execute universal automated build script:
./build.sh
```

### Deploying to Vercel

This project is fully configured for zero-configuration serverless deployment on **Vercel** with automated Tailwind CSS building and Django Serverless WSGI execution.

#### 1. Import Repository into Vercel
1. Go to [Vercel Dashboard](https://vercel.com/new).
2. Import this GitHub repository.
3. Vercel automatically detects `vercel.json`, `package.json`, and `api/index.py`.

#### 2. Configure Environment Variables in Vercel
Under **Project Settings > Environment Variables**, add:

| Variable | Value / Description |
|---|---|
| `GROQ_API_KEY` | `gsk_...` (Your Groq Cloud API key) |
| `SECTORS_API_KEY` | `...` (Your Sectors Financial API key) |
| `DJANGO_SECRET_KEY` | Strong random secret key |
| `DJANGO_DEBUG` | `False` |
| `DATABASE_URL` | *(Optional)* PostgreSQL connection string (e.g., from [Neon](https://neon.tech/)) for persistent reports |

#### 3. Deploy via Vercel CLI (Alternative)
```bash
npm install -g vercel
vercel --prod
```

---

## Testing & Quality Assurance

The project contains automated unit and integration tests covering API routing, schema structures, and external API mocking.

```bash
uv run python manage.py test
```

### Test Scope

- **`test_schemas.py`**: Validates that `INTENT_PARSER_SCHEMA` and `COPILOT_REPORT_SCHEMA` comply with JSON schema specifications and enum constraints.
- **`test_sectors_api.py`**: Verifies Sectors API URL formatting, request parameters, cache hit/miss semantics, and cache override behavior.
- **`test_views.py`**: Performs HTTP status checks on application routes, verifies HTML title tag generation, and confirms Tailwind CSS asset inclusion.

---

## Database Schema

```
SavedReport
├── id (BigAutoField, PK)
├── title (CharField, max length 255)
├── symbols (JSONField, list of analyzed IDX tickers)
├── user_prompt (TextField, original user prompt)
├── report_data (JSONField, structured report payload)
├── created_at (DateTimeField, auto timestamp)
└── updated_at (DateTimeField, auto timestamp)

WatchlistItem
├── id (BigAutoField, PK)
├── symbol (CharField, unique, max length 10)
└── added_at (DateTimeField, auto timestamp)
```

---

## Troubleshooting

### 1. Missing or Invalid API Keys

- **Symptom**: `SectorsAPIError: 401 Unauthorized` or `GroqAPIError: Invalid API Key`.
- **Solution**: Ensure `.env` is present in the repository root and contains valid `GROQ_API_KEY` and `SECTORS_API_KEY` tokens.

### 2. Styles Not Updating

- **Symptom**: Browser shows unstyled markup or Tailwind CSS changes are missing.
- **Solution**: Run `npm run tailwind:build` to produce a fresh build of `static/dist/app.css`. If running in development, ensure `npm run tailwind:watch` is active.

### 3. Database Location & Locking

- **Symptom**: Database errors indicating file permissions or missing database tables.
- **Solution**: Confirm that the `database/` directory exists at root and run `uv run python manage.py migrate` to apply migrations.

### 4. Cache Reset

- **Symptom**: Outdated Sectors API data displayed during active testing.
- **Solution**: Restart the Django server or clear the cache using Django shell:
  ```bash
  uv run python manage.py shell -c "from django.core.cache import cache; cache.clear()"
  ```

---

## Core Services Architecture

### 1. Groq Client (`src/research/services/groq_client.py`)

Orchestrates all LLM inference with Groq Cloud API using JSON schema constraints. Enforces structured outputs and graceful fallback to faster models under rate limits.

**Key Functions:**

- `parse_user_intent(prompt: str) -> dict`: Extracts intent using `INTENT_PARSER_SCHEMA`. Returns analysis type (single_stock, comparison, screener, etc.), required endpoints, date ranges, and normalized symbols.
- `generate_copilot_report(context: dict, intent: dict) -> dict`: Ingests API payloads and Groq output, generates final research report validated against `COPILOT_REPORT_SCHEMA`.
- `_call_groq_json(...)`: Internal handler for Groq API calls with automatic retry on TPM/413 errors; demotes to FAST_MODEL (`gpt-oss-20b`) if PRIMARY_MODEL (`gpt-oss-120b`) hits rate limits.
- `detect_language(text: str) -> str`: Auto-detects Indonesian vs English and enforces response language in system prompt.

**Schema Enforcement:** All responses validated against JSON schema; malformed outputs logged and re-parsed or rejected.

---

### 2. Orchestrator (`src/research/services/orchestrator.py`)

Multi-step workflow coordinator. Manages intent parsing, parallel API dispatch, data synthesis, and report generation in a single `run_analysis(prompt)` call.

**Main Functions:**

- `run_analysis(prompt: str) -> dict`: Central entry point. Validates prompt via `prompt_guard`, parses intent, fetches context data, synthesizes report, detects anomalies.
- `run_comparison(symbols: list[str], date_range: dict) -> dict`: Parallel comparison mode for 2+ tickers. Returns side-by-side valuations, flows, and momentum analysis.
- `detect_flow_divergence(context: dict, symbols: list[str]) -> list[dict]`: Identifies price-flow divergence signals (bullish/bearish mismatches).
- `_safe_dates(intent: dict) -> dict[str, str]`: Normalizes date ranges; caps at 90 days, defaults to 30D if absent.
- `_symbols(intent: dict) -> list[str]`: Validates and deduplicates IDX ticker symbols (4-letter uppercase, max 10).

**Parallelization:** Uses `ThreadPoolExecutor` to dispatch independent API calls concurrently (company report, quarterly financials, daily transactions, broker summary, foreign flow, news, corporate actions).

---

### 3. Sectors Financial API Wrapper (`src/research/services/sectors_api.py`)

Low-level HTTP client for Sectors Financial API v2 (`https://api.sectors.app`). Handles auth, caching, fallback mock data, and error recovery.

**Endpoints Covered:**

- `get_company_report(symbol)`: `/v2/company/report/{symbol}/` — valuation, financials, management, ownership.
- `get_quarterly(symbol)`: `/v2/quarterly-financial/{symbol}/` — historical quarterly P&L, balance sheet.
- `get_daily(symbol, start, end)`: `/v2/daily/{symbol}/` — OHLCV with date filtering.
- `get_broker_summary_top(symbol, start, end)`: `/v2/broker-summary/{symbol}/` — top 5 broker net buy/sell.
- `get_foreign_flow(symbol, start, end)`: `/v2/daily/{symbol}/` → filtered foreign net flow.
- `get_news(symbols, start, end)`: `/v2/news/` — sentiment and headlines.
- `get_corporate_actions(symbol)`: `/v2/corporate-actions/{symbol}/` — dividends, splits, IPO data.

**Fallback Mock Data:** Built-in fallback dataset (BBCA, BMRI, TLKM, ASII, GGRM) for offline testing and demo resilience. Triggered on network/API failures.

**Error Handling:** `SectorsAPIError(code, message, status_code)` raised on HTTP errors; logged and propagated to user as friendly messages.

---

### 4. Caching Layer (`src/research/services/cache.py` + `sectors_api.py`)

TTL-based response caching via Django's cache framework to minimize duplicate API calls and preserve Sectors API credits.

**Cache TTLs:**

| Endpoint | TTL | Rationale |
|---|---|---|
| `daily` | 900s (15m) | Intraday data updates frequently |
| `company` | 86400s (1d) | Company overview, ownership stable |
| `quarterly` | 86400s (1d) | Quarterly earnings released quarterly |
| `broker` | 900s (15m) | Broker positions update intraday |
| `news` | 1800s (30m) | News sentiment refreshes hourly |
| `screener` | 300s (5m) | Screening results dynamic |
| `reference` | 86400s (1d) | Lookup reference data stable |

**Cache Keys:** SHA256 hash of endpoint + sorted params; enables cache bypass via `force_refresh` header.

---

### 5. Data Distiller (`src/research/services/data_distiller.py`)

Compact extraction of critical metrics from raw API payloads to fit Groq's input token budget. Strips redundant/verbose fields while preserving valuation verdicts and flow signals.

**Key Distillers:**

- `distill_company_report(data)`: Extracts PE, PB, ROE, dividend yield, revenue trend, management names.
- `distill_quarterly(data)`: Last 8 quarters of revenue, net income, EBITDA; YoY growth rates.
- `distill_daily(data)`: Price range, volume, close, sorted by date (latest first).
- `distill_broker(data)`: Top 3 brokers by net buy/sell; aggregate net position.
- `distill_foreign_flow(data)`: Daily net inflow/outflow; cumulative over period; trend direction.
- `distill_news(data)`: Top 10 headlines + sentiment labels (positive/neutral/negative).

**Result:** Typically 40–50% token reduction vs raw API response, enabling richer context and lower Groq latency.

---

### 6. Prompt Guard (`src/research/services/prompt_guard.py`)

Security and domain validation layer. Prevents prompt injection, rejects non-financial queries, extracts IDX tickers early.

**Validation Pipeline:**

1. **Length Check**: Reject prompts < 3 chars.
2. **Injection Detection**: Regex patterns detect "ignore previous instructions," "jailbreak," "bypass," "reveal prompt."
3. **Ticker Extraction**: Uppercase 4-letter tokens; filter against stopwords (common Indonesian/English words like YANG, WHAT, THIS).
4. **Financial Domain Guard**: Searches for financial keywords (saham, stock, dividen, laba, sektor, valuasi, etc.). Rejects cooking, weather, coding, politics queries.
5. **Out-of-Scope Decision**: If non-financial pattern matches AND no financial context detected, return `GuardResult(is_allowed=False)` with reason and suggestions.

**Output:** `GuardResult` dataclass with `is_allowed`, `category`, `reason`, `suggested_prompts` for user guidance.

---

## JSON Schema Reference

### INTENT_PARSER_SCHEMA

Parsed by Groq; defines intent structure after user prompt analysis.

```json
{
  "analysis_type": "single_stock|comparison|screener|broker_flow|macro_sector|news_filings|out_of_scope",
  "is_valid_query": true,
  "response_language": "id|en",
  "symbols": ["BBCA", "BMRI"],
  "sector_slug": "finance|energy|...",
  "date_range": {"start": "2026-08-16", "end": "2026-09-16"},
  "required_endpoints": ["company_report", "quarterly_financials", "daily_transaction", ...],
  "user_goal_summary": "Compare valuation trends of two leading banks over past month"
}
```

**Enum Constraints:**

- `analysis_type`: Determines API call strategy (single ticker deep-dive vs multi-ticker comparison vs screener queries).
- `required_endpoints`: Groq selects subset of [company_report, quarterly_financials, daily_transaction, broker_summary_top, foreign_flow, news, corporate_actions, sector_report, screener].
- `response_language`: Enforced in final synthesis; ensures Indonesian prompts get Indonesian reports.

---

### COPILOT_REPORT_SCHEMA

Final research report structure. Returned by Groq synthesis; stored in `SavedReport.report_data`.

```json
{
  "title": "BBCA vs BMRI: Valuation Comparison (30D)",
  "summary": "Bank Central Asia trades at premium valuation despite lower net profit growth...",
  "analyzed_symbols": ["BBCA", "BMRI"],
  "fundamental_analysis": {
    "valuation_verdict": "undervalued|fair|overvalued|inconclusive",
    "pe_pb_commentary": "BMRI PE 11.8x vs BBCA 23.4x suggests...",
    "revenue_profit_trend": "Both show +5-7% YoY growth; BBCA margin expansion...",
    "segment_insights": "BBCA weighted to corporate lending..."
  },
  "flow_and_momentum": {
    "foreign_flow_sentiment": "strong_inflow|mild_inflow|neutral|outflow",
    "net_foreign_amount_idr": 234_567_000_000,
    "top_broker_action": "Mandiri Securities net buy +125M shares",
    "price_trend_summary": "BBCA +3.2% vs BMRI -1.1% over 30D..."
  },
  "risks_and_drivers": {
    "bullish_drivers": [...],
    "bearish_risks": [...],
    "critical_events": [...]
  },
  "citations": {
    "metrics": {"BBCA_PE": "23.4 (company_report)", ...},
    "data_sources": ["daily_transaction", "broker_summary_top", "news"]
  }
}
```

**Validation:** All enum fields strictly enforced; missing required fields cause synthesis retry.

---

## Template Architecture

8 Django templates in `src/research/templates/research/`:

| Template | Purpose | Key Components |
|---|---|---|
| `workspace.html` | Chat interface for natural language queries | Prompt textarea, HTMX form, recent reports sidebar, message history |
| `report.html` | Rendered equity research report | Metric cards, valuation verdict badge, flow sentiment gauge, citations section, save/export buttons |
| `dashboard.html` | Summary dashboard | Latest reports, market heat map, top gainers/losers, quick-access screener |
| `comparison.html` | Side-by-side multi-ticker analysis | Parallel cards, valuation comparison, flow divergence signals, action links |
| `screener.html` | Stock screening interface | Filter table (market cap, PE, dividend yield), preset filters, edit/save screens |
| `watchlist.html` | Personal ticker watchlist | Add/remove symbols, daily price quotes, quick compare action |
| `saved_reports.html` | Historical report archive | Sortable list (date, symbols, title), delete/re-run actions, export options |
| `followup_response.html` | AJAX response partial for follow-up questions | Nested citations, metric updates, flow context |

**Frontend Stack:**
- **HTMX 2.0**: Dynamic form submission and partial HTML swaps (no full-page reload).
- **Tailwind CSS v4**: Dark financial theme (surface-950, brand-500 accent colors).
- **Django templates**: Server-rendered; reusable component partials in `templates/components/`.

---

## Development Workflow

### Adding a New Analysis Type

1. **Update `INTENT_PARSER_SCHEMA`** (`schemas.py`):
   ```python
   "analysis_type": {..., "enum": [..., "new_type"]}
   "required_endpoints": {..., "enum": [..., "new_endpoint"]}
   ```

2. **Add endpoint handler** (`sectors_api.py`):
   ```python
   def get_new_endpoint(symbol, **params):
       """Fetch data from /v2/new-endpoint/{symbol}/"""
       # implement
   ```

3. **Add distiller** (`data_distiller.py`):
   ```python
   def distill_new_data(data):
       """Compact extraction for Groq input."""
   ```

4. **Register in orchestrator** (`orchestrator.py`):
   ```python
   SYMBOL_ENDPOINTS = {
       ...,
       "new_endpoint": lambda symbol, dates: sectors_api.get_new_endpoint(symbol, **dates),
   }
   ```

5. **Update synthesis prompt** (`groq_client.py`): Add new_endpoint context to `generate_copilot_report()` instructions.

6. **Test**: `uv run python manage.py test`

---

### Debugging Groq Token Limits

**Symptom:** Groq 413 error or timeout during synthesis.

**Diagnosis:**
```bash
# Check distiller output sizes
uv run python manage.py shell
>>> from research.services.data_distiller import distill_company_report
>>> import json
>>> data = {...}  # your API response
>>> distilled = distill_company_report(data)
>>> len(json.dumps(distilled))  # bytes
```

**Fix:**
- Reduce date range in intent (cap to 30D instead of 90D).
- Reduce symbols in comparison (max 2–3 instead of 5+).
- Further trim distiller fields (e.g., remove news headlines, keep top 3 only).
- Activate FAST_MODEL fallback by lowering `max_tokens` in `_call_groq_json()`.

---

### Testing the Full Pipeline

```bash
# Unit tests (schemas, cache, API wrapper)
uv run python manage.py test research.tests.test_schemas
uv run python manage.py test research.tests.test_sectors_api

# Integration test (orchestrator + Groq)
uv run python manage.py test research.tests.test_orchestrator

# View test output with verbosity
uv run python manage.py test -v 2
```

---

## API Request/Response Flow Examples

### Example 1: Single Stock Analysis

**User Prompt:**
```
Analisis fundamental BBCA, bagaimana valuasinya saat ini?
```

**Step 1: Intent Parsing** (Groq + INTENT_PARSER_SCHEMA)
```json
{
  "analysis_type": "single_stock",
  "symbols": ["BBCA"],
  "date_range": {"start": "2026-08-17", "end": "2026-09-16"},
  "required_endpoints": ["company_report", "quarterly_financials", "daily_transaction", "broker_summary_top", "news"],
  "user_goal_summary": "Evaluate fundamental valuation of BBCA"
}
```

**Step 2: Parallel API Dispatch** (Orchestrator + Sectors API)
```
BBCA_company_report   → /v2/company/report/BBCA/
BBCA_quarterly        → /v2/quarterly-financial/BBCA/
BBCA_daily            → /v2/daily/BBCA/?start=...&end=...
BBCA_broker           → /v2/broker-summary/BBCA/?start=...&end=...
BBCA_news             → /v2/news/?symbols=BBCA&start=...&end=...
```

**Step 3: Data Distillation** (Data Distiller)
```python
context = {
    "BBCA_company_report": {
        "pe_ratio": 23.4,
        "pb_ratio": 4.8,
        "dividend_yield": 0.024,
        "roe": 0.215,
        "revenue_trend": "+5.2% YoY"
    },
    "BBCA_quarterly": [
        {"quarter": "Q2 2026", "revenue": 24.6e12, "net_income": 12.15e12},
        {"quarter": "Q1 2026", "revenue": 23.8e12, "net_income": 11.9e12}
    ],
    "BBCA_daily": [
        {"date": "2026-09-16", "close": 8850, "volume": 125_400_000, "change": 0.56},
        {"date": "2026-09-15", "close": 8800, "volume": 98_200_000, "change": -0.34}
    ],
    "BBCA_broker": {"top_buyers": ["Mandiri", "RZB"], "net_position": "+45.2M shares"},
    "BBCA_news": [{"headline": "BBCA raises dividend payout", "sentiment": "positive"}]
}
```

**Step 4: Report Synthesis** (Groq + COPILOT_REPORT_SCHEMA)
```json
{
  "title": "BBCA Fundamental Analysis",
  "summary": "Bank Central Asia maintains strong profitability with stable dividend policy. Trading at premium valuation relative to sector peers.",
  "analyzed_symbols": ["BBCA"],
  "fundamental_analysis": {
    "valuation_verdict": "fair",
    "pe_pb_commentary": "PE 23.4x above banking sector average (~18x), justified by consistent ROE >20%.",
    "revenue_profit_trend": "Revenue +5.2% YoY; net income +4.8% YoY. Margin compression observed due to rising funding costs."
  },
  "flow_and_momentum": {
    "foreign_flow_sentiment": "mild_inflow",
    "net_foreign_amount_idr": 89_300_000_000,
    "top_broker_action": "Mandiri Securities accumulating +45M shares",
    "price_trend_summary": "+2.1% over 30D; consolidating above 8800."
  }
}
```

---

### Example 2: Multi-Ticker Comparison

**User Prompt:**
```
Bandingkan BBCA dan BMRI, mana yang lebih murah sekarang?
```

**Intent Parsing → Analysis Type: `comparison`**
```json
{
  "analysis_type": "comparison",
  "symbols": ["BBCA", "BMRI"],
  "required_endpoints": ["company_report", "quarterly_financials", "daily_transaction"]
}
```

**Parallel Fetch:** Fetch both symbols concurrently; distill metrics.

**Synthesis Output (COPILOT_REPORT_SCHEMA):**
```json
{
  "title": "BBCA vs BMRI: Valuation Comparison",
  "fundamental_analysis": {
    "valuation_verdict": "undervalued",
    "pe_pb_commentary": "BMRI trades at 11.8x PE vs BBCA 23.4x PE. BMRI PB 2.1x vs BBCA 4.8x suggests undervaluation.",
    "revenue_profit_trend": "BBCA net margin 49.4% vs BMRI 38.2%. BBCA shows stronger profitability; BMRI growing faster."
  },
  "flow_and_momentum": {
    "foreign_flow_sentiment": "neutral",
    "price_trend_summary": "BBCA +2.1% vs BMRI -0.8% over 30D. Divergence suggests BMRI may be setting value entry."
  },
  "citations": {
    "metrics": {
      "BBCA_PE": "23.4 (company_report)",
      "BMRI_PE": "11.8 (company_report)",
      "BBCA_PB": "4.8 (company_report)",
      "BMRI_PB": "2.1 (company_report)"
    }
  }
}
```

---

## Error Codes & Resolution

| Error | Code | Cause | Resolution |
|---|---|---|---|
| Unauthorized | `401` | Invalid/missing Sectors API key | Check `.env`, verify key at sectors.app |
| Not Found | `404` | Ticker symbol not listed on IDX | Verify symbol spelling (BBCA not BCA); check `WatchlistItem` model for valid tickers |
| Rate Limit | `429` | Too many requests to Sectors API | Increase cache TTL, reduce query frequency, enable Groq fast-model fallback |
| Token Limit | `413` | Groq input + schema exceed token budget | Reduce symbols (max 3), limit date range to 30D, prune distiller fields |
| Timeout | `504` | API unreachable or slow | Check network; retry with exponential backoff; use mock data fallback |
| Validation Error | `422` | Prompt out-of-scope or invalid format | Reword prompt to include financial keywords or IDX ticker symbols |

---

## Performance Optimization Tips

### 1. Cache Strategy

**Default TTLs** already optimize for typical usage. Adjust if needed:

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# For production, use Redis:
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        }
    }
}
```

### 2. Batch Symbol Operations

Instead of analyzing 5 symbols sequentially:
```python
# Slow (5 separate calls)
for symbol in ["BBCA", "BMRI", "ASII", "TLKM", "BBNI"]:
    run_analysis(f"Analisis {symbol}")

# Fast (1 comparison call)
run_comparison(["BBCA", "BMRI", "ASII", "TLKM", "BBNI"], {"start": "...", "end": "..."})
```

### 3. Groq Token Budget

Prioritize high-value endpoints. Edit orchestrator to skip low-priority calls:

```python
# Skip news if token budget tight
SYMBOL_ENDPOINTS = {
    "company_report": ...,
    "quarterly_financials": ...,
    # "news": ...,  # commented out
}
```

### 4. Database Indexing

Add index on frequently filtered fields:

```python
class SavedReport(models.Model):
    ...
    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['symbols']),
        ]
```

---

## Deployment Considerations

### Environment-Specific Configuration

**Development (.env):**
```ini
DEBUG=True
GROQ_API_KEY=gsk_dev_...
SECTORS_API_KEY=dev_...
DJANGO_CACHE_BACKEND=localmemory
```

**Production (.env):**
```ini
DEBUG=False
GROQ_API_KEY=gsk_prod_...
SECTORS_API_KEY=prod_...
DJANGO_CACHE_BACKEND=redis
DJANGO_CACHE_LOCATION=redis://prod-redis:6379/1
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_URL=postgresql://user:pass@db:5432/sectors
ALLOWED_HOSTS=sectors.app,www.sectors.app
CSRF_TRUSTED_ORIGINS=https://sectors.app
```

### Monitoring & Logging

Log Groq usage and Sectors API errors:

```bash
# View logs
tail -f /var/log/sectors/django.log

# Monitor cache hit rate
uv run python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()  # Reset counters
>>> # Run queries, then check stats
```

### Database Migrations on Deploy

```bash
# Before restarting app
uv run python manage.py migrate

# Verify schema is current
uv run python manage.py check
```

---

## Groq Model Selection & Tuning

### Primary Model: `openai/gpt-oss-120b`

Best for complex multi-symbol analysis, detailed flow analysis, sector comparisons.

- Pros: Larger context window, better at nuanced reasoning, lower error rate.
- Cons: Slower (2–5s), higher token cost, more prone to TPM limits.

### Fast Model: `openai/gpt-oss-20b`

Fallback for single-stock queries or token-limit scenarios.

- Pros: 10–100x faster, lower TPM, cheaper.
- Cons: Less nuanced analysis, occasional JSON parse errors.

### Tuning Response Temperature

In `groq_client.py`:

```python
def _call_groq_json(..., temperature: float = 0.1):
    # temperature=0.0: Deterministic (best for schema enforcement)
    # temperature=0.5: Balanced (default, good for reports)
    # temperature=1.0: Creative (risky for structured outputs)
```

Lower temperature → stricter schema compliance, less hallucination. Increase if Groq returns `null` fields.

---

## Security Considerations

### 1. API Key Protection

- Never commit `.env` to git. Add to `.gitignore`:
  ```
  .env
  .env.local
  secrets/
  ```
- Rotate keys quarterly.
- Use environment-specific keys (dev/prod separate).

### 2. Prompt Injection Prevention

`prompt_guard.py` detects and blocks common injection patterns:
- "ignore previous instructions"
- "reveal system prompt"
- "jailbreak"

Extend patterns if new attacks discovered:

```python
INJECTION_PATTERNS = [
    ...,
    r"your\\s+actual\\s+instructions",  # new pattern
]
```

### 3. SQL Injection & ORM Safety

Always use Django ORM; never construct raw SQL:

```python
# Safe
SavedReport.objects.filter(symbols__contains="BBCA")

# Unsafe (never do this)
# SavedReport.objects.raw(f"SELECT * FROM research_savedreport WHERE symbols LIKE '%{user_input}%'")
```

### 4. CSRF Protection

HTMX requests automatically include CSRF token via `hx-headers`:

```html
<form hx-post="/workspace" hx-csrf-token="...">
```

Verify in views:

```python
@require_http_methods(["POST"])
@csrf_protect
def workspace(request):
    ...
```

### 5. Sensitive Data in Logs

Never log API keys or user prompts containing private info:

```python
logger.info("Analysis for symbol: %s", symbol)  # OK
# logger.info("Full prompt: %s", user_prompt)  # RISKY if contains personal data
```

---

## Contributing Guidelines

### Code Style

Follow PEP 8 with line length ≤100 chars:

```bash
# Check style
pip install flake8
flake8 src/

# Auto-fix
pip install black
black src/
```

### Adding a New Feature

1. Create feature branch: `git checkout -b feat/screener-filters`
2. Implement feature with tests.
3. Run test suite: `uv run python manage.py test`
4. Update README with new API/workflow.
5. Push and create PR.

### Test Coverage

Maintain >80% coverage:

```bash
pip install coverage
coverage run --source='src' manage.py test
coverage report
coverage html  # View in htmlcov/index.html
```

---

## Quick Reference & Cheat Sheet

### Common Django Commands

```bash
# Create migrations for model changes
uv run python manage.py makemigrations

# Apply migrations to database
uv run python manage.py migrate

# Create superuser (admin account)
uv run python manage.py createsuperuser

# Run Django shell (interactive Python with models loaded)
uv run python manage.py shell

# Clear cache
uv run python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Check project configuration
uv run python manage.py check

# Run test suite with coverage
coverage run --source='src' manage.py test && coverage report
```

### Common npm Commands

```bash
# Build Tailwind CSS (production)
npm run tailwind:build

# Watch and rebuild Tailwind CSS (development)
npm run tailwind:watch

# Start both Tailwind watcher + Django server
npm run dev

# Install dependencies
npm install
```

### uv Commands

```bash
# Sync environment from pyproject.toml + uv.lock
uv sync

# Add a new dependency
uv add package_name

# Remove a dependency
uv remove package_name

# Update all packages
uv lock --upgrade

# Run Python command with venv activated
uv run python script.py
```

---

## Frequently Asked Questions

### Q: How do I add a new IDX ticker to the watchlist?

**A:** Use the watchlist form in the UI, or programmatically:

```python
from research.models import WatchlistItem

WatchlistItem.objects.get_or_create(symbol="INCO")
```

Symbols must be valid 4-letter IDX tickers. Validation happens in `forms.py`.

---

### Q: Can I use the app without internet (offline mode)?

**A:** Sectors API calls will fail without internet. However, `sectors_api.py` includes a built-in fallback mock dataset (BBCA, BMRI, TLKM, ASII, GGRM) that activates on network errors. Useful for demo/testing.

To force mock data:

```python
# In settings.py or .env
SECTORS_API_MOCK_ONLY=True
```

---

### Q: How do I change the response language?

**A:** Language detection happens automatically in `groq_client.py::detect_language()`. Indonesian prompts → Indonesian reports. English prompts → English reports.

Override via environment variable:

```ini
GROQ_RESPONSE_LANGUAGE=id  # Force Indonesian
```

---

### Q: The Groq API is rate-limited. What should I do?

**A:** The orchestrator automatically falls back to FAST_MODEL (`gpt-oss-20b`) when rate limits are detected (429, 413, or "rate_limit" in error).

To manually tune:

1. Increase cache TTL in `settings.py` (reduce duplicate calls).
2. Reduce max symbols in a comparison (2 instead of 5).
3. Reduce date range to 30D max instead of 90D.
4. Comment out low-priority endpoints in `SYMBOL_ENDPOINTS` (e.g., remove `news`).

---

### Q: How do I deploy to production?

**A:** Two paths:

**Option 1: Linux VPS / Docker**
```bash
# Pull latest code
git pull origin main

# Sync deps
uv sync

# Build CSS
npm run build:prod

# Migrate DB
uv run python manage.py migrate

# Restart Gunicorn/uWSGI
systemctl restart sectors
```

**Option 2: Vercel (serverless)**
```bash
# Push to GitHub
git push origin main

# Vercel auto-deploys on push
# Verify at https://sectors.vercel.app
```

---

### Q: Can I export a report as PDF?

**A:** Not yet. Current exports:
- JSON (via report API endpoint)
- HTML (via browser print-to-PDF)

PDF export is a backlog item. Track in issues.

---

### Q: How do I test with a specific date range?

**A:** Construct intent manually:

```python
from research.services.orchestrator import run_analysis

# Simulated intent (normally parsed by Groq)
intent = {
    "symbols": ["BBCA"],
    "date_range": {
        "start": "2026-01-01",
        "end": "2026-09-15"
    }
}

# But to test via UI, just type:
# "Analisis BBCA dari 1 Januari hingga 15 September 2026"
```

Groq will parse date range from natural language.

---

### Q: The database is locked. How do I fix it?

**A:** SQLite locks occur when multiple processes access `database/db.sqlite3` simultaneously.

**Solution:**
```bash
# Stop the Django server
# Then delete the lock file
rm database/db.sqlite3-wal
rm database/db.sqlite3-shm

# Restart Django
npm run dev
```

For production, use PostgreSQL (no file locks).

---

## Example Prompts & Expected Outputs

### Prompt 1: Single Stock Fundamental Analysis
```
Analisis fundamental BBCA
```

**Expected Output:**
- Analysis type: `single_stock`
- Endpoints: company_report, quarterly_financials, daily_transaction, broker_summary_top, news
- Report includes: Valuation verdict (fair/undervalued/overvalued), PE/PB ratios, dividend yield, ROE, recent price trend.

---

### Prompt 2: Multi-Ticker Comparison
```
Bandingkan BBCA, BMRI, dan BBNI. Mana yang paling murah?
```

**Expected Output:**
- Analysis type: `comparison`
- 3 symbols analyzed in parallel
- Report includes: Side-by-side valuations, flow sentiment, price momentum for each.
- Verdict: Which offers best value (lowest PE/PB, highest ROE, strongest momentum).

---

### Prompt 3: Sector Screening
```
Cari saham perbankan dengan dividen yield >5%
```

**Expected Output:**
- Analysis type: `screener`
- Endpoint: screener (if available) or manual filtering.
- Report includes: List of stocks matching criteria with sorted metrics.

---

### Prompt 4: Out-of-Scope Query (Rejected)
```
Bagaimana cara membuat website dengan Django?
```

**Expected Response:**
```json
{
  "is_out_of_scope": true,
  "category": "out_of_domain",
  "message": "Pertanyaan di luar lingkup riset saham...",
  "suggestions": [
    "Analisis fundamental BBCA",
    "Bandingkan BMRI dan BBRI 30 hari",
    "Screening saham perbankan undervalue",
    "Bagaimana foreign flow TLKM minggu ini?"
  ]
}
```

---

## Metrics & Monitoring

### Key Metrics to Track

| Metric | Location | Threshold |
|---|---|---|
| Groq API latency | logs | <5s (single stock), <10s (comparison) |
| Sectors API hit rate | cache stats | >80% (avoid re-fetching same data) |
| Error rate | Django error logs | <1% |
| Database query time | Django debug toolbar | <500ms per view |
| Test coverage | coverage report | >80% |

### Log Locations

```bash
# Django logs
/var/log/sectors/django.log

# Groq API calls
grep "Groq model" /var/log/sectors/django.log

# Sectors API errors
grep "SectorsAPIError" /var/log/sectors/django.log

# Cache statistics
uv run python manage.py shell
>>> from django.core.cache import cache
>>> cache.get_many(["key1", "key2"])  # view cache stats
```

---

## Changelog & Version History

### v1.0.0 (Current)

**Features:**
- Natural language equity research via Groq + Sectors API
- Intent parsing with JSON schema validation
- Multi-endpoint parallel data fetching
- Caching layer with TTL-based expiry
- Django admin for saved reports & watchlist
- HTMX dynamic UI with Tailwind CSS
- Full test suite (14+ tests)

**Models:**
- SavedReport: Stores analysis results with citations
- WatchlistItem: User ticker watchlist

**Services:**
- groq_client: LLM inference + schema enforcement
- orchestrator: Multi-step workflow coordination
- sectors_api: Financial data wrapper
- data_distiller: Token budget optimization
- prompt_guard: Security & domain validation

### Future Roadmap (v1.1+)

- [ ] PDF/Excel export of reports
- [ ] Portfolio comparison (multiple watchlists)
- [ ] Real-time alerts (price targets, dividend announcements)
- [ ] User authentication (logins, personal reports)
- [ ] Advanced screener with custom filters
- [ ] Multi-language UI (Indonesian + English)
- [ ] Mobile app (React Native)

---

## External Resources

### Financial Data & APIs

- [Sectors Financial API](https://api.sectors.app/) — Indonesian stock data, valuations, flows.
- [Indonesia Stock Exchange (IDX)](https://www.idx.co.id/) — Official IDX homepage.
- [Yahoo Finance](https://finance.yahoo.com/) — Reference for IDX tickers.
- [Investing.com](https://www.investing.com/indices/idx.html) — Market data and charts.

### LLM & AI

- [Groq Cloud Console](https://console.groq.com/) — API key management, rate limit tracking.
- [OpenAI API Docs](https://platform.openai.com/docs/) — Reference for OpenAI-compatible APIs.
- [Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs) — JSON schema enforcement.

### Django & Python

- [Django Documentation](https://docs.djangoproject.com/en/5.1/) — Official docs for Django 5.1.
- [Pydantic Validation](https://docs.pydantic.dev/latest/) — Schema validation library.
- [Django Cache Framework](https://docs.djangoproject.com/en/5.1/topics/cache/) — Caching strategies.
- [Python asyncio](https://docs.python.org/3/library/asyncio.html) — Async/concurrent execution.

### Frontend

- [HTMX Documentation](https://htmx.org/) — Dynamic HTML interactions.
- [Tailwind CSS v4](https://tailwindcss.com/docs/v4/installation) — CSS utility framework.
- [Flowbite UI Components](https://flowbite.com/) — Pre-built Tailwind components.

### DevOps & Deployment

- [Vercel Deployment Guide](https://vercel.com/docs) — Serverless hosting for Django + Node.
- [Docker & Docker Compose](https://docs.docker.com/) — Containerization.
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) — Production database.
- [Redis Cache](https://redis.io/docs/) — High-performance caching layer.

---

## Project Metrics & Stats

**Codebase Size:**
- Python: ~1,200 LOC (src/research/)
- Templates: ~800 LOC (8 HTML files)
- CSS: ~400 LOC (Tailwind config + custom styles)
- Tests: ~350 LOC (4 test files)
- Total: ~2,750 LOC

**API Endpoints:**
- Sectors Financial API: 7 main endpoints (company, quarterly, daily, broker, foreign, news, corporate actions)
- Django Views: 9 main routes (workspace, report detail, comparison, screener, watchlist, saved reports, dashboard)
- Groq LLM: 2 schema-enforced calls (intent parser, report generator)

**Performance Targets:**
- Single stock analysis: <5s (cached endpoints) to 15s (cold calls)
- Comparison (2 symbols): <10s (cached) to 20s (cold)
- Cache hit rate: >80% on repeat queries
- Groq latency: <3s (FAST_MODEL) to <8s (PRIMARY_MODEL)

---

## License & Attribution

This project is created for Sectors Hackathon 2026 and uses:

- **Groq Cloud API** — LLM inference
- **Sectors Financial API** — Indonesian stock data
- **Django** — Web framework
- **Tailwind CSS** — Frontend styling
- **HTMX** — Dynamic interactions

See `LICENSE` file for terms.

---

## Support & Issues

### Reporting Bugs

1. Check [Issues](https://github.com/Khairil-12/Sectors-hackathon-2026/issues) for duplicates.
2. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment (OS, Python version, API status)
   - Relevant logs (sanitized of API keys)

### Requesting Features

Open a GitHub Discussion or Issue with:
- Use case / motivation
- Proposed implementation (optional)
- Priority (nice-to-have vs must-have)

### Community

- **Slack/Discord**: Join Sectors community channels for updates.
- **Email**: khairil@example.com (maintainer)

---

## Disclaimer

This software is an AI-powered research assistant designed for educational, analytical, and informational purposes. It does not provide certified financial advice, investment recommendations, or trading signals. Market data is sourced from third-party APIs and may experience latency. Always conduct independent due diligence before making investment decisions on the Indonesia Stock Exchange.
