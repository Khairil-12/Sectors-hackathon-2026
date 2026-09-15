from __future__ import annotations

import re
from django import forms

SYMBOL_RE = re.compile(r"^[A-Z]{4}$")


class PromptForm(forms.Form):
    prompt = forms.CharField(
        label="Ask IDX Copilot",
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Contoh: Bandingkan BBCA dan BMRI untuk 30 hari terakhir...",
                "class": "w-full rounded-lg border border-slate-700 bg-surface-950 px-4 py-3 text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none transition-colors",
            }
        ),
    )

    def clean_prompt(self):
        prompt = self.cleaned_data["prompt"].strip()
        if len(prompt) < 3:
            raise forms.ValidationError("Pertanyaan minimal tiga karakter.")
        return prompt


class WatchlistAddForm(forms.Form):
    symbol = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. BBCA, TLKM",
                "class": "uppercase rounded-md border border-slate-700 bg-surface-950 px-3 py-2 text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none",
            }
        ),
    )

    def clean_symbol(self):
        symbol = self.cleaned_data["symbol"].strip().upper().removesuffix(".JK")
        if not SYMBOL_RE.fullmatch(symbol):
            raise forms.ValidationError("Symbol must be a valid 4-letter IDX ticker.")
        return symbol


class ScreenerSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. profitable banking companies with high dividend yield",
                "class": "min-w-0 flex-1 rounded-md border border-slate-700 bg-surface-950 px-4 py-3 text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none",
            }
        ),
    )
    preset = forms.CharField(required=False)
