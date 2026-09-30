# HEXACO-100

`scales.csv` scores the six domains, the interstitial Altruism scale and the 24 facets from the authors'
key: each item belongs to its facet and its domain, and reverse-keyed items carry `key` −1. The scale names
match the columns of `data/hexaco100_scores.csv`.

`items.csv` lists the 100 items in the published order, `h001` to `h100`, with the answer format (`agree5`)
and the Miraai factor that matches each domain (Honesty-Humility `HH`, Emotionality `Em`, Extraversion
`Ex`, Agreeableness `Ag`, Conscientiousness `Co`, Openness to Experience `Op`; blank for the Altruism
items). The `text` column is empty: paste in each item from the inventory, available at hexaco.org and free
for noncommercial academic research. `check` reports any item still blank.

The HEXACO-100 is copyright Kibeom Lee and Michael C. Ashton. Do not commit a filled-in `items.csv` to a
public repository.
