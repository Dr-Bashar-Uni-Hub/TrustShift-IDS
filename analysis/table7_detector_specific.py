"""Manuscript Table 7 and Supplementary S19: transferred XGBoost states vs detector-specific monitors
for the neural detectors (binary; orderings 1, 7, 21). Output: results/derived/table7_detector_specific.csv"""
import pandas as pd
from paths import P, DERIVED
EPS = 0.01; SEEDS = [1, 7, 21]
cf = pd.read_csv(P("WP2_V11_all_threshold_window_counterfactuals.csv")); mon = pd.read_csv(P("WP2_V9_label_free_monitor_windows.csv"))
st = pd.read_csv(P("V2_STEP_13C_MULTI_SEED_LABEL_FREE_MONITORING_WINDOWS.csv"))[["deployment_order_seed", "global_window_id", "stage_name", "primary_shift_evidence_state"]]
st.columns = ["seed", "window", "stage", "xgb_state"]; st["xgb_state"] = st.xgb_state.str.lower()
def summ(x):
    v = (x.acc_n > 0) & (x.acc_err / x.acc_n.clip(lower=1) > EPS); c = x[x.stage.str.startswith("clean")]
    return dict(viol=int(v.sum()), cov=x.acc_n.sum()/x.n.sum(), clean_cov=c.acc_n.sum()/c.n.sum(),
                risk=x.acc_err.sum()/x.acc_n.sum(), att_def=x.deferred_attack.sum()/x.n_attack.sum())
rows = []
for det in ["MLP", "FTTransformer"]:
    c = cf[(cf.detector == det) & cf.seed.isin(SEEDS)].merge(st, on=["seed", "window"])
    c = c.merge(mon[mon.detector == det][["seed", "window", "state"]].rename(columns={"state": "ds_state"}), on=["seed", "window"])
    for k, v in {"Fixed": c[c.state == "normal"], "Adaptive, transferred XGBoost states": c[c.state == c.xgb_state],
                 "Adaptive, detector-specific states": c[c.state == c.ds_state], "Static Severe": c[c.state == "severe"]}.items():
        rows.append(dict(detector=det, policy=k, windows=len(v), **summ(v)))
    cl = mon[(mon.detector == det) & mon.seed.isin(SEEDS)].merge(st, on=["seed", "window"]); cl = cl[cl.stage.str.startswith("clean")]
    print(f"{det}: Severe on {int((cl.state=='severe').sum())} of {len(cl)} clean windows (XGBoost monitor: {int((cl.xgb_state=='severe').sum())})")
T = pd.DataFrame(rows); T.to_csv(DERIVED/"table7_detector_specific.csv", index=False); print(T.round(4).to_string(index=False))
