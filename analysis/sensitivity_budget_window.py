"""Sensitivity of BCDR and violations to the risk budget and window size; SOC capacity model. POST HOC."""
import pandas as pd, numpy as np, json
R='../results/'
CNT=['n','acc_n','acc_err','n_attack','acc_attack','acc_missed_attack','acc_benign','acc_false_alarm']
def load():
    S={}
    ms=pd.read_csv(R+'revision/R2_multiseed_window_threshold_outcomes.csv.gz'); d=ms[(ms.seed!=42)&(ms.task=='binary')]
    h1=pd.read_csv(R+'acceptall_R7/H1_cic_xgboost_acceptall.csv'); h2=pd.read_csv(R+'acceptall_R7/H2_cic_neural_acceptall.csv')
    h3=pd.read_csv(R+'acceptall_R7/H3_netflow_sequences_acceptall.csv'); h4=pd.read_csv(R+'acceptall_R7/H4_netflow_external_acceptall.csv')
    S['CICIDS2017 sequences, XGBoost']=(d,h1[(h1.dataset=='CIC_sequences')&(h1.seed!=42)],['seed','window_id'],{'fixed':'state_normal','severe':'state_severe','elevated':'state_elevated'})
    n2=pd.read_csv(R+'revision_R4_neural/N2_neural_stream_window_outcomes.csv.gz'); n2=n2[n2.seed!=42]
    for det in ['MLP','FTTransformer']:
        S[f'CICIDS2017 sequences, {det}']=(n2[n2.detector==det],h2[(h2.dataset=='CIC_sequences')&(h2.detector==det)&(h2.seed!=42)],['seed','window_id'],{'fixed':'fixed','severe':'severe','elevated':'elevated'})
    f2=pd.read_csv(R+'replication_R5_netflow/F2_sequence_window_outcomes.csv.gz')
    for det in ['XGBoost','MLP']:
        S[f'NF-UNSW-NB15-v2 sequences, {det}']=(f2[f2.detector==det],h3[h3.detector==det],['seed','window_id'],{'fixed':'fixed','severe':'severe','elevated':'elevated'})
    g=pd.read_csv(R+'confirmation_R6_ton/G1_ToN_window_outcomes.csv.gz')
    for det in ['XGBoost','MLP']:
        S[f'NF-ToN-IoT-v2, {det}']=(g[g.detector==det],h4[(h4.dataset=='ToN_confirmation')&(h4.detector==det)],['window_id'],{'fixed':'fixed','severe':'severe','elevated':'elevated'})
    return S
def merge_windows(df, keys, k):
    """Combine k consecutive 5,000-flow windows into one (sum counts). Groups never cross a stage boundary for k=2 (stages have 10 windows)."""
    x=df.copy(); x['grp']=x['window_id']//k
    gk=[c for c in keys if c!='window_id']+['grp']
    cols=[c for c in CNT+['TP_all','FA_all'] if c in x.columns]
    extra=['thr_name'] if 'thr_name' in x.columns else []
    out=x.groupby(gk+extra,as_index=False)[cols].sum().rename(columns={'grp':'window_id'})
    return out
def bcdr(df, aa, keys, names, eps):
    AA=aa.set_index(keys); r={}
    for lab in ['fixed','elevated','severe']:
        T=df[df.thr_name==names[lab]].set_index(keys).loc[AA.index]
        v=(T.acc_n>0)&(T.acc_err/T.acc_n.clip(lower=1)>eps); det=T.acc_attack-T.acc_missed_attack
        r['SYM '+lab]=(det[~v].sum()/T.n_attack.sum(), int(v.sum()))
    T=df[df.thr_name==names['severe']].set_index(keys).loc[AA.index]
    TP,FA=AA.TP_all,AA.FA_all; miss=T.acc_missed_attack; bok=T.acc_benign-T.acc_false_alarm
    acc=TP+FA+miss+bok; v=(acc>0)&((FA+miss)/acc.clip(lower=1)>eps)
    r['ASY severe']=(TP[~v].sum()/T.n_attack.sum(), int(v.sum()))
    return r
S=load(); rows=[]
for name,(df,aa,keys,names) in S.items():
    for k in [1,2]:
        d2=df if k==1 else merge_windows(df,keys,k); a2=aa if k==1 else merge_windows(aa,keys,k)
        for eps in [0.005,0.01,0.02,0.05]:
            r=bcdr(d2,a2,keys,names,eps)
            best=max([v for kk,v in r.items() if kk.startswith('SYM')],key=lambda t:t[0])
            rows.append(dict(setting=name,window=5000*k,eps=eps,best_sym_bcdr=best[0],best_sym_viol=best[1],
                             sym_severe_bcdr=r['SYM severe'][0],asy_severe_bcdr=r['ASY severe'][0],asy_severe_viol=r['ASY severe'][1],windows=len(a2)))
D=pd.DataFrame(rows); D.to_csv('sensitivity_bcdr.csv',index=False)
pd.set_option('display.width',220)
print(D[D.window==5000].pivot_table(index='setting',columns='eps',values=['best_sym_bcdr','asy_severe_bcdr']).round(3).to_string())
print(D[D.eps==0.01].pivot_table(index='setting',columns='window',values=['best_sym_bcdr','asy_severe_bcdr']).round(3).to_string())
