"""Manuscript Figures 1-5. Outputs to figures/."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
from paths import P, DERIVED, FIGURES
O=str(FIGURES)+'/'; EPS=0.01
def rk(d): return np.where(d.acc_n>0,d.acc_err/d.acc_n.clip(lower=1),np.nan)
# ---------- Fig 1 schematic
fig,ax=plt.subplots(figsize=(7.2,3.1)); ax.axis('off'); ax.set_xlim(0,100); ax.set_ylim(0,44)
def box(x,y,w,h,t,c):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4',fc=c,ec='#444',lw=0.8)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=6.2)
def arr(x1,y1,x2,y2): ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',lw=0.9,color='#333'))
box(1,30,15,10,'Flow stream\n68 features\n5,000-flow\nwindows','#eef3fb')
box(21,30,16,10,'Frozen XGBoost\nbinary / 9-class\n+ temperature\nscaling','#eef3fb')
box(42,30,16,10,'Selective\nprediction:\naccept if\nrisk ≤ τ','#eef3fb')
box(63,34,17,7,'Accepted\n(automatic)','#e8f5e9'); box(63,25,17,7,'Abstained\n(to analyst)','#fdecea')
arr(16,35,21,35); arr(37,35,42,35); arr(58,37,63,37.5); arr(58,33,63,28.5)
ax.text(50,21.5,'How is τ chosen for each window?  (policies compared)',ha='center',fontsize=8,weight='bold')
box(1,3,22,14,'Static thresholds\nNormal / Elevated /\nSevere + coverage\ngrid (no monitor)','#fff7e0')
box(26,3,22,14,'Monitor-adaptive\n(TrustShift SSS)\nstate → threshold\nsame-window, lag-1','#fff7e0')
box(51,3,22,14,'Other label-free\nmonitors:\npredictive, feature,\nclass-only; ATC','#fff7e0')
box(76,3,22,14,'Oracle state\n(label-informed\nupper bound;\nnot deployable)','#f2f2f2')
box(84,30,15,11,'Metrics:\nviolations,\ncoverage,\nmissed attacks,\ndeferral','#ede7f6')
arr(80,37.5,84,36)
for x in [12,37,62,87]: arr(x,17.4,50,29.5) if False else None
ax.annotate('',xy=(50,29.6),xytext=(50,18),arrowprops=dict(arrowstyle='->',lw=0.9,color='#333'))
plt.savefig(O+'Figure_1.png',dpi=300,bbox_inches='tight'); plt.close()
# ---------- Fig 2 external shift security
g=pd.read_csv(DERIVED/'S1_family_security.csv')
fams=['Brute Force','DoS','Web Attack','Botnet','DDoS','Infiltration']
fig,axs=plt.subplots(1,2,figsize=(7.2,2.9))
lab={'state_normal':'Fixed','state_elevated':'Elevated','state_severe':'Severe (= adaptive)'}
col={'state_normal':'#9e9e9e','state_elevated':'#f0a35e','state_severe':'#c0392b'}
x=np.arange(len(fams)); w=0.27
for i,th in enumerate(['state_normal','state_elevated','state_severe']):
    d=g[g.thr_name==th].set_index('family').loc[fams]
    axs[0].bar(x+(i-1)*w,100*d.att_def,w,color=col[th],label=lab[th])
    axs[1].bar(x+(i-1)*w,100*d.risk,w,color=col[th])
axs[0].set_ylabel('Attack flows deferred (%)'); axs[1].set_ylabel('Selective risk on accepted flows (%)')
for a in axs: a.set_xticks(x); a.set_xticklabels(fams,rotation=30,ha='right',fontsize=8)
axs[1].axhline(1,ls=':',c='k',lw=0.8); axs[1].text(5.4,2,'1% budget',fontsize=7,ha='right')
axs[0].legend(fontsize=7,frameon=False,loc='upper right'); axs[0].set_title('(a) Deferral by attack family',fontsize=9); axs[1].set_title('(b) Risk on accepted traffic',fontsize=9)
fig.text(0.5,-0.04,'Share of all attack flows correctly detected: 0.0–2.1% (fixed) and 0% (Severe) in every family.',ha='center',fontsize=7.5)
plt.tight_layout(); plt.savefig(O+'Figure_2.png',dpi=300,bbox_inches='tight'); plt.close()
# ---------- Fig 3 frontier
ms=pd.read_csv(P('R2_multiseed_window_threshold_outcomes.csv.gz')); new=ms[ms.seed!=42].copy(); new['viol']=(new.acc_n>0)&(rk(new)>EPS)
mc=pd.read_csv(DERIVED/'monitor_compare_streams.csv')
fig,axs=plt.subplots(1,2,figsize=(7.2,3.0),sharey=True)
for a,t in zip(axs,['binary','multiclass']):
    d=new[new.task==t]; s=d[d.thr_name.str.startswith('cov_')|d.thr_name.isin(['state_normal'])].groupby('thr_name').agg(v=('viol','sum'),acc=('acc_n','sum'),n=('n','sum'))
    s['cov']=100*s.acc/s.n; s=s.sort_values('cov')
    a.plot(s['cov'],s.v,'-o',color='#777',ms=3,lw=1,label='Static threshold (calibration grid)')
    m=mc[mc.task==t].set_index('monitor')
    pts=[('FULL (frozen SSS)','Adaptive 3-family SSS','#c0392b','s'),('FULL lag-1','Adaptive, lag-1','#e67e22','D'),('Predictive only','Predictive-only monitor','#2471a3','^'),('ATC (task-specific)','ATC monitor','#17a589','v'),('Feature only','Feature-only monitor','#8e44ad','P'),('Static Elevated','Static Elevated','#000','x')]
    for k,l,c,mk in pts:
        a.scatter(100*m.loc[k,'cov'],m.loc[k,'viol'],color=c,marker=mk,s=34,zorder=5,label=l)
    a.set_title(f'({"a" if t=="binary" else "b"}) {t.capitalize()}',fontsize=9); a.set_xlabel('Overall coverage (%)'); a.set_xlim(74,101)
axs[0].set_ylabel('Violating windows (of 240)'); axs[1].legend(fontsize=6.5,frameon=False,loc='upper left')
plt.tight_layout(); plt.savefig(O+'Figure_4.png',dpi=300,bbox_inches='tight'); plt.close()
# ---------- Fig 4 stagewise
stages=['clean_initial','S3_05','S3_10','S3_20','S3_10_PLUS_S4_10','clean_recovery']; sl=['Clean','S3-05','S3-10','S3-20','S3-10+\nS4-10','Clean\nrecovery']
d=new[new.task=='binary']; ad=d[d.thr_name=='state_'+d.state]
fig,axs=plt.subplots(1,2,figsize=(7.2,2.8))
for lab_,x_,c,ls in [('Fixed',d[d.thr_name=='state_normal'],'#9e9e9e','--'),('Adaptive SSS',ad,'#c0392b','-'),('Static Elevated',d[d.thr_name=='state_elevated'],'#000',':'),('Static 97.5%',d[d.thr_name=='cov_0.975'],'#2471a3','-.')]:
    cov=[100*x_[x_.stage_name==s].acc_n.sum()/x_[x_.stage_name==s].n.sum() for s in stages]
    dfr=[100*(1-x_[x_.stage_name==s].acc_attack.sum()/x_[x_.stage_name==s].n_attack.sum()) for s in stages]
    axs[0].plot(range(6),cov,ls,marker='o',ms=3,color=c,label=lab_); axs[1].plot(range(6),dfr,ls,marker='o',ms=3,color=c)
for a in axs: a.set_xticks(range(6)); a.set_xticklabels(sl,fontsize=7)
axs[0].set_ylabel('Coverage (%)'); axs[1].set_ylabel('Attack flows deferred (%)'); axs[0].legend(fontsize=7,frameon=False)
axs[0].set_title('(a) Coverage by stage',fontsize=9); axs[1].set_title('(b) Attack deferral by stage',fontsize=9)
plt.tight_layout(); plt.savefig(O+'Figure_5.png',dpi=300,bbox_inches='tight'); plt.close()
# ---------- Fig 5 LOAO
L=pd.read_csv(P('Step_12_3E_LOAO_unseen_fixed_coverage.csv')); L=L[L.task=='binary']
fig,ax=plt.subplots(figsize=(4.6,2.9))
for f,c in zip(['Botnet','Brute Force','DoS','DDoS','Web Attack'],['#8e44ad','#c0392b','#e67e22','#2471a3','#17a589']):
    x_=L[L.held_out_family==f].sort_values('target_coverage'); ax.plot(100*x_.target_coverage,100*x_.selective_risk,'-o',ms=3,color=c,label=f)
ax.set_xlabel('Coverage of held-out family flows (%)'); ax.set_ylabel('Selective risk (miss rate, %)'); ax.legend(fontsize=7,frameon=False,ncol=2); ax.set_ylim(0,105)
plt.tight_layout(); plt.savefig(O+'Figure_3.png',dpi=300,bbox_inches='tight'); plt.close()
print('done')
