"""Pilot statistics from the twins, and how the twins' scores relate to the people they copy."""
from pathlib import Path

import numpy as np
import pandas as pd

from .files import load_scales
from .score import draw, expected_values, keyed, load_results, scale_scores

MIRAAI = Path(__file__).resolve().parents[1] / "data" / "miraai_scores.csv"


def _alpha(V):
    V = V[~np.isnan(V).any(1)]
    k = V.shape[1]
    if k < 2 or len(V) < 3:
        return np.nan
    tot = V.sum(1).var(ddof=1)
    return float(k / (k - 1) * (1 - V.var(0, ddof=1).sum() / tot)) if tot > 0 else np.nan


def _r(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    return float(np.corrcoef(a[ok], b[ok])[0, 1]) if ok.sum() > 2 and a[ok].std() > 0 and b[ok].std() > 0 else np.nan


def analyze(results, scales_path, out_dir, draws=10, seed=20260930, human=None, how="mean"):
    """Writes item_stats.csv, scale_stats.csv, twin_scores.csv, miraai_correlations.csv and, with human
    scores, human_comparison.csv. Returns a short text summary."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    P, people, items, nopt = load_results(results)
    sc = load_scales(scales_path)
    scales = list(dict.fromkeys(s for s, _, _ in sc))
    col = {i: j for j, i in enumerate(items)}
    rng = np.random.default_rng(seed)

    # sample statistics from drawn answers, averaged over draws
    item_rows, scale_rows = {}, {}
    for _ in range(draws):
        X = keyed(draw(P, rng), items, nopt, sc)
        for s in scales:
            js = [col[i] for s2, i, _ in sc if s2 == s and i in col]
            V = X[:, js]
            tot = np.nansum(V, 1)
            srow = scale_rows.setdefault(s, {"alpha": [], "mean": [], "sd": []})
            srow["alpha"].append(_alpha(V))
            m = np.nanmean(V, 1) if how == "mean" else tot
            srow["mean"].append(np.nanmean(m)); srow["sd"].append(np.nanstd(m, ddof=1))
            for k, j in enumerate(js):
                rest = tot - V[:, k]
                d = item_rows.setdefault((s, items[j]), {"mean": [], "sd": [], "itc": []})
                d["mean"].append(np.nanmean(V[:, k])); d["sd"].append(np.nanstd(V[:, k], ddof=1))
                d["itc"].append(_r(V[:, k], rest) if len(js) > 2 else np.nan)
    key = {(s, i): k for s, i, k in sc}
    IT = pd.DataFrame([{"scale": s, "item_id": i, "key": key[(s, i)], "mean (keyed)": np.mean(v["mean"]),
                        "sd": np.mean(v["sd"]), "corrected item-total r": np.nanmean(v["itc"]) if len(v["itc"]) else np.nan}
                       for (s, i), v in item_rows.items()])
    ST = pd.DataFrame([{"scale": s, "items": sum(1 for s2, _, _ in sc if s2 == s), "alpha": np.nanmean(v["alpha"]),
                        "mean": np.mean(v["mean"]), "sd": np.mean(v["sd"])} for s, v in scale_rows.items()])
    IT.round(3).to_csv(out / "item_stats.csv", index=False)
    ST.round(3).to_csv(out / "scale_stats.csv", index=False)

    # person level: expected scores
    S = scale_scores(keyed(expected_values(P), items, nopt, sc), items, sc, how)
    S.insert(0, "qarin_id", people)
    S.round(4).to_csv(out / "twin_scores.csv", index=False)
    lines = [f"{len(people)} twins, {len(items)} items, {len(scales)} scales ({draws} drawn answer sets)."]

    if MIRAAI.is_file():
        M = pd.read_csv(MIRAAI, dtype={"qarin_id": str}).set_index("qarin_id").reindex(people)
        C = pd.DataFrame({m: [_r(S[s], M[m]) for s in scales] for m in M.columns}, index=scales)
        C.index.name = "scale"
        C.round(3).to_csv(out / "miraai_correlations.csv")
        lines.append("Correlations with the people's own Miraai factor and trait scores: miraai_correlations.csv")

    if human:
        H = pd.read_csv(human, dtype={"qarin_id": str}).set_index("qarin_id").reindex(people)
        rows = []
        for s in scales:
            if s in H.columns:
                h, t = H[s].to_numpy(float), S[s].to_numpy(float)
                ok = ~(np.isnan(h) | np.isnan(t))
                rows.append({"scale": s, "n": int(ok.sum()), "r twin with person": _r(t, h),
                             "mean twin": t[ok].mean(), "mean people": h[ok].mean(),
                             "difference in people's SD units": (t[ok].mean() - h[ok].mean()) / h[ok].std(ddof=1)})
        HC = pd.DataFrame(rows)
        HC.round(3).to_csv(out / "human_comparison.csv", index=False)
        if len(HC):
            lines.append(f"Twin score against the person's own, {len(HC)} scales: mean r {HC['r twin with person'].mean():.2f} "
                         f"(human_comparison.csv)")
    lines.append(f"Mean alpha {ST['alpha'].mean():.2f}; mean corrected item-total r {IT['corrected item-total r'].mean():.2f}.")
    (out / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(lines)
