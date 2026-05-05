import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = "generated"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv("fire_sizes2.csv")
sizes = df["size"].values
sizes = sizes[sizes > 0]

# 1. zwykły histogram
plt.figure(figsize=(11, 7))
plt.hist(sizes, bins=60, edgecolor="black")
plt.xlabel("Fire size")
plt.ylabel("Count")
plt.title("Histogram of fire sizes")
plt.grid(alpha=0.3)
plt.savefig(os.path.join(OUTPUT_DIR, "histogram_fire_sizes.png"), dpi=300, bbox_inches="tight")
plt.close()

# 2. histogram log-log
bins = np.logspace(np.log10(sizes.min()), np.log10(sizes.max()), 60)

plt.figure(figsize=(11, 7))
plt.hist(sizes, bins=bins, edgecolor="black")
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Fire size (log scale)")
plt.ylabel("Count (log scale)")
plt.title("Fire size distribution (log-log histogram)")
plt.grid(alpha=0.3, which="both")
plt.savefig(os.path.join(OUTPUT_DIR, "histogram_loglog_fire_sizes.png"), dpi=300, bbox_inches="tight")
plt.close()

# # 3. CCDF
# sorted_sizes = np.sort(sizes)
# unique_sizes = np.unique(sorted_sizes)
# ccdf = np.array([np.sum(sorted_sizes >= x) / len(sorted_sizes) for x in unique_sizes])

# plt.figure(figsize=(8, 5))
# plt.loglog(unique_sizes, ccdf, marker="o", linestyle="none")
# plt.xlabel("Fire size")
# plt.ylabel("P(X ≥ x)")
# plt.title("CCDF of fire sizes (log-log)")
# plt.grid(alpha=0.3, which="both")
# plt.savefig(os.path.join(OUTPUT_DIR, "ccdf_fire_sizes.png"), dpi=300, bbox_inches="tight")
# plt.close()

print("Wykresy zapisane do plików PNG.")