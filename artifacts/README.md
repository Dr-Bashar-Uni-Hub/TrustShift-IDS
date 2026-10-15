# Frozen artifacts

| File | Size (MB) | SHA-256 | Purpose |
|---|---|---|---|
| `TrustShift_IDS_STEP_10_FROZEN_SELECTIVE_POLICY.json` | 0.004 | `16cce770420e2dfc…` | Fixed (Normal) selective policy, Step 10R |
| `V2_FROZEN_V1_PROVENANCE.json` | 0.001 | `7103cd7f6dd562f2…` | V1 to V2 provenance and anchor values |
| `V2_FULL_TRAINING_FEATURE_MEDIANS_68F.npy` | 0.001 | `44fa27a24dcfbb92…` | Training medians used by the S3/S4 perturbations |
| `V2_S3_corruption_mask_05.npy` | 1.237 | `9a3c04ebe288c8b4…` | S3 per-flow feature mask (indices into the 68-feature order) |
| `V2_S3_corruption_mask_10.npy` | 2.885 | `f22b410a51faf95f…` | S3 per-flow feature mask (indices into the 68-feature order) |
| `V2_S3_corruption_mask_20.npy` | 5.771 | `b06ee6de1ff0cf0d…` | S3 per-flow feature mask (indices into the 68-feature order) |
| `V2_S3_corruption_mask_30.npy` | 8.244 | `f46a37dbd077ec13…` | S3 per-flow feature mask (indices into the 68-feature order) |
| `V2_STEP_6D_S3_CORRUPTION_REALIZATION.json` | 0.004 | `14be8c959d80a917…` | S3 protocol and 68-feature order |

`metadata/` holds the frozen protocol and state records of every V1 step (Steps 4–12.9). The key records are:
- `TrustShift_IDS_STEP_4_FROZEN_SUMMARY.json`: the group-disjoint split. Groups are identical 76-feature vectors (2,233,419 groups), and there is zero cross-partition duplicate leakage.
- `TrustShift_IDS_STEP_9_RISK_ESTIMATOR_SELECTION.json`, `..._STEP_10_FROZEN_SELECTIVE_POLICY.json` and `..._STEP_11_IID_EVALUATION_STATE.json`: the group-aware correction (9R/10R/11R) and the IID history.
- `TrustShift_IDS_STEP_12_1_EXTERNAL_FOUNDATION.json`: the CSE-CIC-IDS2018 harmonisation and the overlap audit (0.95% of external flows share a 68-feature hash with CICIDS2017).
