# Sectors-hackathon-2026: AI IDX Investment Research Copilot

A Django-based conversational equity research platform for the Indonesia Stock Exchange (IDX) powered by Groq Cloud and Sectors Financial API.

## Requirements
- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js (for Tailwind CSS builds)

## Setup

1. **Clone repository and copy environment file:**
   ```powershell
   copy .env.template .env
   ```
   Configure `GROQ_API_KEY`, `SECTORS_API_KEY`, and `DJANGO_SECRET_KEY` in `.env`.

2. **Install Python dependencies with UV:**
   ```powershell
   uv sync
   ```

3. **Install frontend dependencies and build CSS:**
   ```powershell
   npm install
   npm run build
   ```

4. **Apply database migrations:**
   ```powershell
   uv run python manage.py migrate
   ```

5. **Run test suite:**
   ```powershell
   uv run python manage.py test
   ```

6. **Start local development servers:**
   ```powershell
   # Terminal 1: Watch Tailwind changes
   npm run dev

   # Terminal 2: Run Django
   uv run python manage.py runserver
   ```
