# Qarin - Digital Twins

Digital twins of 100 real people who answered the Miraai Personality, with the same people's answers to the
HEXACO-100. Give the twins your own questionnaire items and they answer them as those people would, so you
can see how a draft item or scale behaves before you recruit anyone, and check the twins against real
people on a public instrument.

A twin is a language-model respondent built from one person's biodata and a written profile of their
personality. Miraai calls its twins **Qarin profiles**, from the Arabic *qarin* (قرين), companion,
pronounced ka-REEN. The method and its evidence are in the report *The Pilot Before the Pilot*
(MIR-TR-007, Miraai Ltd, 2026), on OSF: https://osf.io/pv67f/.

For noncommercial research and teaching. See [License](#license).

---

## Contents

1. [What the twins do](#what-the-twins-do)
2. [What is in this repository](#what-is-in-this-repository)
3. [Before you start](#before-you-start)
4. [Quick start](#quick-start)
5. [Step by step](#step-by-step)
6. [Your study files](#your-study-files)
7. [Reading the results](#reading-the-results)
8. [Worked example: the HEXACO-100](#worked-example-the-hexaco-100)
9. [How a twin answers](#how-a-twin-answers)
10. [Troubleshooting](#troubleshooting)
11. [License, citation and acknowledgments](#license)

---

## What the twins do

In the report, twins built this way:

- **Carry the person to another instrument.** On the HEXACO-100, which no twin was built from, a twin's
  domain scores correlate .64 with the person's own, about as well as a regression on the person's Miraai scores
  fitted without that person. For the 100 people released here, with the release's biodata, the figure is
  .65.
- **Reproduce group differences.** On the Miraai Personality, the twins' differences between demographic
  groups correlate .99 with the people's.
- **Catch bad items.** Seeded among real items, 33 of 36 items with a critical defect (gendered, age-typed
  or ethnicity-typed content, wrong keying, double-barrelled wording) were flagged by the twin sample, and
  1 of 16 well-written controls.

They are a pilot sample for items and scales. They are not a norm group, and a twin's answers are not a
statement about the person it copies.

---

## What is in this repository

```
qarin-digital-twins/
├── README.md                  this file
├── LICENSE.md                 the licenses in brief, and third-party terms
├── LICENSE-CODE.md            PolyForm Noncommercial 1.0.0 (software)
├── LICENSE-DATA.md            CC BY-NC 4.0 (data and documentation)
├── CITATION.cff               how to cite
├── requirements.txt           Python packages
├── .env.example               where your API key goes
├── data/
│   ├── CODEBOOK.md            every file and variable
│   ├── people.csv             100 people: age band, gender, degree
│   ├── profiles/              Q001.json ... Q100.json, the twins
│   ├── miraai_scores.csv      each person's Miraai factor and trait scores
│   ├── hexaco100_responses.csv  each person's HEXACO-100 answers, by item number
│   └── hexaco100_scores.csv   each person's HEXACO-100 domain and facet scores
├── qarin/                     the software (run with python -m qarin)
├── templates/                 blank study files to copy
├── examples/demo/             a small study written for this repository
├── instruments/hexaco100/     scales and keys for the HEXACO-100 (no item text)
└── tests/test_offline.py      checks the installation without a key or a network
```

---

## Before you start

- **Python 3.10 or later.** Check with `python --version`.
- **An API key for Jev**, the answering model from TypeSafe (https://typesafe.ai). Every twin answer is a
  request to Jev, made with your key, under your agreement with TypeSafe.
- **Your items**, as you would show them to respondents, and, if you want scale statistics, which items
  belong to which scale and which are reverse-keyed.

No Miraai or HEXACO item text is included, and none is needed to use the twins on your own items.

---

## Quick start

```bash
git clone https://github.com/Miraai-io/qarin-digital-twins.git
cd qarin-digital-twins
pip install -r requirements.txt
python tests/test_offline.py                      # should end with "offline test passed"
cp .env.example .env                              # then paste your key into .env
python -m qarin check --items examples/demo/items.csv --scales examples/demo/scales.csv --formats examples/demo/formats.csv
python -m qarin run --items examples/demo/items.csv --formats examples/demo/formats.csv --out results/demo.csv
python -m qarin analyze --results results/demo.csv --scales examples/demo/scales.csv --out results/demo_analysis
```

On Windows, use `copy .env.example .env`, and `py` in place of `python` if that is how Python is installed.

---

## Step by step

### 1. Install

```bash
pip install -r requirements.txt
python tests/test_offline.py
```

The offline test runs the whole pipeline on the demo study with a stand-in for the answering model. It needs
no key and sends nothing. If it ends with `offline test passed`, the installation works.

### 2. Add your API key

Copy `.env.example` to `.env` and put your key after the `=`:

```
TYPESAFE_API_KEY=your-key-here
```

Or set `TYPESAFE_API_KEY` as an environment variable. `.env` is listed in `.gitignore`; never commit it.

### 3. Write your study files

Copy the three files in `templates/` to a folder of your own, for example `my_study/`, and fill them in.
[Your study files](#your-study-files) describes every column.

| File | Needed for | What it holds |
|---|---|---|
| `items.csv` | every run | one row per item: code, text, answer format, and optionally a Miraai factor |
| `formats.csv` | only if you use answer options other than the five-point agreement scale | the answer options of each format, low to high |
| `scales.csv` | scoring and analysis | which items make up each scale, and which are reverse-keyed |

### 4. Check the files

```bash
python -m qarin check --items my_study/items.csv --scales my_study/scales.csv --formats my_study/formats.csv
```

It lists anything that would stop a run (a blank item, a duplicate code, a format that is not defined, a
scale item that is not in the items file) and ends with `OK` when the files are ready.

### 5. See exactly what will be sent

```bash
python -m qarin run --items my_study/items.csv --formats my_study/formats.csv --out results/my_study.csv --dry-run
```

This prints the first request for the first twin, the profile and your first item as the model will read
them, and stops. It sends nothing and needs no key.

### 6. Run one twin, then all of them

```bash
python -m qarin run --items my_study/items.csv --formats my_study/formats.csv --out results/my_study.csv --profiles data/profiles/Q001.json
python -m qarin run --items my_study/items.csv --formats my_study/formats.csv --out results/my_study.csv
```

The first command runs one twin; the second adds the other 99 to the same results file. Each twin answers
every item three times, once with each of its three profiles, 50 items to a request. A run that stops, for
a lost connection or anything else, picks up where it left off when you run the same command again: the
progress is kept in `results/my_study.csv.jsonl`. If you change the items, use a new `--out` name.

Options:

| Option | Effect |
|---|---|
| `--profiles` | a profile file or a folder of them; the default is all 100 in `data/profiles` |
| `--workers 4` | how many twins run at once |
| `--factor-scoped` | also answer each item that has a `factor` with the profile of that Miraai factor alone (see [How a twin answers](#how-a-twin-answers)) |

### 7. Score and analyze

```bash
python -m qarin score   --results results/my_study.csv --scales my_study/scales.csv --out results/my_study_scores.csv
python -m qarin analyze --results results/my_study.csv --scales my_study/scales.csv --out results/my_study_analysis
```

`score` writes one row per twin and one column per scale. `analyze` writes the pilot statistics and the
comparison with the people; [Reading the results](#reading-the-results) explains each file. Add
`--human my_study/human_scores.csv` to `analyze` if you have the same people's own scores on your scales, as
you do for the HEXACO-100.

---

## Your study files

### items.csv

| Column | Required | Content |
|---|---|---|
| `item_id` | yes | your code for the item; letters, numbers and underscores |
| `text` | yes | the item exactly as respondents read it; put it in double quotes if it contains a comma |
| `format` | no | a `format_id` from `formats.csv`; blank means `agree5` |
| `factor` | no | the Miraai factor the item measures, used only with `--factor-scoped`: `HH` Honesty-Humility, `Em` Emotional Stability, `Ex` Extraversion, `Ag` Agreeableness, `Co` Conscientiousness, `Op` Openness |

Items can be statements ("I plan my week before it starts.") or questions ("How often do you check your
work twice?"). The twin is asked how the person in its profile would answer the item on a questionnaire
about themselves, so write items that a person answers about themselves.

### formats.csv

| Column | Content |
|---|---|
| `format_id` | a short name, used in the `format` column of `items.csv` |
| `options` | the answer options from lowest to highest, separated by `\|` |

`agree5` (Strongly Disagree, Disagree, Neutral, Agree, Strongly Agree) is built in. The template also
defines `freq5` and `agree7`; delete the rows you do not need or add your own. Options are scored 1 to K
from left to right, so the first option must be the lowest.

### scales.csv

| Column | Content |
|---|---|
| `scale` | the scale name; it becomes a column name in the output |
| `item_id` | an item in `items.csv` |
| `key` | `1` for an item scored as answered, `-1` for a reverse-keyed item (scored K + 1 − answer) |

One row per item and scale. An item can belong to more than one scale, for example a facet and its domain.
Scale scores are the mean of their items (`--sum` gives sums). All items of one scale need the same number of
answer options.

### human_scores.csv (optional)

If you have the same people's own scores on your scales, put them in a file with a `qarin_id` column and one
column per scale, named exactly as in `scales.csv`. For the HEXACO-100 this file is provided as
`data/hexaco100_scores.csv`.

---

## Reading the results

### The results file (`run`)

One row per twin and item: `qarin_id`, `item_id`, `format`, `n_options`, `p1` to `pK` (the probability of
each answer option, averaged over the twin's profiles), `expected` (the expected answer, 1 to K) and
`n_profiles` (3, or 6 with `--factor-scoped`).

The model returns a probability for every option, not a single answer. The probabilities are the twin's
answer; `expected` is their average on the 1 to K scale.

### The analysis folder (`analyze`)

| File | Content |
|---|---|
| `item_stats.csv` | per item and scale: keyed mean, SD, and corrected item-total correlation |
| `scale_stats.csv` | per scale: number of items, coefficient alpha, mean and SD of scale scores |
| `twin_scores.csv` | each twin's scale scores from its expected answers |
| `miraai_correlations.csv` | each scale's correlation, across the 100 twins, with the people's own Miraai factor and trait scores |
| `human_comparison.csv` | with `--human`: per scale, the correlation of twin and person, and the mean difference in the people's SD units |
| `summary.txt` | the headline figures |

Item and scale statistics use **drawn answers**: one answer per twin and item, sampled from its
probabilities, as a real respondent gives one answer. The statistics are averaged over 10 draws
(`--draws`). Person-level scores use the expected answers.

### What to read into them

- **Rank items, do not quote their values.** On rating scales the twins answer a little more moderately
  than people: fewer answers at the ends of the scale, means slightly low. The order of items by mean and
  by item-total correlation is the useful part; the exact values are not a forecast of a human pilot.
- **A weak item among good ones is the signal.** An item whose item-total correlation is well below the
  rest of its scale, or whose mean sits at the end of the scale, is the item to rewrite.
- **Relations with the Miraai scores** show what a new scale carries of the Big Five and Honesty-Humility
  in the people behind the twins. They are between-person correlations over 100 twins: read the pattern,
  not the second decimal.
- **Fit indices from twin data** are not evidence about an instrument: twins answer more consistently than
  people, and models fit them better.
- **Nothing here is a norm** and no twin answer describes the real person.

---

## Worked example: the HEXACO-100

The HEXACO-100 is the one instrument for which you have both the twins and the people. It is the way to see
how close the twins come on a published inventory before you trust them with your own items.

1. Get the inventory from hexaco.org. It is free for noncommercial academic research.
2. Open `instruments/hexaco100/items.csv`. It has one row per item, `h001` to `h100` in the published
   order, with the format and factor filled in and the `text` column empty. Paste each item's text into
   its row.
3. Check and run:

   ```bash
   python -m qarin check   --items instruments/hexaco100/items.csv --scales instruments/hexaco100/scales.csv
   python -m qarin run     --items instruments/hexaco100/items.csv --out results/hexaco.csv
   python -m qarin analyze --results results/hexaco.csv --scales instruments/hexaco100/scales.csv \
                           --human data/hexaco100_scores.csv --out results/hexaco_analysis
   ```

4. `human_comparison.csv` gives, for every domain and facet, the correlation of each twin's score with its
   person's. The report's figure for the domains is .64 on 116 people (.65 for these 100).

The report's person-level figures use the full profiles, as the commands above do. Adding
`--factor-scoped` lowers the correlation with the people on the HEXACO-100 (report, Table 16.1).

Keep your copy of the item file private: the HEXACO-100 item text is the authors' and is not
redistributed.

---

## How a twin answers

Each profile file holds, for one person:

- `biodata`: three sentences, from the person's age band, gender and whether they hold a bachelor's degree.
  A field left blank in the data gives no sentence.
- `form_B`, `form_C` and `form_D`: three profiles, each a written description of the person's 24 Miraai
  facets. Each is built from a different two-thirds of the person's Miraai answers, so the three agree
  closely but not exactly, the way three observers of one person would.
- Under each form, `full` is the whole profile, and `factor` holds six shorter versions (`HH`, `Em`, `Ex`,
  `Ag`, `Co`, `Op`), each with only the four facets of one factor.

The profile text is the twin: `run` sends it as it is, with your item, and asks the model how the person
in the profile would answer. Averaging the three forms gives each twin an answer that is neither too sure
nor too scattered. The rule that turns a person's answers into descriptors is not released, and the
profiles cannot be regenerated from other data.

`--factor-scoped` suits items that each measure a single Big Five or Honesty-Humility factor, where you want
the twin to answer from that factor alone. For person-level agreement on a broad inventory, the full
profile does better.

---

## Troubleshooting

| Message | What to do |
|---|---|
| `No API key` | create `.env` from `.env.example`, or set `TYPESAFE_API_KEY` |
| `HTTP 401` or `HTTP 403` | the key is wrong or not active; check it with TypeSafe |
| `HTTP 429` or `529` | the service is busy; the runner waits and retries by itself |
| `...was written for different items or settings` | you changed the items or options since the first run; use a new `--out` name |
| `format ... is not in the formats file` | pass `--formats` with the file that defines it |
| a stopped or interrupted run | run the same command again; finished twins are kept |
| empty `p1..pK` in a row | the model returned nothing for that item; rerunning with a new `--out` repeats the run |

---

## License

Software: PolyForm Noncommercial License 1.0.0. Data and documentation: Creative Commons
Attribution-NonCommercial 4.0 International. Both allow noncommercial research and teaching; neither allows
commercial use. `LICENSE.md` explains which applies to what, and the terms for the HEXACO-100 and the
answering model.

For commercial use, or for a research collaboration with the full sample of 662 twins, contact Miraai:
tariq@miraai.me.

## Citation

Shaban, T. (2026). *The pilot before the pilot: Digital twins of 662 known respondents as a pilot sample
for new items* (MIR-TR-007). Miraai Ltd. https://osf.io/pv67f/

When you use the HEXACO-100 data, also cite:

- Lee, K., & Ashton, M. C. (2004). Psychometric properties of the HEXACO personality inventory.
  *Multivariate Behavioral Research, 39*, 329–358.
- Lee, K., & Ashton, M. C. (2018). Psychometric properties of the HEXACO-100. *Assessment, 25*(5), 543–556.

## Acknowledgments

HEXACO-100 responses are shared with the permission of Kibeom Lee and Michael C. Ashton. The inventory is
available at hexaco.org and is free for noncommercial academic research.

The people behind these twins took part in the Miraai Open Research Program and consented to the release of
their de-identified data. Please use it with care: do not attempt to identify anyone.
