"""Asymmetric abstention and BCDR using exact accept-all attack verdicts (R7). Retention fractions with true no-abstention denominators."""
import pandas as pd, numpy as np
EPS = 0.01
def summarize_sym(T):
    acc = T.acc_n; v = (acc > 0) & (T.acc_err / acc.clip(lower=1) > EPS); det = T.acc_attack - T.acc_missed_attack
    return dict(viol=int(v.sum()), cov=acc.sum()/T.n.sum(), att_def=1-T.acc_attack.sum()/T.n_attack.sum(),
                det=det.sum()/T.n_attack.sum(), BCDR=det[~v].sum()/T.n_attack.sum(), fa=T.acc_false_alarm.sum()/max(T.acc_benign.sum(), 1))
def summarize_asy(T, AA):
    """T: threshold record per window; AA: accept-all counts per window (same index)."""
    TP, FA = AA.TP_all, AA.FA_all; miss = T.acc_missed_attack; bok = T.acc_benign - T.acc_false_alarm
    acc = TP + FA + miss + bok; err = FA + miss; v = (acc > 0) & (err / acc.clip(lower=1) > EPS)
    return dict(viol=int(v.sum()), cov=acc.sum()/T.n.sum(), att_def=1-(TP+miss).sum()/T.n_attack.sum(),
                det=TP.sum()/T.n_attack.sum(), BCDR=TP[~v].sum()/T.n_attack.sum(), fa=FA.sum()/max((FA+bok).sum(), 1))
def evaluate(df, aa, keys, names, state_col=None, state_map=None):
    """names: dict fixed/elevated/severe -> thr_name. aa: accept-all frame with keys."""
    AA = aa.set_index(keys)
    R = {}
    F = df[df.thr_name == names['fixed']].set_index(keys).loc[AA.index]
    # no abstention, exact: accept everything
    acc = AA.n; err = (AA.n_attack - AA.TP_all) + AA.FA_all; v = err / acc > EPS
    R['No abstention (accept all)'] = dict(viol=int(v.sum()), cov=1.0, att_def=0.0, det=AA.TP_all.sum()/AA.n_attack.sum(),
                                           BCDR=AA.TP_all[~v].sum()/AA.n_attack.sum(), fa=AA.FA_all.sum()/(AA.n-AA.n_attack).sum())
    R['Fixed threshold'] = summarize_sym(F)
    for lab in ['elevated', 'severe']:
        T = df[df.thr_name == names[lab]].set_index(keys).loc[AA.index]
        R['SYM ' + lab.capitalize()] = summarize_sym(T); R['ASY ' + lab.capitalize()] = summarize_asy(T, AA)
    if state_col is not None:
        st = df[df.thr_name == names['fixed']][keys + [state_col]].copy(); st['thr_name'] = st[state_col].map(state_map)
        T = df.drop(columns=[state_col]).merge(st[keys + ['thr_name']], on=keys + ['thr_name']).set_index(keys).loc[AA.index]
        R['SYM monitor'] = summarize_sym(T); R['ASY monitor'] = summarize_asy(T, AA)
    return pd.DataFrame(R).T
def retention(df, aa, keys, ths, label):
    AA = aa.set_index(keys); TP = AA.TP_all.sum(); FA = AA.FA_all.sum(); MISS = (AA.n_attack - AA.TP_all).sum()
    rows = []
    for t in ths:
        T = df[df.thr_name == t].set_index(keys).loc[AA.index]
        rows.append(dict(setting=label, threshold=t, correct_detections_kept=(T.acc_attack - T.acc_missed_attack).sum()/TP if TP else np.nan,
                         missed_attacks_kept=T.acc_missed_attack.sum()/MISS if MISS else np.nan, false_alarms_kept=T.acc_false_alarm.sum()/FA if FA else np.nan,
                         correct_detections_total=int(TP), missed_attacks_total=int(MISS), false_alarms_total=int(FA)))
    return rows
