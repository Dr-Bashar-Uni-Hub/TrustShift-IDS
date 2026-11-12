"""Supplementary S21: illustrative SOC capacity model on the CICIDS2017 XGBoost deployment sequences (four new orderings). POST HOC."""
import pandas as pd, numpy as np
R = '../results/'
ms = pd.read_csv(R + 'revision/R2_multiseed_window_threshold_outcomes.csv.gz'); d = ms[(ms.seed != 42) & (ms.task == 'binary')]
h1 = pd.read_csv(R + 'acceptall_R7/H1_cic_xgboost_acceptall.csv'); aa = h1[(h1.dataset == 'CIC_sequences') & (h1.seed != 42)].set_index(['seed', 'window_id'])
keys = ['seed', 'window_id']
def pol(name):
    x = d[d.thr_name == 'state_' + d.state] if name == 'adaptive' else d[d.thr_name == name]
    x = x.set_index(keys).loc[aa.index].copy(); x['deferred'] = x.n - x.acc_n; x['def_att'] = x.n_attack - x.acc_attack; return x
def asy():
    T = d[d.thr_name == 'state_severe'].set_index(keys).loc[aa.index].copy()
    acc = aa.TP_all + aa.FA_all + T.acc_missed_attack + (T.acc_benign - T.acc_false_alarm)
    T['deferred'] = T.n - acc; T['def_att'] = T.n_attack - (aa.TP_all + T.acc_missed_attack); return T
P = {'Adaptive (TrustShift)': pol('adaptive'), 'Static Severe': pol('state_severe'), 'Static 97.5%': pol('cov_0.975'), 'Asymmetric Severe': asy()}
rows = []
for k, x in P.items():
    for C in [250, 500, 1000]:
        unrev = (x.def_att * np.clip(1 - C / x.deferred.replace(0, np.nan), 0, 1)).fillna(0)
        rows.append(dict(policy=k, capacity=C, mean_deferred=round(x.deferred.mean()), max_deferred=int(x.deferred.max()),
                         windows_over_capacity=round((x.deferred > C).mean(), 3), deferred_attack_share=round(x.def_att.sum() / x.n_attack.sum(), 3),
                         unreviewed_attack_share=round(unrev.sum() / x.n_attack.sum(), 3)))
print(pd.DataFrame(rows).to_string(index=False))
