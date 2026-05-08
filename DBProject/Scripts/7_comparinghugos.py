import pandas as pd

MUTATION_FILE = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mutations_cleaned.csv"
EXPRESSION_FILE = "/Users/nicksmacbookair/Documents/Database Project/lusc_tcga_pub/data_mrna_seq_rpkm.txt"
OUTPUT_REPORT = "/Users/nicksmacbookair/Documents/Database Project/hugo_symbol_comparison.txt"

def normalize_symbol(series):
    return (
        series.dropna()
        .astype(str)
        .str.strip()
        .str.upper()
    )

# Load files
mut_df = pd.read_csv(MUTATION_FILE)
expr_df = pd.read_csv(EXPRESSION_FILE, sep="\t")

# Validate required columns
if "hugo_symbol" not in [c.lower() for c in mut_df.columns]:
    raise ValueError("Mutation file must contain a 'hugo_symbol' column")

if "Hugo_Symbol" not in expr_df.columns:
    raise ValueError("Expression file must contain a 'Hugo_Symbol' column")

# Get actual mutation column name preserving case
mut_hugo_col = next(c for c in mut_df.columns if c.lower() == "hugo_symbol")

# Normalize symbols
mutation_symbols = set(normalize_symbol(mut_df[mut_hugo_col]))
expression_symbols = set(normalize_symbol(expr_df["Hugo_Symbol"]))

# Compare
in_mut_not_expr = sorted(mutation_symbols - expression_symbols)
in_expr_not_mut = sorted(expression_symbols - mutation_symbols)
in_both = sorted(mutation_symbols & expression_symbols)

# Write report
with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
    f.write("HUGO SYMBOL COMPARISON REPORT\n")
    f.write("=" * 40 + "\n\n")

    f.write(f"Mutation file unique symbols: {len(mutation_symbols)}\n")
    f.write(f"Expression file unique symbols: {len(expression_symbols)}\n")
    f.write(f"Symbols in both files: {len(in_both)}\n")
    f.write(f"Symbols only in mutation file: {len(in_mut_not_expr)}\n")
    f.write(f"Symbols only in expression file: {len(in_expr_not_mut)}\n\n")

    f.write("SYMBOLS IN MUTATION FILE BUT NOT IN EXPRESSION FILE\n")
    f.write("-" * 55 + "\n")
    if in_mut_not_expr:
        for symbol in in_mut_not_expr:
            f.write(symbol + "\n")
    else:
        f.write("None\n")

    f.write("\nSYMBOLS IN EXPRESSION FILE BUT NOT IN MUTATION FILE\n")
    f.write("-" * 55 + "\n")
    if in_expr_not_mut:
        for symbol in in_expr_not_mut:
            f.write(symbol + "\n")
    else:
        f.write("None\n")

print(f"Done. Report written to: {OUTPUT_REPORT}")
print(f"Mutation file unique symbols: {len(mutation_symbols)}")
print(f"Expression file unique symbols: {len(expression_symbols)}")
print(f"Symbols in both files: {len(in_both)}")
print(f"Only in mutation file: {len(in_mut_not_expr)}")
print(f"Only in expression file: {len(in_expr_not_mut)}")