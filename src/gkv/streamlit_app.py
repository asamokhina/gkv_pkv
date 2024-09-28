import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

root_dir = Path(".data/").resolve()


def read_pkv():
    df_pkv = pd.read_csv(root_dir / "pkv-entwicklung-vpi.csv", sep=";")
    df_pkv["percent"] = df_pkv["Beitrag zur privaten Krankenversicherung"].pct_change()
    df_pkv["percent"].iloc[0] = 0
    return df_pkv


def read_insurance():
    df_insurance = pd.read_csv(root_dir / "contribution_rates.csv")
    return df_insurance["Yearly Increase (%)"].values[1:]


def read_zusatz():
    return pd.read_csv(
        root_dir / "additional_contribution_rates_with_increase.csv"
    )


def read_rente_anpassung():
    return pd.read_csv(root_dir / "rentenanpassung-verbraucherpreisindex.csv", sep=";")


def read_gkv():
    df = pd.read_csv(root_dir / "gkv_contribution_rates.csv")
    df["BBG (Month)"] = df["BBG (Month)"] / 100
    df["Average GKV Contribution Rate (%)"] = (
        df["Average GKV Contribution Rate (%)"].str.replace(",", ".").astype(float)
    )
    df.index = df["Year"]
    df = df.drop(columns=["Year"])
    df = df.sort_index()
    df["BBG (Month) pct"] = df["BBG (Month)"].pct_change()
    df["BBG (Month) pct"].iloc[0] = 0
    return df


def get_salary(last_year_salary, max_salary_change_bag):
    salary_increase = np.random.choice(max_salary_change_bag)
    return last_year_salary * (1 + salary_increase)


def get_rente(last_year_rente, rente_increase_bag):
    rente_increase = np.random.choice(rente_increase_bag)
    return last_year_rente * (1 + rente_increase)


def get_gkv_cost(gkv_percent_bag, zusatz_percent_bag, income):
    gkv_percent = np.random.choice(gkv_percent_bag)
    zusatz_percent = np.random.choice(zusatz_percent_bag)

    gkv_cost = 12 * (income * gkv_percent + income * zusatz_percent)
    return gkv_cost

def add_kids_cost_to_pkv(pkv_cost, kids):
    for kid in kids:
        # start and end of care years
        if year > kid[0] and year < kid[1]:
            pkv_cost += kid_pkv_cost * 12
    return pkv_cost

def get_pkv_cost(
    pkv_increase_bag,
    pkv_cost_last_year,
    year,
    kids,
    no_pkv_extra_since_years,
    kid_pkv_cost,
):
    pkv_increase = np.random.choice(pkv_increase_bag)
    # print(f"{pkv_increase=}")
    pkv_cost = pkv_cost_last_year * (1 + pkv_increase)
    # print(f"{pkv=}")

    if year == no_pkv_extra_since_years:
        pkv_cost = pkv_cost * 0.9

    return pkv_cost


def simulate_gkv_pkv_for_lifespan(
    max_salary_for_gkv_2023,
    rente_anspruch_start,
    pkv_initial_cost,
    age_at_start,
    age_retirement,
    expected_lifespan,
    kids,
    max_salary_change_bag,
    gkv_percent_bag,
    zusatz_percent_bag,
    pkv_increase_bag,
    rente_increase_bag,
    no_pkv_extra_since_years,
    kid_pkv_cost,
):
    salary = max_salary_for_gkv_2023
    rente = rente_anspruch_start
    pkv_cost = pkv_initial_cost * 12
    gkv_year_cost = []
    pkv_year_cost = []

    working_years = range(age_at_start, age_retirement)
    retirement_years = range(age_retirement, expected_lifespan)

    for year in working_years:
        salary = get_salary(salary, max_salary_change_bag)
        rente = get_rente(rente, rente_increase_bag)

        gkv_cost = get_gkv_cost(gkv_percent_bag, zusatz_percent_bag, salary)
        # employer pays the other half
        gkv_year_cost.append(gkv_cost / 2)

        pkv_cost = get_pkv_cost(
            pkv_increase_bag,
            pkv_cost,
            year,
            kids,
            no_pkv_extra_since_years,
            kid_pkv_cost,
        )

        # pkv_cost is used to calculate next year increase
        # assign another variable to add kids cost
        if kids:
            final_pkv_cost = add_kids_cost_to_pkv(pkv_cost, kids)
        else:
            final_pkv_cost = pkv_cost

        # employer pays the other half
        pkv_year_cost.append(final_pkv_cost / 2)

        # print(f"{year}: GKV: {gkv_cost/12}, PKV: {pkv_cost/12}, Rente: {rente}")

    for year in retirement_years:
        rente = get_rente(rente, rente_increase_bag)

        gkv_cost = get_gkv_cost(gkv_percent_bag, zusatz_percent_bag, rente)
        # DRK pays the other half
        gkv_own_share_cost = gkv_cost / 2
        gkv_year_cost.append(gkv_own_share_cost)

        pkv_cost = get_pkv_cost(
            pkv_increase_bag,
            pkv_cost,
            year,
            kids,
            no_pkv_extra_since_years,
            kid_pkv_cost,
        )

        pkv_own_share_cost = pkv_cost - gkv_own_share_cost
        pkv_year_cost.append(pkv_own_share_cost)

        # print(f"{year}: GKV: {gkv_cost/12}, PKV: {pkv_cost/12}, Rente: {rente}")

    # print(f"GKV: {sum(gkv_year_cost)}, PKV: {sum(pkv_year_cost)}")
    return sum(gkv_year_cost), sum(pkv_year_cost)


def run_simulation(
    n_simulations,
    df,
    df_pkv,
    df_zusatz,
    renteanpassung,
    age_at_start,
    age_retirement,
    expected_lifespan,
    rente_anspruch_start,
    pkv_initial_cost,
    no_pkv_extra_since_years,
    kid_pkv_cost,
    kids,
):

    max_salary_for_gkv_2023 = df["BBG (Month)"].loc[2023]

    max_salary_change_bag = df["BBG (Month) pct"].values
    gkv_percent_bag = [x / 100 for x in df["Average GKV Contribution Rate (%)"].values]
    zusatz_percent_bag = [
        x / 100 for x in df_zusatz["Average Additional Contribution Rate (%)"].values
    ]
    pkv_increase_bag = df_pkv["percent"].values

    rente_increase_bag = [
        x / 100 for x in renteanpassung["Rentenanpassung West"].values
    ]

    gkv_costs = []
    pkv_costs = []

    for _ in range(n_simulations):
        g, p = simulate_gkv_pkv_for_lifespan(
            max_salary_for_gkv_2023,
            rente_anspruch_start,
            pkv_initial_cost,
            age_at_start,
            age_retirement,
            expected_lifespan,
            kids,
            max_salary_change_bag,
            gkv_percent_bag,
            zusatz_percent_bag,
            pkv_increase_bag,
            rente_increase_bag,
            no_pkv_extra_since_years,
            kid_pkv_cost,
        )
        gkv_costs.append(g)
        pkv_costs.append(p)

    return gkv_costs, pkv_costs


def calculate_wins(n_simulations, gkv_costs, pkv_costs):
    gkv_wins = 0
    pkv_wins = 0
    ties = 0
    percentage_diff = []

    for gkv, pkv in zip(gkv_costs, pkv_costs, strict=True):
        if gkv < pkv:
            gkv_wins += 1
        elif pkv < gkv:
            pkv_wins += 1
        else:
            ties += 1

        diff = ((pkv - gkv) / (pkv + gkv)) * 100
        percentage_diff.append(diff)

    gkv_wins_percentage = (gkv_wins / n_simulations) * 100
    pkv_wins_percentage = (pkv_wins / n_simulations) * 100
    ties_percentage = (ties / n_simulations) * 100

    average_percentage_diff = round(sum(percentage_diff) / n_simulations)
    return (
        gkv_wins_percentage,
        pkv_wins_percentage,
        ties_percentage,
        average_percentage_diff,
    )


def makr_plot(gkv_costs, pkv_costs):
    fig, axs = plt.subplots(3, 1)

    axs[0].boxplot([gkv_costs, pkv_costs], tick_labels=["GKV", "PKV"])
    axs[0].set_title("Box plot for costs")
    axs[0].set_ylabel("Costs sum for life")

    axs[1].hist(gkv_costs, bins=5, alpha=0.5, label="GKV")
    axs[1].hist(pkv_costs, bins=5, alpha=0.5, label="PKV")
    axs[1].set_title("Hist plot for costs")
    axs[1].set_xlabel("Costs sum for life")
    axs[1].set_ylabel("Frequency")
    axs[1].legend()

    sns.kdeplot(gkv_costs, ax=axs[2], label="GKV", fill=True, color="blue", alpha=0.5)
    sns.kdeplot(
        pkv_costs, ax=axs[2], label="PKV", fill=True, color="orange", alpha=0.5
    )
    axs[1].set_title("Density plot for costs")
    axs[1].set_xlabel("Costs sum for life")
    axs[1].set_ylabel("Density")
    axs[1].legend()

    # plt.tight_layout()
    return fig


def main():
    st.title("GKV vs PKV")

    with open(root_dir / "PKVGKV.md", "r") as f:
        st.markdown(f.read())

    st.header("Calculator")

    n_simulations = st.slider("Number of simulations", 100, 1000, 500)

    df_pkv = read_pkv()
    df_zusatz = read_zusatz()
    renteanpassung = read_rente_anpassung()
    df = read_gkv()

    age_at_start = st.slider("Age today", 20, 70, 30)
    age_retirement = st.slider("Age at retirement", 60, 80, 67)
    expected_lifespan = st.slider("Expected lifespan", 30, 100, 85)
    rente_anspruch_start = st.number_input("Retirement Claim today", 1000, 5000, 2000)
    pkv_initial_cost = st.number_input("PKV Initial Cost (Total)", 200, 1000, 500)
    no_pkv_extra_since_years = st.slider("No 10% statutory surcharge in PKV since years", 50, 70, 60)
    kid_pkv_cost = 0

    if expected_lifespan < age_at_start:
        st.error("Expected lifespan should be greater than age at start")
        return

    if "care_years" not in st.session_state:
        st.session_state.care_years = []

    kids_number = st.slider("Number of kids", 0, 5, 2)

    if len(st.session_state.care_years) < kids_number:
        # Add new entries if kids_number is increased
        st.session_state.care_years += [(age_at_start, age_at_start)] * (
            kids_number - len(st.session_state.care_years)
        )
    elif len(st.session_state.care_years) > kids_number:
        # Trim the list if kids_number is decreased
        st.session_state.care_years = st.session_state.care_years[:kids_number]

    for i in range(kids_number):
        start, end = st.session_state.care_years[i]
        new_start = st.slider(
            f"Kid {i+1} start of care. Your age",
            age_at_start,
            expected_lifespan,
            start,
            key=f"start_{i}",
        )
        new_end = st.slider(
            f"Kid {i+1} end of care. Your age",
            age_at_start,
            expected_lifespan,
            end,
            key=f"end_{i}",
        )
        st.session_state.care_years[i] = (new_start, new_end)

    if st.session_state.care_years:
        kid_pkv_cost = st.number_input("Kid PKV Monthly Cost", 50, 500, 200)

    # button to start simulation
    if st.button("Start simulation"):

        gkv_costs, pkv_costs = run_simulation(
            n_simulations,
            df,
            df_pkv,
            df_zusatz,
            renteanpassung,
            age_at_start,
            age_retirement,
            expected_lifespan,
            rente_anspruch_start,
            pkv_initial_cost,
            no_pkv_extra_since_years,
            kid_pkv_cost,
            st.session_state.care_years,
        )

        (
            gkv_wins_percentage,
            pkv_wins_percentage,
            ties_percentage,
            average_percentage_diff,
        ) = calculate_wins(n_simulations, gkv_costs, pkv_costs)

        st.write(f"GKV average lifetime cost: {int(np.mean(gkv_costs))}")

        st.write(f"PKV average lifetime cost: {int(np.mean(pkv_costs))}")

        st.write(
            f"GKV wins: {gkv_wins_percentage}%, PKV wins: {pkv_wins_percentage}%, Ties: {ties_percentage}%"
        )
        st.write(f"Average percentage difference: {average_percentage_diff}%")

        fig = makr_plot(gkv_costs, pkv_costs)
        st.pyplot(fig)

    with open(root_dir / "methodology.md", "r") as f:
        st.markdown(f.read())


main()
