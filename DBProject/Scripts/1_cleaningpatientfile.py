import pandas as pd

# Load file and skip metadata rows that start with '#'
df = pd.read_csv("/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_clinical_patient.txt", sep="\t", comment="#")

# Standardize column names
df.columns = [
    "patient_id",
    "sex",
    "age",
    "t_stage",
    "n_stage",
    "m_stage",
    "smoking_status",
    "pack_years",
]

# Replace blank strings with missing values
df = df.replace(r"^\s*$", pd.NA, regex=True)

# Convert numeric columns
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["pack_years"] = pd.to_numeric(df["pack_years"], errors="coerce")

# Standardize sex
df["sex"] = df["sex"].map({"Male": "M", "Female": "F"})
df["sex"] = df["sex"].fillna("U")  # Unknown

# Normalize smoking status
smoking_map = {
    "Current smoker": "current",
    "Current reformed smoker for < or = 15 years": "former_recent",
    "Current reformed smoker for > 15 years": "former_long",
    "Lifelong Non-smoker": "never",
}
df["smoking_status"] = df["smoking_status"].map(smoking_map)
df["smoking_status"] = df["smoking_status"].fillna("unknown")

# Fill pack years for never smokers with 0
df.loc[df["smoking_status"] == "never", "pack_years"] = 0

# Fill missing numeric values (no row deletion)
df["age"] = df["age"].fillna(df["age"].median())
df["pack_years"] = df["pack_years"].fillna(df["pack_years"].median())

# Clean staging columns
df["m_stage"] = df["m_stage"].replace("MX", pd.NA)

# Simplify staging (T2a → T2, etc.)
df["t_stage"] = df["t_stage"].astype("string").str.extract(r"(T\d)", expand=False)
df["n_stage"] = df["n_stage"].astype("string").str.extract(r"(N\d)", expand=False)

# Fill missing staging values
df["t_stage"] = df["t_stage"].fillna("Unknown")
df["n_stage"] = df["n_stage"].fillna("Unknown")
df["m_stage"] = df["m_stage"].fillna("Unknown")

# Convert categorical columns
categorical_cols = ["sex", "smoking_status", "t_stage", "n_stage", "m_stage"]
for col in categorical_cols:
    df[col] = df[col].astype("category")

# Optional: inspect result
print(df.head())
print()
print(df.dtypes)
print()
print(df.isna().sum())

# Save cleaned dataset
df.to_csv("/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_clinical_patient_cleaned.csv", index=False)