#!/usr/bin/env python3
"""Step 91: is step 51's pooled repricing slowdown (+0.0565 -> +0.0239) present within each
category? Before/after per category, within/between decomposition, and a trend+break test."""
import importlib.util, sys, io, contextlib
import numpy as np, pandas as pd
sys.path.insert(0,'code')
spec=importlib.util.spec_from_file_location('m51','code/51-seller-structure.py'); m=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)
pairs=m.reprice_pairs(m.BAL)
rows=[(q,g,dl,m.CAT[g]) for q,v in pairs.items() for dl,g in v]
d=pd.DataFrame(rows,columns=['q','gig','dl','cat'])
d=d[(d.q>='2020Q4')&(d.q<='2023Q4')]
d['post']=(d.q>='2022Q4').astype(int)
def diff(x):
    # gig-clustered SE of post-pre difference in means via regression dl ~ post
    X=np.column_stack([np.ones(len(x)),x.post]); y=x.dl.to_numpy()
    XtXi=np.linalg.inv(X.T@X); b=XtXi@X.T@y; e=y-X@b
    S=pd.DataFrame(X*e[:,None]).groupby(x.gig.to_numpy()).sum().to_numpy(); G=len(S)
    se=np.sqrt(np.diag(XtXi@S.T@S@XtXi*G/(G-1)))
    return b[0],b[0]+b[1],b[1],se[1],x.gig.nunique(),len(x)
print(f"{'cat':12s} {'pre':>8s} {'post':>8s} {'diff':>8s} {'se':>7s} {'t':>6s} gigs pairs")
r=diff(d); print(f"{'POOLED':12s} {r[0]:+.4f} {r[1]:+.4f} {r[2]:+.4f} {r[3]:.4f} {r[2]/r[3]:+.2f} {r[4]} {r[5]}")
out={}
for c,x in d.groupby('cat'):
    r=diff(x); out[c]=r; print(f"{c:12s} {r[0]:+.4f} {r[1]:+.4f} {r[2]:+.4f} {r[3]:.4f} {r[2]/r[3]:+.2f} {r[4]} {r[5]}")
# weights shift + decomposition
w=d.groupby(['post','cat']).size().unstack(0); w=w/w.sum()
mm=d.groupby(['post','cat']).dl.mean().unstack(0)
within=((w[0]+w[1])/2*(mm[1]-mm[0])).sum(); between=((w[1]-w[0])*(mm[0]+mm[1])/2).sum()
print('\nshares pre/post:\n',w.round(3)); print(f'pooled change {(w[1]*mm[1]).sum()-(w[0]*mm[0]).sum():+.4f} = within {within:+.4f} + between {between:+.4f}')
# precision-weighted average of category diffs
b=np.array([out[c][2] for c in out]); s=np.array([out[c][3] for c in out]); iw=1/s**2
print(f'inverse-variance avg of category diffs {np.sum(iw*b)/iw.sum():+.4f} se {np.sqrt(1/iw.sum()):.4f}; heterogeneity Q={np.sum(iw*(b-np.sum(iw*b)/iw.sum())**2):.2f} on {len(b)-1} df')
# pre-trend: within-category, pre period slope
d['qn']=d.q.str[:4].astype(int)*4+d.q.str[-1].astype(int)
print('\nannual mean dlog p by category:'); d['yr']=d.q.str[:4]; print(d.groupby(['cat','yr']).dl.mean().unstack().round(3))

print('\nWith a linear trend: dl ~ trend + post (gig-clustered)')
def trend_break(x):
    t=(x.qn-x.qn.min()).to_numpy(float)
    X=np.column_stack([np.ones(len(x)),t,x.post]); y=x.dl.to_numpy()
    XtXi=np.linalg.inv(X.T@X); b=XtXi@X.T@y; e=y-X@b
    S=pd.DataFrame(X*e[:,None]).groupby(x.gig.to_numpy()).sum().to_numpy(); G=len(S)
    se=np.sqrt(np.diag(XtXi@S.T@S@XtXi*G/(G-1))); return b,se
b,se=trend_break(d); print(f"{'POOLED':12s} trend {b[1]:+.4f} (t {b[1]/se[1]:+.2f})  post {b[2]:+.4f} (t {b[2]/se[2]:+.2f})")
for c,x in d.groupby('cat'):
    b,se=trend_break(x); print(f"{c:12s} trend {b[1]:+.4f} (t {b[1]/se[1]:+.2f})  post {b[2]:+.4f} (t {b[2]/se[2]:+.2f})")
