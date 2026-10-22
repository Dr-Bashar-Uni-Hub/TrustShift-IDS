"""Regenerates manuscript Tables 6, 7 and 8, the retention analysis (Supplementary S18) and Supplementary S12-S17
from the exported window-level results. CPU only, no raw data. Outputs go to results/derived/."""
import json
import numpy as np, pandas as pd
from paths import P, DERIVED
EPS = 0.01
def rk(d): return np.where(d.acc_n > 0, d.acc_err / d.acc_n.clip(lower=1), np.nan)
def summ(x, clean=None):
    r = dict(viol=int(((x.acc_n > 0) & (rk(x) > EPS)).sum()), cov=x.acc_n.sum()/x.n.sum(), risk=x.acc_err.sum()/max(x.acc_n.sum(), 1),
             att_def=1-x.acc_attack.sum()/x.n_attack.sum(), det=(x.acc_attack.sum()-x.acc_missed_attack.sum())/x.n_attack.sum(),
             fa=x.acc_false_alarm.sum()/max(x.acc_benign.sum(), 1))
    if clean is not None:
        c = x[clean(x)]; r["clean_cov"] = c.acc_n.sum()/c.n.sum()
    return r
def state(v, b): return np.where(v <= b[0], "normal", np.where(v <= b[1], "elevated", "severe"))
MAP = {"normal": "fixed", "elevated": "elevated", "severe": "severe"}
def oracle(d, keys):
    x = d[d.thr_name.isin(["fixed", "elevated", "severe"])].copy(); x["o"] = x.thr_name.map({"fixed": 0, "elevated": 1, "severe": 2})
    x["v"] = (x.acc_n > 0) & (rk(x) > EPS); ok = x[~x.v].sort_values("o").groupby(keys).head(1)
    miss = x[x.o == 2].merge(ok[keys].assign(k=1), on=keys, how="left"); miss = miss[miss.k.isna()].drop(columns="k")
    return pd.concat([ok, miss])
def policies(d, keys, atc_b, state_col=None):
    pol = {k: d[d.thr_name == t] for k, t in [("Fixed", "fixed"), ("Static Elevated", "elevated"), ("Static Severe", "severe"), ("Static 97.5%", "cov_0.975")]}
    if state_col:
        st = d[d.thr_name == "fixed"][keys + [state_col]].copy(); st["thr_name"] = st[state_col].map(MAP)
        pol["Adaptive (TrustShift states)"] = d.drop(columns=state_col).merge(st[keys + ["thr_name"]], on=keys + ["thr_name"])
    a = d[d.thr_name == "fixed"][keys + ["atc_est"]].copy(); a["thr_name"] = pd.Series(state(a.atc_est.values, atc_b)).map(MAP).values
    pol["ATC monitor"] = d.merge(a[keys + ["thr_name"]], on=keys + ["thr_name"]); pol["Oracle"] = oracle(d, keys)
    return pol
# ---- Table 6: neural detectors (CICIDS2017)
N1 = json.load(open(P("N1_neural_calibration_and_thresholds.json")))
n2 = pd.read_csv(P("N2_neural_stream_window_outcomes.csv.gz")); n2 = n2[n2.seed != 42]
n3 = pd.read_csv(P("N3_neural_external_window_outcomes.csv.gz"))
rows = []
for det in ["MLP", "FTTransformer"]:
    for k, v in policies(n2[n2.detector == det], ["seed", "window_id"], N1[det]["atc_boundaries"], "xgb_sss_state").items():
        rows.append(dict(detector=det, setting="sequences", policy=k, **summ(v, lambda x: x.stage_name.str.startswith("clean"))))
    for t in ["fixed", "elevated", "severe", "cov_0.500"]:
        rows.append(dict(detector=det, setting="CSE-CIC-IDS2018", policy=t, **summ(n3[(n3.detector == det) & (n3.thr_name == t)])))
T6 = pd.DataFrame(rows); T6.to_csv(DERIVED/"table6_neural.csv", index=False)
# ---- Table 7: NetFlow replication
F1 = json.load(open(P("F1_calibration_thresholds.json")))
f2 = pd.read_csv(P("F2_sequence_window_outcomes.csv.gz")); f3 = pd.read_csv(P("F3_external_window_outcomes.csv.gz"))
f2 = f2.rename(columns={"stage": "stage_name"}); rows = []
for det in ["XGBoost", "MLP"]:
    for k, v in policies(f2[f2.detector == det], ["seed", "window_id"], F1[det]["atc_bounds"]).items():
        rows.append(dict(detector=det, setting="sequences", policy=k, **summ(v, lambda x: x.stage_name.str.startswith("clean"))))
    for t in ["fixed", "elevated", "severe"]:
        rows.append(dict(detector=det, setting="NF-CSE-CIC-IDS2018-v2", policy=t, **summ(f3[(f3.detector == det) & (f3.thr_name == t)])))
T7 = pd.DataFrame(rows); T7.to_csv(DERIVED/"table7_netflow.csv", index=False)
# ---- Table 8 and S18: asymmetric abstention with exact accept-all counts
exec(open(__file__.replace("tables_6_7_8.py", "remedy_exact.py")).read())
h1 = pd.read_csv(P("H1_cic_xgboost_acceptall.csv")); h2 = pd.read_csv(P("H2_cic_neural_acceptall.csv"))
h3 = pd.read_csv(P("H3_netflow_sequences_acceptall.csv")); h4 = pd.read_csv(P("H4_netflow_external_acceptall.csv"))
cicN = {"fixed": "state_normal", "elevated": "state_elevated", "severe": "state_severe"}; nN = {"fixed": "fixed", "elevated": "elevated", "severe": "severe"}
res = {}; ret = []
ms = pd.read_csv(P("R2_multiseed_window_threshold_outcomes.csv.gz")); d = ms[(ms.seed != 42) & (ms.task == "binary")]
aa = h1[(h1.dataset == "CIC_sequences") & (h1.seed != 42)]
res["CIC XGBoost sequences"] = evaluate(d, aa, ["seed", "window_id"], cicN, "state", {"normal": "state_normal", "elevated": "state_elevated", "severe": "state_severe"})
cl = d[d.stage_name.str.startswith("clean")]; aac = aa.merge(cl[["seed", "window_id"]].drop_duplicates(), on=["seed", "window_id"])
TH = lambda c: ([f"state_{x}" for x in ["elevated", "severe"]] if c else ["elevated", "severe"]) + ["cov_0.900", "cov_0.700", "cov_0.500"]
ret += retention(cl, aac, ["seed", "window_id"], TH(True), "CICIDS2017 clean windows XGBoost (reference)")
e = pd.read_csv(P("R7_S1_binary_security_window_outcomes.csv.gz")); aa = h1[h1.dataset == "CIC_external"]
res["CIC XGBoost external"] = evaluate(e, aa, ["window_id"], cicN); ret += retention(e, aa, ["window_id"], TH(True), "CSE-CIC-IDS2018 XGBoost")
for det in ["MLP", "FTTransformer"]:
    aa = h2[(h2.dataset == "CIC_sequences") & (h2.detector == det) & (h2.seed != 42)]
    res[f"CIC {det} sequences"] = evaluate(n2[n2.detector == det], aa, ["seed", "window_id"], nN, "xgb_sss_state", MAP)
    aa = h2[(h2.dataset == "CIC_external") & (h2.detector == det)]
    res[f"CIC {det} external"] = evaluate(n3[n3.detector == det], aa, ["window_id"], nN); ret += retention(n3[n3.detector == det], aa, ["window_id"], TH(False), f"CSE-CIC-IDS2018 {det}")
g = pd.read_csv(P("G1_ToN_window_outcomes.csv.gz")); f2o = pd.read_csv(P("F2_sequence_window_outcomes.csv.gz"))
def atcst(df, det): x = df.copy(); x["atc_state"] = state(x.atc_est.values, F1[det]["atc_bounds"]); return x
for det in ["XGBoost", "MLP"]:
    res[f"NetFlow {det} sequences"] = evaluate(atcst(f2o[f2o.detector == det], det), h3[h3.detector == det], ["seed", "window_id"], nN, "atc_state", MAP)
    aa = h4[(h4.dataset == "NetFlow_external") & (h4.detector == det)]
    res[f"NetFlow {det} external"] = evaluate(atcst(f3[f3.detector == det], det), aa, ["window_id"], nN, "atc_state", MAP)
    ret += retention(f3[f3.detector == det], aa, ["window_id"], TH(False), f"NF-CSE-CIC-IDS2018-v2 {det}")
    aa = h4[(h4.dataset == "ToN_confirmation") & (h4.detector == det)]
    res[f"ToN {det}"] = evaluate(atcst(g[g.detector == det], det), aa, ["window_id"], nN, "atc_state", MAP)
    ret += retention(g[g.detector == det], aa, ["window_id"], TH(False), f"NF-ToN-IoT-v2 {det}")
T8 = pd.concat([v.assign(setting=k).rename_axis("policy").reset_index() for k, v in res.items()])
T8.to_csv(DERIVED/"remedy_exact_results.csv", index=False); pd.DataFrame(ret).to_csv(DERIVED/"retention_exact.csv", index=False)
print("Table 8 (BCDR, violations):")
print(T8[T8.policy.isin(["SYM Severe", "ASY Severe"])][["setting", "policy", "BCDR", "viol"]].round(4).to_string(index=False))
