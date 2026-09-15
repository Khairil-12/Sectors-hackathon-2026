import json
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

import django
django.setup()

from django.test import TestCase

from research.schemas import COPILOT_REPORT_SCHEMA, INTENT_PARSER_SCHEMA


class LanguageDetectionTest(TestCase):
    def test_detect_indonesian(self):
        from research.services.groq_client import detect_language
        result = detect_language("Analisis BBCA fundamentals")
        self.assertEqual(result, "id")

    def test_detect_english(self):
        from research.services.groq_client import detect_language
        result = detect_language("Analyze BBCA fundamentals")
        self.assertEqual(result, "en")

    def test_language_instruction(self):
        from research.services.groq_client import language_instruction
        self.assertIn("Indonesian", language_instruction("id"))
        self.assertIn("English", language_instruction("en"))


class IntentSchemaTest(TestCase):
    def test_intent_schema_has_required_fields(self):
        self.assertIn("analysis_type", INTENT_PARSER_SCHEMA["properties"])
        self.assertIn("symbols", INTENT_PARSER_SCHEMA["properties"])
        self.assertIn("required_endpoints", INTENT_PARSER_SCHEMA["properties"])
        self.assertIn("user_goal_summary", INTENT_PARSER_SCHEMA["properties"])
        self.assertIn("response_language", INTENT_PARSER_SCHEMA["properties"])

    def test_intent_schema_analysis_type_enum(self):
        analysis_types = INTENT_PARSER_SCHEMA["properties"]["analysis_type"]["enum"]
        self.assertIn("single_stock", analysis_types)
        self.assertIn("comparison", analysis_types)
        self.assertIn("screener", analysis_types)

    def test_intent_schema_valid_json(self):
        json_str = json.dumps(INTENT_PARSER_SCHEMA)
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["type"], "object")

    def test_intent_schema_response_language_enum(self):
        langs = INTENT_PARSER_SCHEMA["properties"]["response_language"]["enum"]
        self.assertIn("id", langs)
        self.assertIn("en", langs)


class ReportSchemaTest(TestCase):
    def test_report_schema_has_required_fields(self):
        self.assertIn("title", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("summary", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("analyzed_symbols", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("fundamental_analysis", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("flow_and_momentum", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("bullish_drivers", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("bearish_risks", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("data_citations", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("disclaimer", COPILOT_REPORT_SCHEMA["properties"])
        self.assertIn("response_language", COPILOT_REPORT_SCHEMA["properties"])

    def test_report_schema_valuation_verdict_enum(self):
        verdicts = COPILOT_REPORT_SCHEMA["properties"]["fundamental_analysis"]["properties"]["valuation_verdict"]["enum"]
        self.assertIn("undervalued", verdicts)
        self.assertIn("fair", verdicts)
        self.assertIn("overvalued", verdicts)
        self.assertIn("inconclusive", verdicts)