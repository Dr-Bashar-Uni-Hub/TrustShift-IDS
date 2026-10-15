"""POST HOC policy comparison on the deployment orders (manuscript Table 8, Figure 4).
Outputs: results/derived/ms_policy_compare.csv, results/derived/monitor_compare_streams.csv"""
from common import *
ms = pd.read_csv(P('R2_multiseed_window_threshold_outcomes.csv.gz')); ms['viol'] = (ms.acc_n > 0) & (rk(ms) > EPS)
keys = ['seed', 'window_id', 'task']
def summarize(x):
    return dict(viol=int(x.viol.sum()), cov=x.acc_n.sum()/x.n.sum(), risk=x.acc_err.sum()/x.acc_n.sum(),
                att_deferred=1-x.acc_attack.sum()/x.n_attack.sum(),
                missed_among_acc_att=x.acc_missed_attack.sum()/max(x.acc_attack.sum(), 1),
                fa_rate=x.acc_false_alarm.sum()/x.acc_benign.sum())
def static(d, name): return d[d.thr_name == name]
def adaptive(d, lag=0):
    st = d[d.thr_name == 'state_normal'][keys + ['state']].copy()
    if lag:
        st = st.sort_values(['task', 'seed', 'window_id'])
        st['state'] = st.groupby(['task', 'seed']).state.shift(lag).fillna('normal')
    st['thr_name'] = 'state_' + st.state
    return d.drop(columns='state').merge(st, on=keys + ['thr_name'])
def oracle(d):
    x = d[d.thr_name.isin(['state_normal', 'state_elevated', 'state_severe'])].copy()
    x['o'] = x.thr_name.map({'state_normal': 0, 'state_elevated': 1, 'state_severe': 2})
    ok = x[~x.viol].sort_values('o').groupby(keys).head(1)
    rest = x.merge(ok[keys].assign(k=1), on=keys, how='left'); rest = rest[rest.k.isna() & (rest.o == 2)]
    return pd.concat([ok, rest.drop(columns='k')])
pols = {'Fixed (Normal threshold)': lambda d: static(d, 'state_normal'),
        'Adaptive TrustShift (same-window)': adaptive, 'Adaptive, causal lag-1': lambda d: adaptive(d, 1),
        'Static Elevated threshold': lambda d: static(d, 'state_elevated'), 'Static Severe threshold': lambda d: static(d, 'state_severe'),
        'Static cov 0.975': lambda d: static(d, 'cov_0.975'), 'Static cov 0.95': lambda d: static(d, 'cov_0.950'),
        'Oracle state (label-informed)': oracle}
rows = []
for subset, dd in [('new4', ms[ms.seed != 42]), ('all5', ms)]:
    for name, fn in pols.items():
        x = fn(dd)
        for t in ['binary', 'multiclass']:
            rows.append(dict(policy=name, subset=subset, task=t, **summarize(x[x.task == t])))
pd.DataFrame(rows).to_csv(DERIVED/'ms_policy_compare.csv', index=False)
# alternative label-free monitors (new orders)
new = ms[ms.seed != 42]
mon = pd.read_csv(P('V2_STEP_13C_MULTI_SEED_LABEL_FREE_MONITORING_WINDOWS.csv')).rename(columns={'deployment_order_seed': 'seed', 'global_window_id': 'window_id'}).set_index(['seed', 'window_id'])
win = new[new.thr_name == 'state_normal'].pivot_table(index=['seed', 'window_id'], columns='task', values='atc_est')
clean = lambda x: x.stage_name.str.startswith('clean')
full = pd.Series(state(mon.SSS_primary, B['FULL']), index=mon.index)
monitors = {'FULL (frozen SSS)': {t: full for t in ['binary', 'multiclass']},
            'FULL lag-1': {t: full.groupby(level=0).shift(1).fillna('normal') for t in ['binary', 'multiclass']}}
for k, lab in [('pred', 'Predictive only'), ('cls', 'Predicted-class only'), ('feat', 'Feature only')]:
    monitors[lab] = {t: pd.Series(state(mon[FAM[k]], B[k]), index=mon.index) for t in ['binary', 'multiclass']}
monitors['ATC (task-specific)'] = {t: pd.Series(state(win[t], B['ATC_' + t]), index=win.index) for t in ['binary', 'multiclass']}
rows = []
for name, st in monitors.items():
    for t, x in evaluate(new, ['seed', 'window_id'], st).items():
        rows.append(dict(monitor=name, task=t, **summ(x, clean)))
for name, thr in [('Static Elevated', 'state_elevated'), ('Static Severe', 'state_severe')]:
    for t in ['binary', 'multiclass']:
        rows.append(dict(monitor=name, task=t, **summ(new[(new.task == t) & (new.thr_name == thr)], clean)))
R = pd.DataFrame(rows); R.to_csv(DERIVED/'monitor_compare_streams.csv', index=False)
print(R.round(4).to_string(index=False))
