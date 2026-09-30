"""Reading and checking the study files: items, formats, scales, profiles."""
import csv
import json
from pathlib import Path

from . import FACTORS, FORMS

DEFAULT_FORMATS = {"agree5": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]}


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh)]


def load_formats(path=None):
    """format_id -> list of options, low to high. agree5 is always available."""
    fm = dict(DEFAULT_FORMATS)
    if path:
        for r in read_csv(path):
            opts = [o.strip() for o in r.get("options", "").split("|") if o.strip()]
            fm[r["format_id"]] = opts
    return fm


def load_items(path, formats):
    rows = read_csv(path)
    for r in rows:
        r["format"] = r.get("format") or "agree5"
        r["factor"] = r.get("factor", "")
    return rows


def load_scales(path):
    """[(scale, item_id, key)] with key +1 or -1."""
    out = []
    for r in read_csv(path):
        k = r.get("key", "1") or "1"
        out.append((r["scale"], r["item_id"], -1 if k.strip() in ("-1", "R", "r", "reverse") else 1))
    return out


def profile_files(path):
    p = Path(path)
    return sorted(p.glob("Q*.json")) if p.is_dir() else [p]


def load_profile(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    for f in FORMS:
        if f not in d or "full" not in d[f]:
            raise SystemExit(f"{path}: not a Qarin profile file (missing {f})")
    return d


def check(items_path, scales_path=None, formats_path=None):
    """Return (errors, warnings) for a study's files."""
    errors, warnings = [], []
    try:
        formats = load_formats(formats_path)
    except KeyError as e:
        return [f"formats file: missing column {e} (needs format_id, options)"], []
    for f, opts in formats.items():
        if len(opts) < 2:
            errors.append(f"format {f}: needs at least two options separated by |")
    rows = read_csv(items_path)
    if not rows:
        return ["items file is empty"], warnings
    for col in ("item_id", "text"):
        if col not in rows[0]:
            errors.append(f"items file: missing column {col}")
    if errors:
        return errors, warnings
    seen, blank = set(), []
    for n, r in enumerate(rows, start=2):
        iid = r["item_id"]
        if not iid:
            errors.append(f"items row {n}: item_id is blank")
        elif iid in seen:
            errors.append(f"items row {n}: item_id {iid} appears twice")
        seen.add(iid)
        if not r.get("text"):
            blank.append(iid)
        fmt = r.get("format") or "agree5"
        if fmt not in formats:
            errors.append(f"items row {n} ({iid}): format {fmt} is not in the formats file")
        fac = r.get("factor", "")
        if fac and fac not in FACTORS:
            errors.append(f"items row {n} ({iid}): factor {fac} is not one of {', '.join(FACTORS)}")
    if blank:
        errors.append(f"{len(blank)} item(s) have no text: {', '.join(blank[:5])}{' ...' if len(blank) > 5 else ''}")
    if scales_path:
        sc = read_csv(scales_path)
        if sc and not {"scale", "item_id"} <= set(sc[0]):
            errors.append("scales file: needs columns scale, item_id and key")
        else:
            fmt_of = {r["item_id"]: (r.get("format") or "agree5") for r in rows}
            by_scale = {}
            for n, r in enumerate(sc, start=2):
                if r["item_id"] not in seen:
                    errors.append(f"scales row {n}: item {r['item_id']} is not in the items file")
                k = (r.get("key") or "1").strip()
                if k not in ("1", "+1", "-1", "R", "r", "reverse"):
                    errors.append(f"scales row {n}: key {k} should be 1 or -1")
                by_scale.setdefault(r["scale"], []).append(r["item_id"])
            for s, its in by_scale.items():
                if len({len(formats.get(fmt_of.get(i, "agree5"), [])) for i in its if i in fmt_of}) > 1:
                    errors.append(f"scale {s}: mixes items with different numbers of options")
                if len(its) < 3:
                    warnings.append(f"scale {s}: {len(its)} items; alpha and item-total r need at least 3")
    return errors, warnings
