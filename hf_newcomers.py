#!/usr/bin/env python3
"""Models and Spaces that entered Hugging Face's trending top 50 since your last run.

The Hugging Face signal of zhuyansen/new-term-radar as one stdlib file: both lists are
fetched in parallel, quantised / fine-tuned copies are grouped under their base name,
and a model and its demo Space become one lead.

  python hf_newcomers.py                 # live; the first run only saves a snapshot
  python hf_newcomers.py --json          # machine-readable
  python hf_newcomers.py --demo          # offline example from tests/golden
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HF_TOP, HF_FETCH, TOP = 50, 100, 25   # entering the top 50 against the last run's top 100
UA = "hf-newcomers/0.1 (+https://github.com/Dodai0419/hf-newcomers)"
# Words too common in AI repo names to be a lead on their own (new-term-radar's stop list).
STOP = set("""
a an and are as at be by can for from has have in into is it its of on or that the this to with your you
using use used via based built make makes made new open source opensource simple fast free first best
ai agent agents agentic llm llms mcp server servers skill skills tool tools toolkit plugin plugins claude code
codex cursor gpt openai anthropic model models app apps api cli sdk framework library project repo repository
github python typescript javascript node rust go web based local self hosted hosted powered support supports
your all any more most one two three get set run runs build builder generate generator help helper helps
assistant assistants chat bot bots automation automate automated workflow workflows system systems data
md readme docs example examples demo test tests template templates collection awesome list curated
""".split())
SPACE_NOISE = {"demo", "webgpu", "studio", "space", "spaces", "playground", "gradio", "app", "online", "zerogpu", "gpu", "chat"}
_NOISE = re.compile(r"[-_.](gguf|ggml|awq|gptq|fp8|fp16|bf16|int[48]|mlx|exl2|onnx|uncensored|abliterated|"
                    r"instruct|chat|it|base|preview|turbo|lora|q\d\w*|\d+(\.\d+)?b|a\d+(\.\d+)?b)(?=[-_.]|$)", re.I)


def base_name(model_id: str) -> str:
    """'abenzerps/Qwen-Image-2.1-Uncensored-GGUF' -> 'qwen image 2.1'."""
    name = model_id.split("/")[-1]
    for _ in range(4):   # suffixes stack: -27B-Instruct-GGUF
        name = _NOISE.sub("", name)
    return re.sub(r"[-_]+", " ", name).strip().lower()


def trending(what: str) -> list[dict]:
    req = urllib.request.Request(f"https://huggingface.co/api/{what}?sort=trendingScore&direction=-1&limit={HF_FETCH}",
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as res:
        return json.load(res)


def entered(items: list[dict], before: list[str], what: str) -> list[dict]:
    """Items new in the top HF_TOP since the last snapshot, grouped by base name, best rank first."""
    seen, grouped = set(before), {}
    for rank, m in enumerate(items[:HF_TOP], 1):
        if m["id"] in seen:
            continue
        term = base_name(m["id"])
        if what == "spaces":   # 'lightonocr 3 demo' -> 'lightonocr 3'
            term = " ".join(w for w in term.split() if w not in SPACE_NOISE)
        if not term or term in STOP:
            continue
        g = grouped.setdefault(term, {"term": term, "rank": rank, "copies": 0, "examples": []})
        g["copies"] += 1
        g["examples"].append(f"{m['id']} ({m.get('pipeline_tag') or m.get('sdk') or '?'}, ♥{m.get('likes', 0)})")
    rows = sorted(grouped.values(), key=lambda g: g["rank"])
    for g in rows:
        g["recent"] = g["copies"]
        g["note"] = f"Hugging Face{'' if what == 'models' else ' Spaces'}: new at #{g['rank']}" + \
            (f", {g['copies']} versions" if g["copies"] > 1 else "")
    return rows


def newcomers(state: Path, fetch=trending) -> dict:
    with ThreadPoolExecutor(2) as pool:   # the two requests are independent: wait for the slower, not the sum
        lists = dict(zip(("models", "spaces"), pool.map(fetch, ("models", "spaces"))))
    out = {"first_run": False, "terms": []}
    for what in ("models", "spaces"):
        items, path = lists[what], state / f"hf_{what}_top.json.gz"
        before = json.loads(gzip.decompress(path.read_bytes())) if path.exists() else None
        if items:   # a failed or empty fetch keeps the last snapshot
            state.mkdir(parents=True, exist_ok=True)
            path.write_bytes(gzip.compress(json.dumps([m["id"] for m in items]).encode()))
        out[what] = len(items)
        if before is None:
            out["first_run"] = True
            continue
        have = {r["term"]: r for r in out["terms"]}
        for r in entered(items, before, what):
            if r["term"] in have:   # a model and its demo both new: one lead, both examples
                have[r["term"]]["examples"] += r["examples"]
            else:
                out["terms"].append(r)
    out["terms"] = out["terms"][:TOP]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default=".hf-newcomers", help="snapshot directory (default: .hf-newcomers)")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    ap.add_argument("--demo", action="store_true", help="offline run on tests/golden/demo_in.json")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")   # model names and ♥ survive Windows code pages
    if a.demo:
        data = json.loads((Path(__file__).parent / "tests/golden/demo_in.json").read_text(encoding="utf-8"))
        state = Path(tempfile.mkdtemp())
        newcomers(state, fetch=lambda w: data["before"][w])
        res = newcomers(state, fetch=lambda w: data["after"][w])
    else:
        res = newcomers(Path(a.state))
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    elif res["first_run"]:
        print(f"first run: saved the top {res['models']} models and {res['spaces']} Spaces. Run again later to see newcomers.")
    else:
        print(f"{len(res['terms'])} newcomers ({res['models']} models, {res['spaces']} Spaces checked)")
        for r in res["terms"]:
            print(f"- {r['term']}  [{r['note']}]  {'; '.join(r['examples'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
