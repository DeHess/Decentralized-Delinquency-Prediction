import pandas as pd
import itertools


df_baseline = pd.read_csv("Baseline_anomaly/combined_scores.csv")
df_manip = pd.read_csv("Data/improvement_best_manipulation_eval.csv")

bucket_names = ['not flagged', 'review', 'potential manipulation']


lower_thresholds = [0.2, 0.3]
upper_thresholds = [0.5, 0.7, 0.9]
anomaly_thresholds = [1.5, 1.75, 2.0, 2.25, 2.5]

results = []

def flag_bucket(prob, lower, upper):
    if prob <= lower:
        return "not flagged"
    elif prob <= upper:
        return "review"
    else:
        return "potential manipulation"

for lower, upper, anom_thr in itertools.product(lower_thresholds, upper_thresholds, anomaly_thresholds):
    if upper <= lower:
        continue

    n_points = len(df_baseline)

    buckets_baseline = df_baseline['predicted_probability'].apply(lambda x: flag_bucket(x, lower, upper))
    counts_base = buckets_baseline.value_counts().reindex(bucket_names, fill_value=0)
    perc_base = counts_base / n_points * 100


    buckets_manip_before = df_manip['prediction_before'].apply(lambda x: flag_bucket(x, lower, upper))
    counts_manip_before = buckets_manip_before.value_counts().reindex(bucket_names, fill_value=0)
    perc_manip_before = counts_manip_before / len(df_manip) * 100


    buckets_manip_after = df_manip['prediction_after'].apply(lambda x: flag_bucket(x, lower, upper))
    counts_manip_after = buckets_manip_after.value_counts().reindex(bucket_names, fill_value=0)
    perc_manip_after = counts_manip_after / len(df_manip) * 100


    in_pot_manip = (buckets_baseline == 'potential manipulation')
    not_in_pot_manip = ~in_pot_manip
    over_anom_thr = (df_baseline['average_score'] > anom_thr) & not_in_pot_manip
    pct_pot_manip = 100 * in_pot_manip.sum() / n_points if n_points else 0
    pct_over_anom = 100 * over_anom_thr.sum() / n_points if n_points else 0


    before = buckets_manip_before
    after = buckets_manip_after
    not_flagged = df_manip['anomaly_after'] <= anom_thr


    is_now_notflagged = (after == 'not flagged') & not_flagged
    pct_manip_now_notflagged = 100 * is_now_notflagged.sum() / len(df_manip) if len(df_manip) else 0

    is_potmanip_to_review = (before == 'potential manipulation') & (after == 'review') & not_flagged
    pct_manip_potmanip_to_review = 100 * is_potmanip_to_review.sum() / len(df_manip) if len(df_manip) else 0
    
    total = (is_now_notflagged.sum() + is_potmanip_to_review.sum()) / len(df_manip) * 100 if len(df_manip) else 0

    def bucket_summary(counts, perc):
        return " | ".join(
            f"{name}: {counts[name]} ({perc[name]:.1f}%)" for name in bucket_names
        )

    print(f"\n[Lower={lower}, Upper={upper}, AnomalyThr={anom_thr}]")
    print(f"  Baseline: {pct_pot_manip:.2f}% in 'potential manipulation' bucket")
    print(f"  Baseline: {pct_over_anom:.2f}% over anomaly threshold")
    print(f"  Manipulated: {total:.2f}% improved bucket without being noticed")
    

    results.append({
        'lower_threshold': lower,
        'upper_threshold': upper,
        'anomaly_threshold': anom_thr,
        'n_baseline': n_points,
        'bucket_base_not_flagged': counts_base['not flagged'],
        'bucket_base_review': counts_base['review'],
        'bucket_base_potential_manipulation': counts_base['potential manipulation'],
        'pct_base_not_flagged': perc_base['not flagged'],
        'pct_base_review': perc_base['review'],
        'pct_base_potential_manipulation': perc_base['potential manipulation'],
        'n_manip': len(df_manip),
        'bucket_manip_before_not_flagged': counts_manip_before['not flagged'],
        'bucket_manip_before_review': counts_manip_before['review'],
        'bucket_manip_before_potential_manipulation': counts_manip_before['potential manipulation'],
        'pct_manip_before_not_flagged': perc_manip_before['not flagged'],
        'pct_manip_before_review': perc_manip_before['review'],
        'pct_manip_before_potential_manipulation': perc_manip_before['potential manipulation'],
        'bucket_manip_after_not_flagged': counts_manip_after['not flagged'],
        'bucket_manip_after_review': counts_manip_after['review'],
        'bucket_manip_after_potential_manipulation': counts_manip_after['potential manipulation'],
        'pct_manip_after_not_flagged': perc_manip_after['not flagged'],
        'pct_manip_after_review': perc_manip_after['review'],
        'pct_manip_after_potential_manipulation': perc_manip_after['potential manipulation'],
        'pct_baseline_potential_manip': pct_pot_manip,
        'pct_baseline_over_anom_thr': pct_over_anom,
        'pct_manip_now_notflagged': pct_manip_now_notflagged,
        'pct_manip_potmanip_to_review': pct_manip_potmanip_to_review,
    })


pd.DataFrame(results).to_csv("experiment_combined_results.csv", index=False)
print("\All results saved to experiment_combined_results.csv")
