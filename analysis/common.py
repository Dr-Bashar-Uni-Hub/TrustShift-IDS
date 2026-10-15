"""Shared definitions: source-null boundaries for the frozen SSS, single-family and ATC monitors; state assignment; helpers."""
from paths import P, DERIVED
import pandas as pd, numpy as np
EPS=0.01
nul=pd.read_csv(P('V2_source_null_PRIMARY_SSS.csv')); n2=pd.read_csv(P('R1_source_null_windows_ATC_and_outcomes.csv'))
FAM={'pred':'family__predictive_confidence_uncertainty','cls':'family__predicted_class_distribution','feat':'family__input_feature_distribution'}
B={'FULL':tuple(np.quantile(nul.SSS_primary,[.95,.99]))}
for k,c in FAM.items(): B[k]=tuple(np.quantile(nul[c],[.95,.99]))
for t in ['binary','multiclass']: B['ATC_'+t]=tuple(np.quantile(n2[f'{t}_atc_est_lwo'],[.95,.99]))
def state(x,b): return np.where(x<=b[0],'normal',np.where(x<=b[1],'elevated','severe'))
def rk(d): return np.where(d.acc_n>0,d.acc_err/d.acc_n.clip(lower=1),np.nan)
def evaluate(out, keys, states_by_task):
    # out: long table with thr_name; states_by_task: dict task-> Series aligned by keys -> state
    res={}
    for t in ['binary','multiclass']:
        d=out[out.task==t]; s=states_by_task[t].rename('mstate').reset_index()
        x=d.merge(s,on=keys); x=x[x.thr_name=='state_'+x.mstate]
        res[t]=x
    return res
def summ(x, clean_mask=None):
    r=dict(viol=int(((x.acc_n>0)&(rk(x)>EPS)).sum()),cov=x.acc_n.sum()/x.n.sum(),risk=x.acc_err.sum()/x.acc_n.sum())
    if 'n_attack' in x and x.n_attack.sum()>0: r['att_def']=1-x.acc_attack.sum()/x.n_attack.sum()
    if clean_mask is not None:
        c=x[clean_mask(x)]; r['clean_cov']=c.acc_n.sum()/c.n.sum()
    return r
