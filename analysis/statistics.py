"""POST HOC statistics: exact McNemar tests, stratified coverage-difference bootstrap, source-null boundary bootstrap. Output: results/derived/stats.json"""
from common import *
from scipy.stats import binomtest
import json
ms=pd.read_csv(P('R2_multiseed_window_threshold_outcomes.csv.gz')); new=ms[ms.seed!=42].copy(); new['viol']=(new.acc_n>0)&(rk(new)>EPS)
mon=pd.read_csv(P('V2_STEP_13C_MULTI_SEED_LABEL_FREE_MONITORING_WINDOWS.csv')).rename(columns={'deployment_order_seed':'seed','global_window_id':'window_id'})
mon=mon[mon.seed!=42].set_index(['seed','window_id'])
rng=np.random.default_rng(2026); S={}
piv={t:{th:new[(new.task==t)&(new.thr_name==th)].set_index(['seed','window_id']).loc[mon.index] for th in ['state_normal','state_elevated','state_severe']} for t in ['binary','multiclass']}
nulv=nul.SSS_primary.to_numpy(); res=[]
for b in range(2000):
    q=np.quantile(rng.choice(nulv,54,replace=True),[.95,.99]); st=state(mon.SSS_primary.to_numpy(),q); r={'q95':q[0],'q99':q[1]}
    for t in ['binary','multiclass']:
        acc=np.select([st=='normal',st=='elevated'],[piv[t]['state_normal'].acc_n,piv[t]['state_elevated'].acc_n],piv[t]['state_severe'].acc_n)
        v=np.select([st=='normal',st=='elevated'],[piv[t]['state_normal'].viol,piv[t]['state_elevated'].viol],piv[t]['state_severe'].viol)
        r[t+'_viol']=int(v.sum()); r[t+'_cov']=acc.sum()/(5000*len(st))
    res.append(r)
R=pd.DataFrame(res); S['boot']={c:[float(R[c].quantile(.025)),float(R[c].median()),float(R[c].quantile(.975))] for c in R.columns}
def mcn(a,b):
    n01=int((a&~b).sum()); n10=int((~a&b).sum()); return [n01,n10,float(binomtest(n01,n01+n10,.5).pvalue) if n01+n10 else 1.0]
for t in ['binary','multiclass']:
    d=new[new.task==t]; ad=d[d.thr_name=='state_'+d.state].sort_values(['seed','window_id'])
    for comp in ['state_normal','cov_0.975','state_elevated']:
        S[f'mcn_{t}_{comp}']=mcn(ad.viol.to_numpy(),d[d.thr_name==comp].sort_values(['seed','window_id']).viol.to_numpy())
    st=d[d.thr_name=='cov_0.975'].sort_values(['seed','window_id']); diff=(ad.acc_n.to_numpy()-st.acc_n.to_numpy())/5000
    strata=ad.seed.astype(str).to_numpy()+ad.stage_name.to_numpy(); groups=[np.where(strata==s)[0] for s in np.unique(strata)]
    bs=[diff[np.concatenate([rng.choice(g,len(g)) for g in groups])].mean() for _ in range(5000)]
    S[f'covdiff_{t}']=[float(diff.mean()),float(np.quantile(bs,.025)),float(np.quantile(bs,.975))]
print(json.dumps(S,indent=1)); json.dump(S,open(DERIVED/'stats.json','w'),indent=1)
