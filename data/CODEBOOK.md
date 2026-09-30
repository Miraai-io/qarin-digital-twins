# Codebook

100 Qarin profiles: digital twins of 100 respondents to the Miraai Personality (MIR-RP-001), drawn at random
from the 116 who also completed the HEXACO-100. Every file has one row, or one file, per person.

## Identifier

`qarin_id`: release ID, Q001 to Q100. It is not an ID used in any other Miraai data file.

## people.csv

| Variable | Values |
|---|---|
| `age_band` | 18-34, 35-49, 50-65 |
| `gender` | woman, man, another or not stated |
| `degree` | 1 if bachelor's degree or higher, 0 otherwise |

A blank value was withheld so that no combination of these fields, with race, identifies fewer than five
people in the MIR-RP-001 sample. No exact age, location, occupation, sector, tenure, supervisory status,
race, income, platform ID or date is released.

## profiles/Q001.json to Q100.json

| Key | Content |
|---|---|
| `qarin_id` | the release ID |
| `biodata` | the biodata sentences, written from `people.csv` |
| `form_B`, `form_C`, `form_D` | three profiles, each written from a different two-thirds of the person's Miraai answers |
| `form_*.full` | the profile with all 24 Miraai facets, as the twin receives it |
| `form_*.factor.HH` ... `.Op` | the profile with only the four facets of one factor |

The profile texts are complete: they are sent to the answering model as they are.

## miraai_scores.csv

Raw scores on the 96-pair reported form of the Miraai Personality: each pair scored −2 to +2 toward the
high pole and summed.

| Variables | Scale | Range |
|---|---|---|
| `HH`, `Em`, `Ex`, `Ag`, `Co`, `Op` | Factors: Honesty-Humility, Emotional Stability, Extraversion, Agreeableness, Conscientiousness, Openness | −32 to +32 |
| `HH_Ho`, `HH_Hu`, `Em_En`, `Em_Re`, `Ex_As`, `Ex_En`, `Ag_Co`, `Ag_Po`, `Co_In`, `Co_Or`, `Op_In`, `Op_Op` | Traits: Honesty, Humility, Engagement, Regulation, Assertiveness, Enthusiasm, Compassion, Politeness, Industriousness, Orderliness, Intellect, Openness to Experience | −16 to +16 |

No item responses and no facet scores are released.

## hexaco100_responses.csv

`h001` to `h100`: each person's answer to each HEXACO-100 item, 1 (strongly disagree) to 5 (strongly
agree), by item number in the published inventory. The item text is not included; the inventory is at
hexaco.org.

## hexaco100_scores.csv

Domain scores (`Honesty-Humility`, `Emotionality`, `Extraversion`, `Agreeableness`, `Conscientiousness`,
`Openness to Experience`), the interstitial scale (`Altruism (interstitial)`) and the 24 facet scores, each
the mean of its items after reverse-keying, from the authors' key. The column names match
`instruments/hexaco100/scales.csv`, so the file can be passed to `analyze --human` as it is.

HEXACO-100 responses are shared with the permission of Kibeom Lee and Michael C. Ashton.
