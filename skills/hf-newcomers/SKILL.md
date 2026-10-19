---
name: hf-newcomers
description: Use when the user asks which new AI models or demos are taking off on Hugging Face, what entered HF trending since last time, or wants early names of new models to watch.
---

# hf-newcomers

Reports models and Spaces that entered Hugging Face's trending top 50 since the previous run.
Copies of one model (GGUF, AWQ, 27B, Instruct...) are grouped under the base name, and a model
and its demo Space become one lead. Public API, no key.

## Run
```bash
python hf_newcomers.py                  # first run saves a snapshot; later runs list newcomers
python hf_newcomers.py --json           # same, as JSON
python hf_newcomers.py --state DIR      # where snapshots live (default .hf-newcomers)
python hf_newcomers.py --demo           # offline example, no network
```

## Read the result
Each line: `term  [Hugging Face: new at #rank, N versions]  repo id (task or sdk, likes)`.
A first run prints only "first run: saved ..."; run it again hours later (e.g. every 8 hours).
Tell the user the rank and the examples; do not claim a model is popular beyond its trending rank.
