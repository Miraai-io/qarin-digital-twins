# Demo study

Eleven items written for this repository: two agreement scales (Planning, Social Ease) and one frequency
scale (Checking). They show every feature of the study files: a custom answer format, reverse-keyed items,
and the optional `factor` column.

```
python -m qarin check --items examples/demo/items.csv --scales examples/demo/scales.csv --formats examples/demo/formats.csv
python -m qarin run --items examples/demo/items.csv --formats examples/demo/formats.csv --out results/demo.csv --dry-run
python -m qarin run --items examples/demo/items.csv --formats examples/demo/formats.csv --out results/demo.csv --profiles data/profiles/Q001.json
python -m qarin run --items examples/demo/items.csv --formats examples/demo/formats.csv --out results/demo.csv
python -m qarin analyze --results results/demo.csv --scales examples/demo/scales.csv --out results/demo_analysis
```

The third command runs one twin, a cheap way to see a result before running all 100. Running the fourth
command after it adds the other 99 to the same results file.
