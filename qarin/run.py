"""Run Qarin profiles on a set of items and keep the answer probabilities."""
import concurrent.futures as cf
import csv
import json
import sys
from pathlib import Path

from . import FACTORS, FORMS, api
from .files import load_formats, load_items, load_profile, profile_files


def _mean(vs):
    vs = [v for v in vs if v]
    return [sum(x) / len(vs) for x in zip(*vs)] if vs else None


def _ask(state, items, formats, key, post):
    out = {}
    for c in range(0, len(items), api.PER_CALL):
        chunk = items[c:c + api.PER_CALL]
        out.update(api.probabilities(post(api.body(state, chunk, formats), key), chunk, formats))
    return out


def run_person(prof, items, formats, key, factor_scoped=False, post=api.post):
    """Each form's full profile answers every item; with factor_scoped, items that name a factor are also
    answered by that factor's scoped profile. Returns per-form probabilities and the combined answer."""
    per = {}
    for f in FORMS:
        per[f"{f}/full"] = _ask(prof[f]["full"], items, formats, key, post)
        if factor_scoped:
            for F in FACTORS:
                its = [i for i in items if i.get("factor") == F]
                if its:
                    per[f"{f}/{F}"] = _ask(prof[f]["factor"][F], its, formats, key, post)
    combined = {}
    for i in items:
        iid = i["item_id"]
        full = _mean([per[f"{f}/full"].get(iid) for f in FORMS])
        F = i.get("factor")
        if factor_scoped and F in FACTORS:
            scoped = _mean([per[f"{f}/{F}"].get(iid) for f in FORMS])
            combined[iid] = (_mean([full, scoped]), 6) if scoped else (full, 3)
        else:
            combined[iid] = (full, 3)
    return per, combined


def dry_run(profiles, items_path, formats_path=None):
    """Print the first request for the first person. Sends nothing and needs no key."""
    formats = load_formats(formats_path)
    items = load_items(items_path, formats)
    f = profile_files(profiles)[0]
    prof = load_profile(f)
    b = api.body(prof["form_B"]["full"], items[:api.PER_CALL], formats)
    first = next(iter(b["questions"].items()))
    print(json.dumps({"state": b["state"], "model": b["model"], "questions": {first[0]: first[1]}}, indent=2, ensure_ascii=False))
    n_req = -(-len(items) // api.PER_CALL)
    print(f"\n{f.stem}: {len(items)} items, {n_req} request(s) per profile, 3 profiles per person "
          f"(more with --factor-scoped). Nothing was sent.", file=sys.stderr)


def run(profiles, items_path, out_path, formats_path=None, factor_scoped=False, workers=4, post=api.post, key=None):
    formats = load_formats(formats_path)
    items = load_items(items_path, formats)
    files = profile_files(profiles)
    if not files:
        raise SystemExit(f"no profile files found at {profiles}")
    key = key if key is not None else api.get_key()
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = out.with_name(out.name + ".jsonl")
    sig = {"items": [(i["item_id"], i["text"], i["format"], i.get("factor", "")) for i in items],
           "formats": formats, "factor_scoped": factor_scoped}
    done = {}
    if ckpt.is_file():
        lines = ckpt.read_text(encoding="utf-8").splitlines()
        if lines and json.loads(lines[0]).get("sig") != json.loads(json.dumps(sig)):
            raise SystemExit(f"{ckpt} was written for different items or settings. Use a new --out, or move the file aside.")
        for line in lines[1:]:
            r = json.loads(line); done[r["qarin_id"]] = r
    else:
        ckpt.write_text(json.dumps({"sig": sig}) + "\n", encoding="utf-8")
    todo = [f for f in files if f.stem not in done]
    print(f"{len(files)} people x {len(items)} items; {len(done)} already done, {len(todo)} to run", file=sys.stderr)
    with open(ckpt, "a", encoding="utf-8") as ck, cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_person, load_profile(f), items, formats, key, factor_scoped, post): f.stem for f in todo}
        for fut in cf.as_completed(futs):
            q = futs[fut]
            per, comb = fut.result()
            rec = {"qarin_id": q, "per_profile": per, "combined": comb}
            done[q] = rec
            ck.write(json.dumps(rec) + "\n"); ck.flush()
            print(f"  {len(done)}/{len(files)} {q}", file=sys.stderr)
    K = max(len(v) for v in formats.values())
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["qarin_id", "item_id", "format", "n_options"] + [f"p{k}" for k in range(1, K + 1)] + ["expected", "n_profiles"])
        for q in sorted(done):
            for i in items:
                p, n = done[q]["combined"][i["item_id"]]
                k = len(formats[i["format"]])
                if p:
                    w.writerow([q, i["item_id"], i["format"], k] + [f"{x:.6f}" for x in p] + [""] * (K - k)
                               + [f"{sum((j + 1) * x for j, x in enumerate(p)):.4f}", n])
                else:
                    w.writerow([q, i["item_id"], i["format"], k] + [""] * K + ["", 0])
    print(f"written {out}", file=sys.stderr)
    return out
