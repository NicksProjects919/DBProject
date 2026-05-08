import pandas as pd

MUTATION_FILE = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mutations_cleaned.csv"
EXPRESSION_FILE = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mrna_seq_rpkm.txt"
OUTPUT_FILE = "/Users/nicksmacbookair/Documents/Database Project/expression_inserts_filtered.sql"

mut_df = pd.read_csv(MUTATION_FILE)
expr_df = pd.read_csv(EXPRESSION_FILE, sep="\t")

mut_df.columns = [c.strip().lower() for c in mut_df.columns]
expr_df.columns = [c.strip() for c in expr_df.columns]

if "hugo_symbol" not in mut_df.columns:
    raise ValueError("Mutation file must contain 'hugo_symbol'")

if "Hugo_Symbol" not in expr_df.columns:
    raise ValueError("Expression file must contain 'Hugo_Symbol'")

mutation_genes = set(
    mut_df["hugo_symbol"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
)

expr_df["Hugo_Symbol"] = (
    expr_df["Hugo_Symbol"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
)

expr_df = expr_df[expr_df["Hugo_Symbol"].isin(mutation_genes)]

sample_columns = [c for c in expr_df.columns if c not in ["Hugo_Symbol", "Entrez_Gene_Id"]]

def sql_str(val):
    if pd.isna(val) or str(val).strip() == "":
        return "NULL"
    return "'" + str(val).replace("\\", "\\\\").replace("'", "''") + "'"

def sql_num(val):
    if pd.isna(val) or str(val).strip() == "":
        return "NULL"
    return str(float(val))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("-- Expression inserts filtered to genes present in mutation file\n")
    f.write("-- Batched: one INSERT per gene\n\n")

    for _, row in expr_df.iterrows():
        gene = row["Hugo_Symbol"]
        gene_sql = sql_str(gene)

        value_rows = []

        for sample_col in sample_columns:
            value = row[sample_col]

            if pd.isna(value):
                continue

            sample_sql = sql_str(sample_col)
            value_sql = sql_num(value)
            value_rows.append(f"(@gene_id, {sample_sql}, {value_sql})")

        if not value_rows:
            continue

        f.write("-- ----------------------------------------\n")
        f.write(f"-- Gene: {gene}\n")
        f.write(f"SET @gene_id = (SELECT GENE_ID FROM Genes WHERE hugo_symbol = {gene_sql});\n")
        f.write("INSERT INTO Expression (GENE_ID, SAMPLE_ID, RPKM_VALUE)\n")
        f.write("VALUES\n")
        f.write(",\n".join(value_rows))
        f.write("\nON DUPLICATE KEY UPDATE RPKM_VALUE = VALUES(RPKM_VALUE);\n\n")

print(f"Done. SQL file written to: {OUTPUT_FILE}")
print(f"Genes kept: {expr_df['Hugo_Symbol'].nunique()}")
print(f"Total expression rows kept: {len(expr_df)}")