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
| `npm run tailwind:watch` | Watch `./static/src/input.css` and recompile to `./static/dist/app.css`. |
| `npm run tailwind:build` | Minify and compile production CSS bundle. |
| `npm run django:run` | Start Django server through npm script runner. |

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

## Disclaimer

This software is an AI-powered research assistant designed for educational, analytical, and informational purposes. It does not provide certified financial advice, investment recommendations, or trading signals. Market data is sourced from third-party APIs and may experience latency. Always conduct independent due diligence before making investment decisions on the Indonesia Stock Exchange.
