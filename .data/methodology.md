
## Methodology 
**One-liner:** Monte Carlo simulation of insurance price development based on historical data.

**A bit longer version:** I gathered historical data on key variables we’re trying to predict, such as average PKV price changes and the percentage of salary allocated to GKV. I treat these variables as part of a random process (a simplified approach to the unpredictability of politics and economics). For each simulation and each step, I randomly select one of the available yearly values from the historical data. The final output presents statistics from all the combined simulations.

### Full version

**GKV Price Calculation Method**

GKV’s monthly price is a percentage of your salary (14.6% plus the Zusatzbeitrag as of 2024), capped at an income of €69,300. The calculations assume this maximum value since below this threshold, switching to PKV wouldn't be an option. The 14.6% rate has been stable since 2015, but it fluctuated before that, so both the maximum income and the percentage are modeled in the simulation.

In addition to the fixed 14.6%, there's a variable fee called the Zusatzbeitrag, which varies between providers based on their financial situation. I use the average across the industry for this fee. Predictions for the Zusatzbeitrag are made annually by the Federal Ministry of Health, but I rely on the actual values that are calculated as the year progresses.

As an employee, you pay half of the GKV premium, while your employer covers the other half. This continues into retirement, with the Deutsche Rentenversicherung (DRV) covering the employer's portion. In the simulation, the total cost is modeled, but only half is considered as your personal expense.

Children don’t impact your GKV payments, as they are insured for free, unless the second parent is insured through PKV, but this calculator doesn't account for that level of detail.

GKV Calculation Steps:
1. Model yearly maximum income or pension.
2. Model the yearly percentage of income.
3. Model the Zusatzbeitrag.
4. Calculate the yearly insurance cost and assume only half as your expense.

**PKV Price Calculation Method**

PKV premiums are not based on your income. Instead, the initial price depends on factors such as your age, health status, and the specific plan you choose. You can get an estimate by searching online (Check24 is a good starting point).

The future development of PKV premiums is influenced by several factors. Insurance companies in Germany can't raise prices arbitrarily; they must demonstrate that conditions have changed. For example, if more insurance benefits are consumed than expected (such as a new treatment becoming widely available) or life expectancy changes, the premiums can increase. The simulation models these price adjustments using the average changes from the last 9 years.

To ease the financial burden of insurance in retirement, PKV includes something called Alterungsrückstellungen. Before age 60, you pay an extra 10%, which helps lower your premiums once you turn 60, at which point this extra charge is removed, and your monthly costs decrease.

Your employer covers half of your PKV premiums while you're employed. However, in retirement, you are responsible for the full cost. You can apply for Rentenzuschuss zur privaten Krankenversicherung, a state program that helps elderly individuals by reducing insurance costs. It covers 8.1% of the GKV rate based on your income level.

Unlike GKV, PKV requires you to pay extra for each family member you wish to add to your plan.

PKV Calculation Steps:
1. Start with the initial premium.
2. Simulate premium changes over time.
3. If applicable, include the cost of insuring children.
4. During employment, assume half of the premium is paid by the employer.
5. After Age 60: Drop the additional 10% charge to reflect the reduction in premium.
6. Retirement: Subtract the Rentenzuschuss from your premium to account for state assistance.
