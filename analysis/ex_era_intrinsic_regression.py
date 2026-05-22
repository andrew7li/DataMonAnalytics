from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "cleaned" / "ex_era_mega_merged_enriched_with_isEX.csv"
OUTPUT_PATH = BASE_DIR / "analysis" / "ex_era_intrinsic_regression_output.txt"


def add_log_price(df):
    df["marketPrice"] = pd.to_numeric(df["marketPrice"], errors="coerce")

    if "log_market_price" not in df.columns:
        df["log_market_price"] = np.where(
            df["marketPrice"] > 0,
            np.log(df["marketPrice"]),
            np.nan
        )

    return df


def clean_for_modeling(df):
    df = add_log_price(df)

    # Drop rows where target cannot be calculated
    df = df[df["log_market_price"].notna()].copy()

    bool_cols = [
        "isstarter",
        "islegendary",
        "ismythical",
        "isgoldstar",
        "istrainer",
        "iseeveelution",
        "isdeltaspecies",
        "isEXcard",
    ]

    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype("boolean").fillna(False).astype(bool)

    cat_cols = [
        "source_set_name",
        "extRarity",
        "subTypeName",
        "generation",
    ]

    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna("missing").astype(str)

    return df


def fit_model(df, formula, title):
    model = smf.ols(formula=formula, data=df).fit(cov_type="HC3")

    output = []
    output.append(title)
    output.append("=" * 100)
    output.append(f"Formula:\n{formula}")

    output.append("\nModel summary:")
    output.append(model.summary().as_text())

    coef_table = pd.DataFrame({
        "coef": model.params,
        "p_value": model.pvalues,
        "std_err": model.bse,
        "conf_low": model.conf_int()[0],
        "conf_high": model.conf_int()[1],
    })

    coef_table = coef_table.sort_values("p_value")

    output.append("\nCoefficients sorted by p-value:")
    output.append(coef_table.to_string())

    interpreted = coef_table.copy()
    interpreted["percent_change"] = (np.exp(interpreted["coef"]) - 1) * 100
    interpreted = interpreted.sort_values("p_value")

    output.append("\nApproximate percent change from log coefficient:")
    output.append(interpreted[["coef", "percent_change", "p_value"]].to_string())

    return "\n".join(output), model


def main():
    df = pd.read_csv(INPUT_PATH)
    df = clean_for_modeling(df)

    lines = []

    lines.append("EX ERA / MEGA ERA INTRINSIC CARD VALUE REGRESSION")
    lines.append("=" * 100)
    lines.append(f"Input file: {INPUT_PATH}")
    lines.append(f"Rows used after dropping invalid prices: {len(df)}")
    lines.append(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------
    # Model 1: structural controls only
    # rarity + finish/art type + set
    # ------------------------------------------------------------
    formula_1 = (
        "log_market_price ~ "
        "C(extRarity) + C(subTypeName) + C(source_set_name)"
    )

    text, model_1 = fit_model(
        df,
        formula_1,
        "MODEL 1: STRUCTURAL CONTROLS ONLY"
    )
    lines.append("\n\n" + text)

    # ------------------------------------------------------------
    # Model 2: structural controls + intrinsic card traits
    # ------------------------------------------------------------
    formula_2 = (
        "log_market_price ~ "
        "C(extRarity) + C(subTypeName) + C(source_set_name) + "
        "C(generation) + "
        "isstarter + islegendary + ismythical + isgoldstar + "
        "iseeveelution + isdeltaspecies + isEXcard"
    )

    text, model_2 = fit_model(
        df,
        formula_2,
        "MODEL 2: STRUCTURAL CONTROLS + INTRINSIC TRAITS"
    )
    lines.append("\n\n" + text)

    lines.append("\n\nMODEL COMPARISON")
    lines.append("=" * 100)

    comparison = pd.DataFrame([
        {
            "model": "Model 1 Structural Controls",
            "nobs": int(model_1.nobs),
            "r_squared": model_1.rsquared,
            "adj_r_squared": model_1.rsquared_adj,
            "aic": model_1.aic,
            "bic": model_1.bic,
        },
        {
            "model": "Model 2 Controls + Intrinsic Traits",
            "nobs": int(model_2.nobs),
            "r_squared": model_2.rsquared,
            "adj_r_squared": model_2.rsquared_adj,
            "aic": model_2.aic,
            "bic": model_2.bic,
        },
    ])

    lines.append(comparison.to_string(index=False))

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Regression output saved to: {OUTPUT_PATH}")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()