import matplotlib.pyplot as plt
import os
import numpy as np

transitions = [
    "review → not flagged",
    "review → review",
    "potential manipulation → not flagged",
    "potential manipulation → review",
    "potential manipulation → potential manipulation"
]
counts = [460, 4766, 38, 1541, 5195]
percent_caught = [81.1, 53.6, 100.0, 77.0, 58.1]


caught = [int(round(c/100*x)) for x, c in zip(counts, percent_caught)]
not_caught = [x - y for x, y in zip(counts, caught)]



anomaly_threshold = 1.75
rows_with_anomaly = sum(caught)
total_rows = sum(counts)
percent_anomaly = (rows_with_anomaly / total_rows) * 100



improved_transitions_indices = [2, 3, 0] 
improved_caught = sum(caught[i] for i in improved_transitions_indices)
improved_total = sum(counts[i] for i in improved_transitions_indices)
percent_improved_caught = (improved_caught / improved_total) * 100

print("Percent of improved transitions caught:", percent_improved_caught)



print("percent oof anomaly score", percent_anomaly)


caught_color = "#44789C"
not_caught_color = "#FDB97E"

os.makedirs("plots", exist_ok=True)
plt.figure(figsize=(10, 5))
y = np.arange(len(transitions))

bars_caught = plt.barh(y, caught, color=caught_color, edgecolor='black', label='Caught')
bars_not_caught = plt.barh(y, not_caught, left=caught, color=not_caught_color, edgecolor='black', label='Not caught')


for i, (caught_val, not_caught_val, total, pct) in enumerate(zip(caught, not_caught, counts, percent_caught)):

    if caught_val > 80:
        plt.text(caught_val / 2, i, f"{pct:.0f}%", va='center', ha='center', color='white', fontweight='bold')
        plt.text(caught_val + not_caught_val + 20, i, str(total), va='center', ha='left', color='black')
    else:
        plt.text(caught_val + 10, i + 0.2, f"{pct:.0f}%", va='bottom', ha='left', color='black', fontweight='bold')
        plt.text(caught_val + 10, i - 0.2, str(total), va='top', ha='left', color='black')

plt.yticks(y, transitions)
plt.xlabel("Count")
plt.title("Transition Counts by Bucket with 'Caught' Percentage (threshold = 1.75)")
plt.tight_layout()
plt.legend(loc="lower right")
plt.savefig("plots/transition_counts_caught_stacked.png")
plt.close()

print("Plot saved as plots/transition_counts_caught_stacked_v3.png")
