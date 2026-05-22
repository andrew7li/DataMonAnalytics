import pandas as pd
from pathlib import Path
import re

# BASE_DIR = Path(__file__).resolve().parent.parent
# INPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "clean_merged_sv_filtered.csv"
# OUTPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "clean_merged_sv_tagged.csv"

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "cleaned" / "sv_promos_cleaned.csv"
OUTPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "cleaned" / "sv_promos_featured.csv"

LEGENDARIES = {
    "Mewtwo", "Articuno", "Zapdos", "Moltres", "Raikou", "Entei", "Suicune",
    "Lugia", "Ho-Oh", "Regirock", "Regice", "Registeel", "Latias", "Latios",
    "Kyogre", "Groudon", "Rayquaza", "Dialga", "Palkia", "Giratina",
    "Regigigas", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus",
    "Landorus", "Reshiram", "Zekrom", "Kyurem", "Xerneas", "Yveltal",
    "Zygarde", "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini",
    "Solgaleo", "Lunala", "Necrozma", "Zacian", "Zamazenta", "Eternatus",
    "Koraidon", "Miraidon", "Chien-Pao", "Ting-Lu", "Wo-Chien", "Chi-Yu",
    "Okidogi", "Munkidori", "Fezandipiti", "Ogerpon", "Terapagos"
}

MYTHICALS = {
    "Mew", "Celebi", "Jirachi", "Deoxys", "Manaphy", "Darkrai", "Shaymin",
    "Arceus", "Victini", "Keldeo", "Meloetta", "Genesect", "Diancie",
    "Hoopa", "Volcanion", "Magearna", "Marshadow", "Zeraora", "Meltan",
    "Melmetal", "Zarude", "Pecharunt"
}

STARTERS = {
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise",
    "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion",
    "Totodile", "Croconaw", "Feraligatr",
    "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken",
    "Mudkip", "Marshtomp", "Swampert",
    "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape",
    "Piplup", "Prinplup", "Empoleon",
    "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar",
    "Oshawott", "Dewott", "Samurott",
    "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox",
    "Froakie", "Frogadier", "Greninja",
    "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar",
    "Popplio", "Brionne", "Primarina",
    "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace",
    "Sobble", "Drizzile", "Inteleon",
    "Sprigatito", "Floragato", "Meowscarada",
    "Fuecoco", "Crocalor", "Skeledirge",
    "Quaxly", "Quaxwell", "Quaquaval"
}

EEVEELUTIONS = {
    "Eevee", "Vaporeon", "Jolteon", "Flareon", "Espeon", "Umbreon",
    "Leafeon", "Glaceon", "Sylveon"
}

MASCOTS = {
    "Pikachu", "Charizard", "Mew", "Mewtwo", "Eevee", "Lucario",
    "Greninja", "Gengar", "Rayquaza"
}

WAIFU_TRAINERS = {
    "Cynthia", "Iono", "Lillie", "Marnie", "Erika", "Misty", "Sabrina",
    "Gardenia", "Elesa", "Skyla", "Rosa", "Nessa", "Perrin"
}

def normalize_for_tags(name):
    name = str(name).strip()

    # Remove Poké Ball / Master Ball pattern suffix
    name = re.sub(r"\s*\((Poke Ball Pattern|Poké Ball Pattern|Master Ball Pattern)\)\s*$", "", name)

    # Remove Mega prefix
    name = re.sub(r"^Mega\s+", "", name)

    return name.strip()

def extract_pattern_type(name):
    name = str(name)

    if "Master Ball Pattern" in name:
        return "masterball"
    elif "Poke Ball Pattern" in name or "Poké Ball Pattern" in name:
        return "pokeball"
    else:
        return "none"
    
def add_features(df):
    # Pattern type (uses original name)
    df["patternType"] = df["cleanName"].apply(extract_pattern_type)

    # Normalized name for tagging
    df["tagName"] = df["cleanName"].apply(normalize_for_tags)

    name = df["tagName"].fillna("").astype(str).str.strip()

    df["isLegendary"] = name.isin(LEGENDARIES)
    df["isMythical"] = name.isin(MYTHICALS)
    df["isStarter"] = name.isin(STARTERS)
    df["isEeveelution"] = name.isin(EEVEELUTIONS)
    df["isMascot"] = name.isin(MASCOTS)
    df["isWaifuTrainer"] = name.isin(WAIFU_TRAINERS)

    return df

def main():
    df = pd.read_csv(INPUT_PATH)

    df = add_features(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()