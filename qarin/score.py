"""Scale scores and drawn answers from the twins' answer probabilities."""
import numpy as np
import pandas as pd

from .files import load_scales


def load_results(path):
    """Long run output -> (P: people x items x K array, people, items, n_options per item)."""
    t = pd.read_csv(path, dtype={"qarin_id": str, "item_id": str})
    people = sorted(t.qarin_id.unique())
    items = list(dict.fromkeys(t.item_id))
    K = int(t.n_options.max())
    P = np.full((len(people), len(items), K), np.nan)
    pi = t.qarin_id.map({p: k for k, p in enumerate(people)}).to_numpy()
    ii = t.item_id.map({p: k for k, p in enumerate(items)}).to_numpy()
    P[pi, ii] = t[[f"p{k}" for k in range(1, K + 1)]].to_numpy(float)
    nopt = t.drop_duplicates("item_id").set_index("item_id").n_options.reindex(items).to_numpy(int)
    return P, people, items, nopt


def keyed(X, items, nopt, scales):
    """Reverse-key item values (1..K) for the items keyed -1 on any scale they belong to."""
    key = {}
    for s, i, k in scales:
        key.setdefault(i, k)
    X = X.copy()
    for j, i in enumerate(items):
        if key.get(i, 1) == -1:
            X[:, j] = (nopt[j] + 1) - X[:, j]
    return X


def scale_scores(X, items, scales, how="mean"):
    """X: people x items (keyed item values). One column per scale: mean (or sum) of its items."""
    col = {i: j for j, i in enumerate(items)}
    out = {}
    for s in dict.fromkeys(sc for sc, _, _ in scales):
        js = [col[i] for sc, i, _ in scales if sc == s and i in col]
        v = X[:, js]
        out[s] = np.nanmean(v, 1) if how == "mean" else np.nansum(v, 1)
    return pd.DataFrame(out)


def expected_values(P):
    K = P.shape[-1]
    return np.nansum(P * np.arange(1, K + 1), -1) / np.where(np.nansum(P, -1) > 0, np.nansum(P, -1), np.nan)


def draw(P, rng):
    """One sampled answer (1..K) per person and item from the probabilities."""
    Q = np.nan_to_num(P)
    c = np.cumsum(Q, -1)
    u = rng.random(P.shape[:2]) * c[..., -1]
    X = (u[..., None] > c).sum(-1) + 1.0
    X[np.isnan(P).all(-1)] = np.nan
    return X


def score(results, scales_path, how="mean"):
    """Twin scale scores from the expected answers (exact, since keying and averaging are linear)."""
    P, people, items, nopt = load_results(results)
    sc = load_scales(scales_path)
    X = keyed(expected_values(P), items, nopt, sc)
    S = scale_scores(X, items, sc, how)
    S.insert(0, "qarin_id", people)
    return S
