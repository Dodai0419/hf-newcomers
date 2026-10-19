import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import hf_newcomers as hf  # noqa: E402

GOLDEN = ROOT / "tests" / "golden"


def two_runs(case):
    """First run builds the snapshot, the second reports newcomers (as upstream does)."""
    data = json.loads((GOLDEN / f"{case}_in.json").read_text(encoding="utf-8"))
    state = Path(tempfile.mkdtemp())
    hf.newcomers(state, fetch=lambda what: data["before"][what])
    return hf.newcomers(state, fetch=lambda what: data["after"][what])


class SameOutputAsUpstream(unittest.TestCase):
    """Golden files were written by zhuyansen/new-term-radar radar.sources.hf_new on the same lists."""

    def test_demo_lists(self):
        self.assertEqual(two_runs("demo"), json.loads((GOLDEN / "demo_out.json").read_text(encoding="utf-8")))

    def test_real_trending_lists(self):
        self.assertEqual(two_runs("live"), json.loads((GOLDEN / "live_out.json").read_text(encoding="utf-8")))

    def test_first_run_reports_nothing(self):
        res = hf.newcomers(Path(tempfile.mkdtemp()), fetch=lambda what: [{"id": "a/B-1"}])
        self.assertEqual(res, {"first_run": True, "terms": [], "models": 1, "spaces": 1})


class BaseName(unittest.TestCase):
    def test_strips_quantisation_and_size(self):
        self.assertEqual(hf.base_name("abenzerps/Qwen-Image-2.1-Uncensored-GGUF"), "qwen image 2.1")
        self.assertEqual(hf.base_name("Qwen/Qwen3.8-Flash-Next-A6B-Instruct"), "qwen3.8 flash next")
        self.assertEqual(hf.base_name("Lightricks/LTX-2.5"), "ltx 2.5")


class Concurrency(unittest.TestCase):
    def test_models_and_spaces_are_fetched_in_parallel(self):
        def slow(what):
            time.sleep(0.3)
            return [{"id": f"x/{what}-{threading.get_ident()}"}]
        t = time.perf_counter()
        hf.newcomers(Path(tempfile.mkdtemp()), fetch=slow)
        self.assertLess(time.perf_counter() - t, 0.5)


class Cli(unittest.TestCase):
    def test_demo_prints_newcomers(self):
        out = subprocess.run([sys.executable, str(ROOT / "hf_newcomers.py"), "--demo"],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("krea 2", out.stdout)
        self.assertIn("Hugging Face Spaces: new at #2", out.stdout)


if __name__ == "__main__":
    unittest.main()
