import pandas as pd
import math

patients_csv = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_clinical_patient_cleaned.csv"
samples_csv = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_clinical_sample_cleaned.csv"
sql_file = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/insert_pt_spl.sql"

patients_df = pd.read_csv(patients_csv)
samples_df = pd.read_csv(samples_csv)

def sql_escape(value):
    if pd.isna(value):
        return "NULL"
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, float):
        if math.isnan(value):
            return "NULL"
        # avoid writing 67.0 for integer-like values
        if value.is_integer():
            return str(int(value))
        return str(value)
    return str(value)

# Merge sample rows with patient clinical fields
merged_df = samples_df.merge(
    patients_df[
        [
            "patient_id",
            "age",
            "t_stage",
            "n_stage",
            "m_stage"
        ]
    ],
    on="patient_id",
    how="left"
)

with open(sql_file, "w", encoding="utf-8") as f:
    f.write("-- Generated SQL inserts\n\n")
    f.write("START TRANSACTION;\n\n")

    # Patients
    f.write("-- Insert into Patients\n")
    for _, row in patients_df.iterrows():
        f.write(f"""INSERT INTO Patients (
    PATIENT_ID,
    SEX,
    SMOKING_HISTORY,
    SMOKING_PACK_YEARS
) VALUES (
    {sql_escape(row["patient_id"])},
    {sql_escape(row["sex"])},
    {sql_escape(row["smoking_status"])},
    {sql_escape(row["pack_years"])}
);\n""")

    f.write("\n-- Insert into Samples\n")
    for _, row in merged_df.iterrows():
        f.write(f"""INSERT INTO Samples (
    SAMPLE_ID,
    PATIENT_ID,
    AGE,
    NONSENSE_MUTATION,
    NONSILENT_PER_MB,
    TMB_NONSYNONYMOUS,
    CLIN_T_STAGE,
    CLIN_N_STAGE,
    CLIN_M_STAGE
) VALUES (
    {sql_escape(row["sample_id"])},
    {sql_escape(row["patient_id"])},
    {sql_escape(row["age"])},
    {sql_escape(row["nonsense_mutation"])},
    {sql_escape(row["nonsilent_per_mb"])},
    {sql_escape(row["tmb_nonsynonymous"])},
    {sql_escape(row["t_stage"])},
    {sql_escape(row["n_stage"])},
    {sql_escape(row["m_stage"])}
);\n""")

    f.write("\nCOMMIT;\n")

print(f"SQL file generated: {sql_file}")