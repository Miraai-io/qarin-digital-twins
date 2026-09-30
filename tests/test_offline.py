"""Offline test: runs the whole pipeline on the demo study with a stand-in for the answering model.

    python tests/test_offline.py

No key and no network. It checks that the files are read, the requests are built, the answers are combined
over the three forms, and scoring and analysis produce their outputs. The numbers it prints are not twin
results: the stand-in answers at random.
"""
import json
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qarin import FACTORS, FORMS                     # noqa: E402
from qarin.analyze import analyze                    # noqa: E402
from qarin.files import check                        # noqa: E402
from qarin.run import run                            # noqa: E402
from qarin.score import score                        # noqa: E402

DEMO = ROOT / "examples" / "demo"
calls = []


def fake_post(payload, key):
    calls.append(payload)
    rnd = random.Random(hash(payload["state"]) % 10**6)
    ans = {}
    for iid, q in payload["questions"].items():
        K = len(q["criteria"])
        w = [rnd.random() + (2 if k == rnd.randrange(K) else 0) for k in range(K)]
        ans[iid] = {"probabilities": {str(k): w[k] / sum(w) for k in range(K)}}
    return {"answers": ans}


def main():
    errors, warnings = check(DEMO / "items.csv", DEMO / "scales.csv", DEMO / "formats.csv")
    assert not errors, errors
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); prof = tmp / "profiles"; prof.mkdir()
        for n in range(1, 13):
            d = {"qarin_id": f"Q{n:03d}", "biodata": "You are between 35 and 49."}
            for f in FORMS:
                d[f] = {"full": f"profile {n} {f} full", "factor": {F: f"profile {n} {f} {F}" for F in FACTORS}}
            (prof / f"Q{n:03d}.json").write_text(json.dumps(d), encoding="utf-8")
        out = tmp / "results.csv"
        run(prof, DEMO / "items.csv", out, DEMO / "formats.csv", factor_scoped=True, workers=2, post=fake_post, key="test")
        assert len(calls) == 12 * 3 * (1 + 2), len(calls)          # full + Co + Ex scoped profiles, per form
        S = score(out, DEMO / "scales.csv")
        assert list(S.columns) == ["qarin_id", "Planning", "Social Ease", "Checking"] and len(S) == 12
        assert S.drop(columns="qarin_id").stack().between(1, 5).all()
        human = tmp / "human.csv"
        human.write_text("qarin_id,Planning\n" + "".join(f"Q{n:03d},{random.uniform(1, 5):.2f}\n" for n in range(1, 13)), encoding="utf-8")
        print(analyze(out, DEMO / "scales.csv", tmp / "analysis", draws=3, human=human))
        assert (tmp / "analysis" / "human_comparison.csv").is_file()
        for f in ("item_stats.csv", "scale_stats.csv", "twin_scores.csv", "summary.txt"):
            assert (tmp / "analysis" / f).is_file(), f
        run(prof, DEMO / "items.csv", out, DEMO / "formats.csv", factor_scoped=True, workers=2, post=fake_post, key="test")
        assert len(calls) == 36 * 3, "a second run should resume and send nothing"
    print("offline test passed")


if __name__ == "__main__":
    main()
