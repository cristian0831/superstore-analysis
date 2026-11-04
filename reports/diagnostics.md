# Business Diagnostics: Main Conclusions

Based on the queries in `sql/diagnostics/` (01–05), run against `db/superstore.db`
(2014–2017 data) with `python -m src.sql_runner diagnostics`. Numbers below come from the
committed outputs in `outputs/diagnostics/tables/`.

## 1. Overall growth (`01_growth_trends.sql`)

| Year | Sales | Profit | Orders | Sales YoY | Margin |
|------|-------|--------|--------|-----------|--------|
| 2014 | 484,247 | 49,544 | 969 | — | 10.2% |
| 2015 | 470,533 | 61,619 | 1,038 | -2.8% | 13.1% |
| 2016 | 609,206 | 81,795 | 1,315 | +29.5% | 13.4% |
| 2017 | 733,215 | 93,439 | 1,687 | +20.4% | 12.7% |

- Sales dipped in 2015 but profit still rose — margin improved that year.
- Strong rebound in 2016-2017 (double-digit sales growth both years).
- Margin peaked in 2016 (13.4%) and slipped slightly in 2017 (12.7%) even though
  sales kept growing — profit growth is no longer keeping full pace with sales growth.

## 2. Growth by category (`02_growth_by_category.sql`)

- **Furniture is the weak link.** Margin is consistently low and trending down:
  3.5% (2014) → 1.8% (2015) → 3.5% (2016) → **1.4% (2017)**, despite sales growing
  every year. Furniture is generating volume without generating profit.
- **Office Supplies** is the steadiest performer: margin stayed in the 15-19% range
  all four years.
- **Technology** is the biggest profit driver by 2017 (50,684 profit, ~18.7% margin)
  and shows the strongest overall improvement since 2014.

## 3. Customer segment profitability (`03_customer_segment_profitability.sql`)

| Segment | Orders | Sales | Profit | Blended margin |
|---------|--------|-------|--------|-----------------|
| Consumer | 2,586 | 1,161,401 | 134,119 | 12% |
| Corporate | 1,514 | 706,146 | 91,979 | 13% |
| Home Office | 909 | 429,653 | 60,299 | **14%** |

- Consumer drives the most volume and absolute profit, but is the *least* efficient
  segment per dollar sold.
- Home Office is the smallest segment but the most profitable per dollar — a good
  candidate for targeted growth investment if acquisition cost allows it.

## 4. Discount impact (`04_discount_impact.sql`)

The clearest, most actionable finding in Phase 2: **discounting past ~20% reliably
destroys margin**, and the cliff is category-specific.

- At **0% discount**, every category is highly profitable (29-37% margin).
- **Furniture breaks first**: margin goes negative starting at the **21-30%** band
  (-12%) and gets progressively worse, down to **-74% at 50%+** discount.
- **Office Supplies** and **Technology** hold up better through 20-30% discounts,
  but also turn sharply negative once discounts reach 31%+ (as low as **-122%**
  for Office Supplies at 50%+, **-76%** for Technology at 50%+).
- No category has a discount band above 40% that is profitable.

**Implication:** discount policy should cap Furniture discounts well below 20%,
and treat any 40%+ discount (any category) as a near-guaranteed loss on that line item.

## 5. Regional / state profitability (`05_regional_profitability.sql`)

- **Texas is the single worst-performing state** (-25,729 profit, -15% margin,
  487 orders) — this is masked entirely by the healthy company-wide numbers in
  sections 1-3.
- Four more states are net-negative: **Ohio** (-16,971), **Pennsylvania**
  (-15,560), **Illinois** (-12,608), **North Carolina** (-7,491). Illinois and
  Texas both sit in the Central region, which looks like a regional problem, not
  an isolated-state one.
- **California** and **New York** are the profit engines of the business
  (76,381 and 74,039 profit respectively) and together account for a large share
  of total company profit — but California's margin (17%) is noticeably lower
  than New York's (24%) for a similar sales scale, suggesting room to improve
  efficiency even in the best-performing state.

## Summary of recommended actions

1. Investigate why Furniture margin keeps falling even as its sales grow —
   likely linked to the discounting problem in (4).
2. Cap discounts (especially on Furniture) below the 20% threshold where margin
   turns negative; treat 40%+ discounts as effectively off-limits company-wide.
3. Audit Texas, Ohio, Pennsylvania, Illinois, and North Carolina — these five
   states are quietly offsetting profit generated elsewhere.
4. Watch the 2017 margin dip (13.4% → 12.7%) — confirm whether it's driven by
   Furniture, deep discounting, or the underperforming states above.
5. Consider whether Home Office's higher per-dollar efficiency justifies
   increased acquisition investment in that segment.
