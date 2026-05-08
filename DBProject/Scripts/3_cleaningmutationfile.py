import pandas as pd
# Load file (tab-delimited)
df = pd.read_csv("/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mutations.txt", sep="\t", comment="#")

# Keep only desired columns
cols = [
    "Hugo_Symbol",
    "Tumor_Sample_Barcode",
    "Chromosome",
    "Start_Position",
    "End_Position",
    "Variant_Classification",
    "Variant_Type",
    "IMPACT",
    "Reference_Allele",
    "Tumor_Seq_Allele2",
    "HGVSp",
    "SIFT",
    "PolyPhen"
]

df = df[cols]

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Save as CSV (comma-separated)
df.to_csv("/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mutations_cleaned.csv", index=False)