"""CSE-CIC-IDS2018 binary security outcomes by attack family (manuscript Table 5, Figure 2).
Families are assigned by the capture-file shard that starts each window (see R7_S1_shard_label_composition.csv).
Output: results/derived/S1_family_security.csv"""
from common import *
sec = pd.read_csv(P('R7_S1_binary_security_window_outcomes.csv.gz'))
fam = {1: 'Botnet', 2: 'DoS', 3: 'Web Attack', 4: 'DDoS', 5: 'Infiltration', 6: 'DoS', 7: 'Web Attack', 8: 'Brute Force', 9: 'DDoS', 10: 'Infiltration'}
sec['family'] = sec.first_shard.map(fam)
cols = ['n', 'acc_n', 'n_attack', 'acc_attack', 'acc_missed_attack', 'acc_benign', 'acc_false_alarm', 'acc_err']
sel = sec[sec.thr_name.isin(['state_normal', 'state_elevated', 'state_severe'])]
g = sel.groupby(['family', 'thr_name'])[cols].sum()
g['cov'] = g.acc_n/g.n; g['att_def'] = 1-g.acc_attack/g.n_attack; g['det'] = (g.acc_attack-g.acc_missed_attack)/g.n_attack; g['risk'] = g.acc_err/g.acc_n
g.to_csv(DERIVED/'S1_family_security.csv')
t = sel.groupby('thr_name')[cols].sum(); t['detected'] = t.acc_attack - t.acc_missed_attack
t['coverage'] = t.acc_n/t.n; t['attack_deferred'] = 1-t.acc_attack/t.n_attack; t['risk'] = t.acc_err/t.acc_n
t['violating_windows'] = sel.assign(v=(sel.acc_n > 0) & (rk(sel) > EPS)).groupby('thr_name').v.sum()
print(t[['coverage', 'risk', 'violating_windows', 'attack_deferred', 'detected']].round(4).to_string())
