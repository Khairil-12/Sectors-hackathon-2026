from django import forms


class PromptForm(forms.Form):
    prompt = forms.CharField(
        label="Ask IDX Copilot",
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Contoh: Bandingkan BBCA dan BMRI untuk 30 hari terakhir.",
                "class": "w-full rounded-lg border border-slate-700 bg-surface-950 px-4 py-3 text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none",
            }
        ),
    )

    def clean_prompt(self):
        prompt = self.cleaned_data["prompt"].strip()
        if len(prompt) < 3:
            raise forms.ValidationError("Pertanyaan minimal tiga karakter.")
        return prompt
