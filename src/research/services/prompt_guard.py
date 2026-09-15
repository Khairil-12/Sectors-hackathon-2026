from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Curated non-ticker stopwords that resemble 4-letter words
COMMON_4_LETTER_STOPWORDS = {
    # Indonesian stopwords
    "YANG", "PADA", "DARI", "UNTU", "AKAN", "BISA", "KITA", "KAMI", "KAMU", "SAYA",
    "ANDA", "MERE", "SAAT", "JIKA", "MAKA", "HARI", "SETA", "JUGA", "LAGI", "DULU",
    "TIDK", "TIDAK", "BUAT", "OLEH", "BAGI", "AGAR", "TENT", "KINI", "SINI", "SITU",
    "SANA", "MANA", "KATA", "BACA", "TULI", "TAHU", "BEDA", "SAMA", "LALU", "KEMU",
    "LAMA", "BARU", "BAIK", "JELE", "NAIK", "TURU", "CEK", "LIHA", "CARI", "APAK",
    "BAGA", "SIAP", "SUDA", "BELU", "PERN", "DEPA", "BELA", "ATAS", "BAWA", "KIRI",
    "KANA", "TENH", "LUAR", "DALA",
    # English stopwords
    "WHAT", "WHEN", "WITH", "THAT", "THIS", "FROM", "HAVE", "SOME", "MORE", "MOST",
    "WANT", "LIKE", "LOOK", "FIND", "VIEW", "SHOW", "MAKE", "HELP", "CODE", "TEST",
    "USER", "TASK", "TYPE", "POST", "HTTP", "JSON", "DATA", "INFO", "FREE", "GOOD",
    "KNOW", "TELL", "CHAT", "BOTS", "AUTO", "PLAY", "WILL", "YOUR", "NAME", "JUST",
}

# Financial and IDX domain keywords (Indonesian and English)
FINANCIAL_KEYWORDS = {
    "saham", "stock", "stocks", "emiten", "ticker", "tickers", "dividen", "dividend",
    "dividends", "laba", "profit", "net income", "revenue", "pendapatan", "omzet",
    "kinerja", "valuasi", "valuation", "pe", "per", "pbv", "pb", "ps", "roe", "roa",
    "der", "ebitda", "ihsg", "idx", "bei", "bursa", "pasar modal", "capital market",
    "broker", "foreign flow", "inflow", "outflow", "net foreign", "bandar", "bandarmology",
    "sektor", "sector", "sectors", "industri", "industry", "screening", "screener",
    "undervalue", "undervalued", "overvalue", "overvalued", "analisis", "analysis",
    "fundamental", "teknikal", "laporan keuangan", "financial statement", "quarterly",
    "kuartal", "market cap", "kapitalisasi", "top gainer", "top gainers", "top loser",
    "top losers", "net buy", "net sell", "akumulasi", "distribusi", "ipo", "buyback",
    "rups", "rights issue", "obligasi", "bond", "yield", "yields", "investasi", "invest",
    "investor", "trading", "trader", "portofolio", "portfolio", "cash flow", "arus kas",
    "neraca", "balance sheet", "utang", "debt", "aset", "asset", "assets", "turnover",
    "transaksi", "volume", "lot", "fraksi", "closing", "penutupan", "harga", "price",
    "bandingkan", "compare", "vs", "versus", "grafik", "chart",
}

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"system\s+prompt",
    r"you\s+are\s+now\s+in\s+dan\s+mode",
    r"jailbreak",
    r"bypass\s+(safety|filter|guard)",
    r"reveal\s+(the\s+)?prompt",
    r"act\s+as\s+an?\s+unrestricted",
]

NON_FINANCIAL_PATTERNS = [
    r"\b(python|javascript|typescript|golang|java|c\+\+|html|css|php|rust|ruby)\b",
    r"\b(programming|coding|algorithm|regex|sql\s+query|git\s+commit|software|framework)\b",
    r"\b(resep|masakan|makanan|minuman|kuliner|baking|membuat\s+website)\b",
    r"\b(cuaca|prakiraan\s+cuaca|hujan|suhu|derajat)\b",
    r"\b(cerita\s+lucu|lelucon|joke|jokes|standup|humor)\b",
    r"\b(siapa\s+presiden|menteri|pemilu|pilpres|pilkada)\b",
    r"\b(lirik\s+lagu|chord\s+gitar|film|sinopsis|anime|game|gaming)\b",
]

DEFAULT_SUGGESTIONS = [
    "Analisis fundamental BBCA",
    "Bandingkan BMRI dan BBRI 30 hari",
    "Screening saham perbankan undervalue",
    "Bagaimana foreign flow TLKM minggu ini?",
]


@dataclass
class GuardResult:
    is_allowed: bool
    category: str = "valid"
    reason: str = ""
    suggested_prompts: list[str] = field(default_factory=lambda: list(DEFAULT_SUGGESTIONS))

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_out_of_scope": not self.is_allowed,
            "category": self.category,
            "message": self.reason,
            "suggestions": self.suggested_prompts,
        }


def extract_potential_tickers(text: str) -> list[str]:
    """Extracts uppercase 4-letter tokens that are potential IDX stock tickers."""
    # Look for explicit uppercase 4-letter words in the original prompt
    candidates = re.findall(r"\b[A-Z]{4}\b", text)
    return [c for c in candidates if c not in COMMON_4_LETTER_STOPWORDS]


def has_financial_context(text: str) -> bool:
    """Checks if the text contains any Indonesian or English financial terms."""
    lower = text.lower()
    return any(re.search(rf"\b{re.escape(kw)}\b", lower) for kw in FINANCIAL_KEYWORDS)


def validate_prompt(user_prompt: str) -> GuardResult:
    """Evaluates whether a user prompt is safe, valid, and within the IDX financial domain."""
    cleaned = user_prompt.strip()

    if len(cleaned) < 3:
        return GuardResult(
            is_allowed=False,
            category="too_short",
            reason="Pertanyaan terlalu pendek. Masukkan kode saham atau topik analisis pasar modal IDX yang ingin Anda teliti.",
        )

    # 1. Prompt Injection / Security Guard
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return GuardResult(
                is_allowed=False,
                category="security_risk",
                reason="Instruksi tidak dapat diproses karena melanggar batasan keamanan sistem.",
            )

    has_finance = has_financial_context(cleaned)
    tickers = extract_potential_tickers(cleaned)

    # 2. Explicit Non-Financial Pattern Detection (e.g. programming, weather, cooking, etc.)
    for pattern in NON_FINANCIAL_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE) and not has_finance:
            return GuardResult(
                is_allowed=False,
                category="out_of_domain",
                reason=(
                    "Pertanyaan di luar lingkup riset saham dan pasar modal IDX. "
                    "AI Copilot ini dirancang khusus untuk menganalisis emiten, valuasi, kinerja keuangan, "
                    "dan pergerakan dana institusi/asing di Bursa Efek Indonesia."
                ),
            )

    # 3. Allow if explicit financial context or recognized uppercase tickers exist
    if tickers or has_finance:
        return GuardResult(is_allowed=True, category="valid")

    # 4. General chit-chat or ambiguous query without financial context
    return GuardResult(
        is_allowed=False,
        category="out_of_domain",
        reason=(
            "Tidak ditemukan emiten atau topik keuangan IDX dalam pertanyaan Anda. "
            "Silakan tanyakan seputar emiten saham (contoh: 'Analisis fundamental BBCA', 'Bandingkan BMRI dan BBRI', 'Screening saham dividen'), atau pergerakan sektor."
        ),
    )
