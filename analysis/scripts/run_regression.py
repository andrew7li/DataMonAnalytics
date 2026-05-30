from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT_DIR = Path(__file__).resolve().parents[2]

# Change this to whichever dataset you want to run.
# Options: "sv", "ex_era", "sv_pricecharting"
DATASET = "sv_pricecharting"

DATA_PATHS = {
    "sv": ROOT_DIR / "data" / "processed" / "sv_modeling_dataset.csv",
    "ex_era": ROOT_DIR / "data" / "processed" / "ex_era_dataset.csv",
    "sv_pricecharting": ROOT_DIR / "data" / "processed" / "sv_pricecharting_sales_graded_clean.csv",
}

OUTPUT_PATHS = {
    "sv": ROOT_DIR / "analysis" / "outputs" / "sv" / "regression_output.txt",
    "ex_era": ROOT_DIR / "analysis" / "outputs" / "ex_era" / "regression_output.txt",
    "sv_pricecharting": ROOT_DIR / "analysis" / "outputs" / "sv_pricecharting" / "regression_output.txt",
}

DATA_PATH = DATA_PATHS[DATASET]
OUTPUT_PATH = OUTPUT_PATHS[DATASET]


REGRESSION_CONFIG = {
    "sv": {
        "title": "SCARLET/VIOLET INTRINSIC CARD VALUE REGRESSION",
        "price_col": "marketPrice",
        "log_col": "logMarketPrice",
        "bool_cols": [
            "isLegendary",
            "isMythical",
            "isStarter",
            "isEeveelution",
            "isWaifuTrainer",
        ],
        "cat_cols": [
            "setName",
            "cardRarity",
            "finishType",
            "patternType",
        ],
        "models": [
            (
                "MODEL 1: STRUCTURAL CONTROLS ONLY",
                "logMarketPrice ~ "
                "C(cardRarity) + C(finishType) + C(patternType) + C(setName)",
            ),
            (
                "MODEL 2: STRUCTURAL CONTROLS + CHARACTER FLAGS",
                "logMarketPrice ~ "
                "C(cardRarity) + C(finishType) + C(patternType) + C(setName) + "
                "isLegendary + isMythical + isStarter + isEeveelution + isWaifuTrainer",
            ),
        ],
        "comparison_names": [
            "Model 1 Structural Controls",
            "Model 2 Controls + Character Flags",
        ],
    },

    "ex_era": {
        "title": "EX ERA / MEGA ERA INTRINSIC CARD VALUE REGRESSION",
        "price_col": "marketPrice",
        "log_col": "log_market_price",
        "bool_cols": [
            "isstarter",
            "islegendary",
            "ismythical",
            "isgoldstar",
            "istrainer",
            "iseeveelution",
            "isdeltaspecies",
            "isEXcard",
        ],
        "cat_cols": [
            "source_set_name",
            "extRarity",
            "subTypeName",
            "generation",
        ],
        "models": [
            (
                "MODEL 1: STRUCTURAL CONTROLS ONLY",
                "log_market_price ~ "
                "C(extRarity) + C(subTypeName) + C(source_set_name)",
            ),
            (
                "MODEL 2: STRUCTURAL CONTROLS + INTRINSIC TRAITS",
                "log_market_price ~ "
                "C(extRarity) + C(subTypeName) + C(source_set_name) + "
                "C(generation) + "
                "isstarter + islegendary + ismythical + isgoldstar + "
                "iseeveelution + isdeltaspecies + isEXcard",
            ),
        ],
        "comparison_names": [
            "Model 1 Structural Controls",
            "Model 2 Controls + Intrinsic Traits",
        ],
    },

    "sv_pricecharting": {
        "title": "SCARLET/VIOLET PRICECHARTING GRADED SALES REGRESSION",
        "price_col": "salePrice",
        "log_col": "logSalePrice",

        "bool_cols": [
            "isLegendary",
            "isMythical",
            "isStarter",
            "isEeveelution",
            "isWaifuTrainer",
            "isExCard",
            "isParadoxPokemon",
            "isPaldeanStarter",
            "isSVBoxLegendary",
            "isSecretNumber",
            "isTrainerPokemon",
            "isPromo",
            "isMasterBall",
            "isTerastal",
        ],

        "cat_cols": [
            "setName",
            "setEra",
            "supertype",
            "cardSubType",
            "stage",
            "cardRarity",
            "finishType",
            "patternType",
            "pokemonGeneration",
            "grade",
        ],

        "models": [
            (
                "MODEL 1: INTRINSIC CARD FEATURES ONLY",
                "logSalePrice ~ "
                "C(cardRarity) + C(finishType) + C(patternType) + C(setName) + "
                "C(supertype) + C(cardSubType) + C(stage) + C(pokemonGeneration) + "
                "isLegendary + isMythical + isStarter + isEeveelution + isWaifuTrainer + "
                "isExCard + isParadoxPokemon + isPaldeanStarter + isSVBoxLegendary + "
                "isSecretNumber + isTrainerPokemon + isPromo + isMasterBall + isTerastal",
            ),
            (
                "MODEL 2: INTRINSIC CARD FEATURES + GRADE",
                "logSalePrice ~ "
                "C(grade) + "
                "C(cardRarity) + C(finishType) + C(patternType) + C(setName) + "
                "C(supertype) + C(cardSubType) + C(stage) + C(pokemonGeneration) + "
                "isLegendary + isMythical + isStarter + isEeveelution + isWaifuTrainer + "
                "isExCard + isParadoxPokemon + isPaldeanStarter + isSVBoxLegendary + "
                "isSecretNumber + isTrainerPokemon + isPromo + isMasterBall + isTerastal",
            ),
        ],

        "comparison_names": [
            "Model 1 Intrinsic Features Only",
            "Model 2 Intrinsic Features + Grade",
        ],
    },
}


def add_log_price(df, price_col, log_col):
    """
    Create a log price column if it does not already exist.

    For sv/ex_era:
        price_col = marketPrice

    For sv_pricecharting:
        price_col = salePrice
    """

    if price_col not in df.columns:
        raise ValueError(f"Expected price column '{price_col}' was not found.")

    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    if log_col not in df.columns:
        df[log_col] = np.where(
            df[price_col] > 0,
            np.log(df[price_col]),
            np.nan,
        )

    return df


def clean_bool_column(series):
    """
    Convert mixed boolean/string columns into real bools.
    Handles True/False, TRUE/FALSE, 1/0, yes/no.
    """

    return (
        series
        .fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
        })
        .fillna(False)
        .astype(bool)
    )


def clean_for_modeling(df, config):
    price_col = config["price_col"]
    log_col = config["log_col"]

    df = add_log_price(df, price_col, log_col)

    # Drop rows where the target cannot be modeled.
    df = df[df[log_col].notna()].copy()

    for col in config["bool_cols"]:
        if col in df.columns:
            df[col] = clean_bool_column(df[col])
        else:
            # This keeps formulas from crashing if a newer flag
            # is missing from an older dataset.
            df[col] = False

    for col in config["cat_cols"]:
        if col in df.columns:
            df[col] = df[col].fillna("missing").astype(str)
        else:
            df[col] = "missing"

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

    output.append("\nMost positive estimated effects:")
    output.append(
        interpreted
        .sort_values("percent_change", ascending=False)
        .head(25)
        .to_string()
    )

    output.append("\nMost negative estimated effects:")
    output.append(
        interpreted
        .sort_values("percent_change", ascending=True)
        .head(25)
        .to_string()
    )

    return "\n".join(output), model


def main():
    config = REGRESSION_CONFIG[DATASET]

    df = pd.read_csv(DATA_PATH, low_memory=False)
    df = clean_for_modeling(df, config)

    lines = []
    lines.append(config["title"])
    lines.append("=" * 100)
    lines.append(f"Input file: {DATA_PATH}")
    lines.append(f"Rows used after dropping invalid prices: {len(df)}")
    lines.append(f"Columns: {len(df.columns)}")
    lines.append(f"Price column: {config['price_col']}")
    lines.append(f"Log price column: {config['log_col']}")

    lines.append("\nPRICE SUMMARY")
    lines.append("-" * 100)
    lines.append(df[config["price_col"]].describe().to_string())

    if "grade" in df.columns:
        lines.append("\nGRADE COUNTS")
        lines.append("-" * 100)
        lines.append(df["grade"].value_counts(dropna=False).to_string())

    models = []

    for title, formula in config["models"]:
        text, model = fit_model(df, formula, title)
        lines.append("\n\n" + text)
        models.append(model)

    lines.append("\n\nMODEL COMPARISON")
    lines.append("=" * 100)

    comparison = pd.DataFrame([
        {
            "model": model_name,
            "nobs": int(model.nobs),
            "r_squared": model.rsquared,
            "adj_r_squared": model.rsquared_adj,
            "aic": model.aic,
            "bic": model.bic,
        }
        for model_name, model in zip(config["comparison_names"], models)
    ])

    lines.append(comparison.to_string(index=False))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Regression output saved to: {OUTPUT_PATH}")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()