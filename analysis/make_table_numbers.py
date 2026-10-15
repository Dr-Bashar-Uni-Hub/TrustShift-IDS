"""Numbers for manuscript Tables 6-8 (post hoc comparators are labelled in the manuscript). Output: results/derived/numbers.json"""
from common import *
import json
T={}
ms=pd.read_csv(P('R2_multiseed_window_threshold_outcomes.csv.gz')); new=ms[ms.seed!=42]
pc=pd.read_csv(DERIVED/'ms_policy_compare.csv'); pc=pc[pc.subset=='new4']
def row(x):
    v=int(((x.acc_n>0)&(rk(x)>EPS)).sum()); c=x[x.stage_name.str.startswith('clean')]
    return [v, x.acc_n.sum()/x.n.sum(), c.acc_n.sum()/c.n.sum(), 1-x.acc_attack.sum()/x.n_attack.sum()]
mon=pd.read_csv(P('V2_STEP_13C_MULTI_SEED_LABEL_FREE_MONITORING_WINDOWS.csv')).rename(columns={'deployment_order_seed':'seed','global_window_id':'window_id'}).set_index(['seed','window_id'])
win=new[new.thr_name=='state_normal'].pivot_table(index=['seed','window_id'],columns='task',values='atc_est')
def apply_states(t,st):
    st=st.copy(); st.index.names=['seed','window_id']
    d=new[new.task==t].merge(st.rename('ms').reset_index(),on=['seed','window_id']); return d[d.thr_name=='state_'+d.ms]
pols={}
for t in ['binary','multiclass']:
    d=new[new.task==t]
    full=pd.Series(state(mon.SSS_primary,B['FULL']),index=mon.index)
    lag=full.groupby(level=0).shift(1).fillna('normal')
    POL={'Fixed (Normal threshold)':d[d.thr_name=='state_normal'],
       'Adaptive, 3-family SSS (frozen)':apply_states(t,full),
       'Adaptive, 3-family SSS, lag-1':apply_states(t,lag),
       'Static Elevated threshold':d[d.thr_name=='state_elevated'],
       'Static Severe threshold':d[d.thr_name=='state_severe'],
       'Static 97.5% calibration threshold':d[d.thr_name=='cov_0.975'],
       'Monitor: predictive evidence only':apply_states(t,pd.Series(state(mon[FAM['pred']],B['pred']),index=mon.index)),
       'Monitor: predicted-class evidence only':apply_states(t,pd.Series(state(mon[FAM['cls']],B['cls']),index=mon.index)),
       'Monitor: input-feature evidence only':apply_states(t,pd.Series(state(mon[FAM['feat']],B['feat']),index=mon.index)),
       'Monitor: ATC':apply_states(t,pd.Series(state(win[t],B['ATC_'+t]),index=win.index))}
    for k,x in POL.items(): pols.setdefault(k,{})[t]=row(x)
for _,r in pc[pc.policy.str.startswith('Oracle')].iterrows():
    pols.setdefault('Oracle state (label-informed)',{})[r['task']]=[int(r['viol']),r['cov'],None,r['att_deferred']]
T['streams']=pols
for k,v in pols.items(): print(k, [[round(z,4) if isinstance(z,float) else z for z in v[t]] for t in v])
c=pd.read_csv(P('R3_S3_S4_window_threshold_outcomes.csv.gz')); c['viol']=(c.acc_n>0)&(rk(c)>EPS)
s3m=pd.read_csv(P('V2_S3_PAIRED_PRIMARY_SSS_ALL_CONDITIONS.csv')); s4m=pd.read_csv(P('V2_S4_IMPORTANT_PRIMARY_SSS_windows.csv')).rename(columns={'window':'window_id'})
fam=pd.concat([s3m[['condition','window_id',FAM['pred']]],s4m[['condition','window_id',FAM['pred']]]]).drop_duplicates(['condition','window_id']).set_index(['condition','window_id'])
ps=pd.Series(state(fam[FAM['pred']],B['pred']),index=fam.index).rename('ps').reset_index()
c=c.merge(ps,on=['condition','window_id'],how='left')
grid={}
for cond in ['clean','S3_05','S3_10','S3_20','S3_30','important_missing_05','important_missing_10','important_missing_20','important_missing_30']:
    for t in ['binary','multiclass']:
        d=c[(c.condition==cond)&(c.task==t)]
        f=d[d.thr_name=='state_normal']; a=d[d.thr_name=='state_'+d.state]; E=d[d.thr_name=='state_elevated']; S=d[d.thr_name=='state_severe']; p=d[d.thr_name=='state_'+d.ps]
        grid.setdefault(cond,{})[t]={k:[int(x.viol.sum()),round(x.acc_n.sum()/x.n.sum(),4)] for k,x in [('fixed',f),('adaptive',a),('E',E),('S',S),('pred',p)]}
        grid[cond][t]['states']=f.state.value_counts().to_dict()
T['grid']=grid
for k,v in grid.items(): print(k, v)
l=pd.read_csv(P('R6_Level2_window_threshold_outcomes.csv.gz')); l['viol']=(l.acc_n>0)&(rk(l)>EPS)
comp={}
for sc in l.condition.unique():
    for t in ['binary','multiclass']:
        d=l[(l.condition==sc)&(l.task==t)]; a=d[d.thr_name=='state_'+d.state]
        comp.setdefault(sc,{})[t]={'W':int(d.window_id.nunique()),'fixed':int(d[d.thr_name=='state_normal'].viol.sum()),'adaptive':int(a.viol.sum()),'E':int(d[d.thr_name=='state_elevated'].viol.sum()),'cov_ad':round(a.acc_n.sum()/a.n.sum(),4),'att_def':round(1-a.acc_attack.sum()/a.n_attack.sum(),4)}
T['compound']=comp
for k,v in comp.items(): print(k,v)
json.dump(T,open(DERIVED/'numbers.json','w'),indent=1,default=float)
