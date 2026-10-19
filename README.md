<div align="center">

# hf-newcomers

**List the Hugging Face models and Spaces that just entered trending, grouped by base name.**

The Hugging Face signal of [new-term-radar](https://github.com/zhuyansen/new-term-radar) pulled out into one 129-line stdlib file: same leads on the same data, a third less wait.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg) ![Status: prototype](https://img.shields.io/badge/status-prototype-orange.svg)

Works with **Claude Code** and **Codex**.

</div>

## Quick start
```bash
git clone https://github.com/Dodai0419/hf-newcomers && cd hf-newcomers
python hf_newcomers.py --demo      # offline example; drop --demo for live data
```
```text
2 newcomers (2 models, 2 Spaces checked)
- krea 2  [Hugging Face: new at #1]  krea/Krea-2 (text-to-image, ♥900); krea/Krea-2-demo (gradio, ♥300)
- lightonocr 3  [Hugging Face Spaces: new at #2]  lighton/LightOnOCR-3-webgpu (static, ♥0)
```
Live: the first run saves a snapshot of the top 100; every later run lists what entered the top 50 since then.

## The problem
- HF trending is full of copies: one release shows up as `-GGUF`, `-AWQ`, `-27B-Instruct`, and a `-demo` Space.
- In new-term-radar this signal lives inside a 3,525-line package with X, Google Trends, mail and SQLite parts you may not need.
- It fetches the model list and the Space list one after the other, so you wait for both round trips.

## The solution
| Idea | Fixes |
|------|-------|
| **Base-name grouping** (`Qwen-Image-2.1-Uncensored-GGUF` -> `qwen image 2.1`) | five copies of one model become one lead |
| **Model + demo merge** | a model and its Space are reported once, with both links |
| **Parallel fetch** of models and Spaces | wait for the slower request, not the sum |
| **One file, stdlib only, gzip snapshot** | copy it anywhere, run it from cron |

## Use with Claude Code
```bash
/plugin marketplace add Dodai0419/hf-newcomers
/plugin install hf-newcomers@hf-newcomers
```

## Use with Codex (ChatGPT)
```bash
git clone https://github.com/Dodai0419/hf-newcomers && cp -r hf-newcomers/skills/* ~/.codex/skills/
```
Or copy `AGENTS.md` into your project root.

## Benchmarks
Live Hugging Face API, 7 interleaved runs of each in one process (`radar.sources.hf_new({}, state)` vs `hf_newcomers.newcomers(state)`), Windows 11, Python 3.11.1, home connection.

| | new-term-radar (HF signal) | this repo |
|-|-|-|
| fetch + diff, median of 7 | 763 ms | 504 ms |
| lines of code to run it | 3,525 (`radar/` package) | 129 |
| dependencies | stdlib | stdlib |

Same output: `tests/golden/*_out.json` were written by new-term-radar's `hf_new` on the same lists (a demo case and a real trending snapshot with 22 newcomers); the tests require equal results. Network latency varies, so expect your numbers to move.

## Inspired by
- [zhuyansen/new-term-radar](https://github.com/zhuyansen/new-term-radar) - the Hugging Face signal, base-name rules and stop words (MIT).

## Roadmap
- [ ] Optional `--top N` to watch a deeper slice of trending
- [ ] Datasets list as a third source

## License
MIT
