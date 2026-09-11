import json

from django.conf import settings
from openai import APIError, APITimeoutError, OpenAI

from copilot_engine.schemas import COPILOT_REPORT_SCHEMA, INTENT_PARSER_SCHEMA


class GroqAPIError(Exception):
    pass


def _client() -> OpenAI:
    return OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL, timeout=30)


def _structured_response(name: str, schema: dict, instructions: str, input_text: str) -> dict:
    if len(input_text) > 80_000:
        raise GroqAPIError("Analysis context is too large.")
    try:
        response = _client().responses.create(
            model="openai/gpt-oss-20b",
            instructions=instructions,
            input=input_text,
            text={"format": {"type": "json_schema", "name": name, "schema": schema}},
        )
        payload = json.loads(response.output_text)
    except (APIError, APITimeoutError, ValueError, json.JSONDecodeError) as exc:
        raise GroqAPIError("AI analysis is temporarily unavailable.") from exc
    if not isinstance(payload, dict) or any(key not in payload for key in schema["required"]):
        raise GroqAPIError("AI returned an incomplete analysis.")
    return payload


def parse_user_intent(user_prompt: str) -> dict:
    return _structured_response(
        "idx_intent_parser",
        INTENT_PARSER_SCHEMA,
        "Extract IDX tickers, valid date range, analysis mode, sector slug, and required Sectors API endpoints. Return only schema data.",
        user_prompt,
    )


def generate_copilot_report(user_prompt: str, context_data: dict) -> dict:
    input_text = f"User Request: {user_prompt}\n\nIDX Context Data:\n{json.dumps(context_data, default=str)}"
    report = _structured_response(
        "idx_copilot_report",
        COPILOT_REPORT_SCHEMA,
        "Analyze only provided IDX data. Do not invent values. Include balanced risks, citations, and Indonesian disclaimer.",
        input_text,
    )
    report["disclaimer"] = "Bukan rekomendasi beli atau jual. Analisis dihasilkan otomatis berdasarkan data Sectors API untuk tujuan edukasi."
    return report
