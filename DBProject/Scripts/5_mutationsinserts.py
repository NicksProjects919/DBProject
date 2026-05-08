import pandas as pd

INPUT_CSV = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mutations_cleaned.csv"
OUTPUT_SQL = "/Users/nicksmacbookair/Documents/Database Project/mutations_inserts.sql"

df = pd.read_csv(INPUT_CSV)
df.columns = [c.strip().lower() for c in df.columns]

required_cols = [
    "hugo_symbol",
    "tumor_sample_barcode",
    "chromosome",
    "start_position",
    "end_position",
    "variant_classification",
    "variant_type",
    "impact",
    "reference_allele",
    "tumor_seq_allele2",
    "hgvsp",
    "sift",
    "polyphen",
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

def sql_str(val):
    if pd.isna(val) or str(val).strip() == "":
        return "NULL"
    return "'" + str(val).replace("\\", "\\\\").replace("'", "''") + "'"

def sql_num(val):
    if pd.isna(val) or str(val).strip() == "":
        return "NULL"
    try:
        f = float(val)
        return str(int(f)) if f.is_integer() else str(f)
    except Exception:
        return "NULL"

genes_seen = set()
sample_mut_seen = set()

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
    f.write("-- Auto-generated SQL inserts for data_mutations_cleaned.csv\n")
    f.write("-- Assumes Variant has a UNIQUE constraint on:\n")
    f.write("-- (GENE_ID, Chromosome, Start_Position, End_Position, Reference_Allele, Tumor_Seq_Allele2, Variant_Type)\n\n")

    for _, row in df.iterrows():
        hugo_symbol_raw = None if pd.isna(row["hugo_symbol"]) else str(row["hugo_symbol"]).strip()
        sample_raw = None if pd.isna(row["tumor_sample_barcode"]) else str(row["tumor_sample_barcode"]).strip()
        chromosome_raw = None if pd.isna(row["chromosome"]) else str(row["chromosome"]).strip()
        start_raw = None if pd.isna(row["start_position"]) else str(row["start_position"]).strip()
        end_raw = None if pd.isna(row["end_position"]) else str(row["end_position"]).strip()
        ref_raw = None if pd.isna(row["reference_allele"]) else str(row["reference_allele"]).strip()
        alt_raw = None if pd.isna(row["tumor_seq_allele2"]) else str(row["tumor_seq_allele2"]).strip()
        variant_type_raw = None if pd.isna(row["variant_type"]) else str(row["variant_type"]).strip()
        variant_class_raw = None if pd.isna(row["variant_classification"]) else str(row["variant_classification"]).strip()
        impact_raw = None if pd.isna(row["impact"]) else str(row["impact"]).strip()

        hugo_symbol = sql_str(row["hugo_symbol"])
        tumor_sample_barcode = sql_str(row["tumor_sample_barcode"])
        chromosome = sql_str(row["chromosome"])
        start_position = sql_num(row["start_position"])
        end_position = sql_num(row["end_position"])
        variant_classification = sql_str(row["variant_classification"])
        variant_type = sql_str(row["variant_type"])
        impact = sql_str(row["impact"])
        reference_allele = sql_str(row["reference_allele"])
        tumor_seq_allele2 = sql_str(row["tumor_seq_allele2"])
        hgvsp = sql_str(row["hgvsp"])
        sift = sql_str(row["sift"])
        polyphen = sql_str(row["polyphen"])

        gene_key = hugo_symbol_raw
        sample_mut_key = (
            sample_raw,
            hugo_symbol_raw,
            chromosome_raw,
            start_raw,
            end_raw,
            ref_raw,
            alt_raw,
            variant_type_raw,
            variant_class_raw,
            impact_raw,
        )

        f.write("-- ----------------------------------------\n")
        f.write(f"-- {hugo_symbol_raw} | {sample_raw}\n")

        if gene_key not in genes_seen:
            genes_seen.add(gene_key)
            f.write(f"INSERT IGNORE INTO Genes (hugo_symbol) VALUES ({hugo_symbol});\n")

        f.write(f"SET @gene_id = (SELECT GENE_ID FROM Genes WHERE hugo_symbol = {hugo_symbol});\n")

        f.write(
            "INSERT IGNORE INTO Variant "
            "(GENE_ID, Chromosome, Start_Position, End_Position, "
            "Reference_Allele, Tumor_Seq_Allele2, Variant_Type) "
            f"VALUES (@gene_id, {chromosome}, {start_position}, {end_position}, "
            f"{reference_allele}, {tumor_seq_allele2}, {variant_type});\n"
        )

        f.write(
            "SET @variant_id = ("
            "SELECT VARIANT_ID FROM Variant "
            f"WHERE GENE_ID = @gene_id "
            f"AND ((Chromosome = {chromosome}) OR (Chromosome IS NULL AND {chromosome} IS NULL)) "
            f"AND ((Start_Position = {start_position}) OR (Start_Position IS NULL AND {start_position} IS NULL)) "
            f"AND ((End_Position = {end_position}) OR (End_Position IS NULL AND {end_position} IS NULL)) "
            f"AND ((Reference_Allele = {reference_allele}) OR (Reference_Allele IS NULL AND {reference_allele} IS NULL)) "
            f"AND ((Tumor_Seq_Allele2 = {tumor_seq_allele2}) OR (Tumor_Seq_Allele2 IS NULL AND {tumor_seq_allele2} IS NULL)) "
            f"AND ((Variant_Type = {variant_type}) OR (Variant_Type IS NULL AND {variant_type} IS NULL)) "
            "LIMIT 1"
            ");\n"
        )

        f.write(
            "INSERT IGNORE INTO Variant_Annotation "
            "(VARIANT_ID, HGCSp_Short, SIFT, PolyPhen) "
            f"VALUES (@variant_id, {hgvsp}, {sift}, {polyphen});\n"
        )

        if sample_mut_key not in sample_mut_seen:
            sample_mut_seen.add(sample_mut_key)
            f.write(
                "INSERT INTO Sample_Mutation "
                "(SAMPLE_ID, VARIANT_ID, Variant_Classification, IMPACT) "
                f"VALUES ({tumor_sample_barcode}, @variant_id, {variant_classification}, {impact});\n"
            )

        f.write("\n")

print(f"Done. SQL file written to: {OUTPUT_SQL}")