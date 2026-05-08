import pandas as pd

# Read file (skip metadata rows starting with '#')
df = pd.read_csv("/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_clinical_sample.txt", sep="\t", comment="#")

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Keep only desired columns
cols = [
    "patient_id",
    "sample_id",
    "nonsense_mutation",
    "nonsilent_per_mb",
    "tmb_nonsynonymous"
]

df_clean = df[cols]

# Ensure numeric columns are floats
df_clean["nonsilent_per_mb"] = pd.to_numeric(df_clean["nonsilent_per_mb"], errors="coerce").astype(float)
df_clean["tmb_nonsynonymous"] = pd.to_numeric(df_clean["tmb_nonsynonymous"], errors="coerce").astype(float)

# Save as CSV (comma-separated)
df_clean.to_csv("/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_clinical_sample_cleaned.csv", index=False)