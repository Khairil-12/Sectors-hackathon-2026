INTENT_PARSER_SCHEMA = {
    "type": "object",
    "properties": {
        "analysis_type": {
            "type": "string",
            "enum": ["single_stock", "comparison", "screener", "broker_flow", "macro_sector", "news_filings"],
        },
        "symbols": {
            "type": "array",
            "items": {"type": "string"},
        },
        "sector_slug": {"type": "string"},
        "date_range": {
            "type": "object",
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": ["start", "end"],
            "additionalProperties": False,
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
                    "screener",
                ],
            },
        },
        "user_goal_summary": {"type": "string"},
    },
    "required": ["analysis_type", "symbols", "required_endpoints", "user_goal_summary"],
    "additionalProperties": False,
}

COPILOT_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "analyzed_symbols": {"type": "array", "items": {"type": "string"}},
        "fundamental_analysis": {
            "type": "object",
            "properties": {
                "valuation_verdict": {
                    "type": "string",
                    "enum": ["undervalued", "fair", "overvalued", "inconclusive"],
                },
                "pe_pb_commentary": {"type": "string"},
                "revenue_profit_trend": {"type": "string"},
                "segment_insights": {"type": "string"},
            },
            "required": ["valuation_verdict", "pe_pb_commentary", "revenue_profit_trend"],
            "additionalProperties": False,
        },
        "flow_and_momentum": {
            "type": "object",
            "properties": {
                "foreign_flow_sentiment": {
                    "type": "string",
                    "enum": ["strong_inflow", "mild_inflow", "neutral", "outflow"],
                },
                "net_foreign_amount_idr": {"type": "number"},
                "top_broker_action": {"type": "string"},
                "price_trend_summary": {"type": "string"},
            },
            "required": ["foreign_flow_sentiment", "price_trend_summary", "top_broker_action"],
            "additionalProperties": False,
        },
        "bullish_drivers": {"type": "array", "items": {"type": "string"}},
        "bearish_risks": {"type": "array", "items": {"type": "string"}},
        "catalysts_and_news": {"type": "array", "items": {"type": "string"}},
        "data_citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_endpoint": {"type": "string"},
                    "as_of_date": {"type": "string"},
                    "key_datapoints": {"type": "string"},
                },
                "required": ["source_endpoint", "as_of_date", "key_datapoints"],
                "additionalProperties": False,
            },
        },
        "disclaimer": {"type": "string"},
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
        "disclaimer",
    ],
    "additionalProperties": False,
}