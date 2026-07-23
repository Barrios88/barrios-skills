---
name: financial-text-nlp
description: Measure sentiment and stance in financial and economic text — 10-K/10-Q MD&A, earnings calls, Fed/ECB communications — using FinBERT, FinVADER, and domain models. Use for accounting and finance NLP features, not general chat sentiment.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Financial & economic text NLP

## When to use

- Tone of MD&A, risk factors, 8-K text, or ESG/boilerplate sections
- Earnings-call transcripts (prepare/Q&A separately when possible)
- Central-bank or supervisory communications (hawkish/dovish stance)
- Building panel covariates (firm–year sentiment) for regressions in [`pyfixest`](../../econometrics/pyfixest/) or Stata

**Not for:** casual product reviews or generic Twitter sentiment without a finance lexicon/model.

## Tool map

| Task | Tool | Notes |
|------|------|-------|
| General financial tone | [FinBERT](https://huggingface.co/ProsusAI/finbert) (ProsusAI) | Sentence/chunk classification: positive/negative/neutral |
| Lexicon baseline | [FinVADER](https://github.com/PetrKorab/FinVADER) | Fast, transparent; good robustness check |
| Central-bank stance | [CentralBankRoBERTa](https://github.com/Moritz-Pfeifer/CentralBankRoBERTa), [WorldCentralBanks](https://github.com/gtfintechlab/WorldCentralBanks) | Domain labels ≠ FinBERT polarity |
| Econ NER / domain LM | [EconBERTa](https://github.com/worldbank/econberta-econie) | Entity/paper domain — not a drop-in sentiment score |
| Document → text | [`sec-edgar`](../sec-edgar/), markitdown/Docling | Get clean text before scoring |

## Iron law: define the unit and the label

1. **Unit of analysis:** sentence, paragraph, section, or full document (document scores need aggregation rules)
2. **Label meaning:** polarity ≠ hawkishness ≠ forward-looking statements
3. **Train/test hygiene:** do not tune thresholds on the same sample used for causal estimates
4. **Inspect:** print 10 scored excerpts before merging to Compustat

## Minimal FinBERT pattern

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_id = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)

def score_texts(texts: list[str], max_length: int = 256):
    inputs = tokenizer(
        texts, padding=True, truncation=True, max_length=max_length, return_tensors="pt"
    )
    with torch.no_grad():
        probs = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)
    # labels: positive, negative, neutral (confirm order via model.config.id2label)
    return probs
```

Aggregate to firm–year with an explicit rule (mean of sentence scores; or net positivity = pos − neg). Document the rule in the paper.

## Accounting / finance research notes

- **Boilerplate:** length and legalese dilute tone — consider section fixed effects or residuals
- **Attribution:** link scores to accession IDs / transcript IDs for replication
- **Identification:** sentiment as outcome vs covariate vs instrument — state which; NLP error is measurement error
- **Robustness:** report FinBERT + lexicon (FinVADER) or alternative chunking

## Checklist

- [ ] Text source and cleaning steps logged
- [ ] Model id + revision pinned
- [ ] Aggregation rule written down
- [ ] Hand-checked excerpts saved
- [ ] Merge keys to firm identifiers validated (CIK / gvkey / ticker map)
