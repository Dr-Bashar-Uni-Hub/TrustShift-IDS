# Frozen models

| File | Size (MB) | SHA-256 |
|---|---|---|
| `TrustShift_IDS_XGBoost_temperature_scaling_parameters.json` | 0.001 | `912160af5158dd8493c988737e2938ff2c3774798560ba68401d8b6e1349e3f7` |
| `XGB_binary_seed42.joblib` | 0.500 | `3dd240fe174f07cb62ead9e2d0bb321b46650c137285ea5b395451ca5a1f52ed` |
| `XGB_multiclass_seed42.joblib` | 2.016 | `6ee55e581a0158cf2436f0b97ca66cf0e2fbedd8b4d4a38e19158cf1878c8a0e` |

Load with `joblib.load` under XGBoost 3.4.1. Apply scalar temperature scaling: `softmax(log(clip(p, 1e-15, 1)) / T)`, with T = 0.9744155346869672 (binary) and 1.1709901909513676 (multiclass).
Inference on the CPU reproduces the frozen predictions bit for bit.
