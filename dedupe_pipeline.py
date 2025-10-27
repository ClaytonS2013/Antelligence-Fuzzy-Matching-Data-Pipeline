import os
import yaml
import re
import pandas as pd
from datetime import datetime
from ingestion import get_last_run_time, update_last_run_time, fetch_practice_records


def load_normalization_rules(path="normalization_rules.yaml"):
    """
    Load normalization rules from a YAML file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Normalization rules file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def normalize_text(text, rules):
    """
    Normalize a text field using the provided normalization rules.
    Converts to lower case, removes punctuation, collapses whitespace,
    and substitutes known abbreviations.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # remove punctuation (keep alphanumeric and whitespace)
    text = re.sub(r"[^\w\s]", " ", text)
    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    substitutions = rules.get("substitutions", {})
    tokens = text.split()
    normalized_tokens = [substitutions.get(tok, tok) for tok in tokens]
    return " ".join(normalized_tokens)


def create_match_keys(df, rules):
    """
    Given a DataFrame with columns 'name', 'address', 'city' and 'zip',
    compute deterministic keys for exact and loose matching.
    Returns the DataFrame with additional columns.
    """
    df = df.copy()
    df["name_norm"] = df["name"].apply(lambda x: normalize_text(x, rules))
    df["address_norm"] = df["address"].apply(lambda x: normalize_text(x, rules))
    df["city_norm"] = df["city"].apply(lambda x: normalize_text(x, rules))
    # ensure zip is a string and stripped
    df["zip_norm"] = df["zip"].astype(str).str.strip()
    df["exact_key"] = df["name_norm"] + "|" + df["address_norm"] + "|" + df["zip_norm"]
    df["loose_key"] = df["name_norm"] + "|" + df["city_norm"]
    return df


def main():
        # Incremental ingestion from Supabase
    print("Pipeline starting...")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    # Load normalization rules
    try:
        rules = load_normalization_rules("normalization_rules.yaml")
    except FileNotFoundError as e:
        print(str(e))
        rules = {"substitutions": {}}

    # Read last run time from log
    last_run_time = get_last_run_time()

    # Fetch new practice records
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Warning: Missing SUPABASE_URL or SUPABASE_KEY")
        data_df = pd.DataFrame()
    else:
        print(f"Connected to Supabase at: {SUPABASE_URL}")
        data_df = fetch_practice_records(SUPABASE_URL, SUPABASE_KEY, last_run_time)

    # Process records if any
    if not data_df.empty:
        data_df = create_match_keys(data_df, rules)
        print(data_df[["name", "exact_key", "loose_key"]].head())
    else:
        print("No new records to process.")

    # Update last run time log
    update_last_run_time(datetime.utcnow().isoformat())
    print("Pipeline completed.")
    return

    print("Pipeline starting…")
    # Example environment variables for Supabase; adjust if using other sources
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Warning: Missing SUPABASE_URL or SUPABASE_KEY")
    else:
        print(f"Connected to Supabase at: {SUPABASE_URL}")

    # Load normalization rules
    try:
        rules = load_normalization_rules("normalization_rules.yaml")
    except FileNotFoundError as e:
        print(str(e))
        rules = {"substitutions": {}}

    # TODO: Load your actual data into a pandas DataFrame with
    # columns ['name', 'address', 'city', 'zip'].
    # For demonstration, we'll create a small example DataFrame.
    example_data = {
        "name": ["John Doe", "john  doe", "Jane Smith"],
        "address": ["123 Main St.", "123 main street", "456 Oak Rd"],
        "city": ["Chicago", "Chicago", "New York"],
        "zip": ["60606", "60606", "10001"]
    }
    df = pd.DataFrame(example_data)
    print("Loaded example data:")
    print(df)

    # Compute deterministic match keys
    df = create_match_keys(df, rules)
    print("Data with deterministic match keys:")
    print(df[["name", "exact_key", "loose_key"]])

    print("Pipeline completed.")


if __name__ == "__main__":
    main()
