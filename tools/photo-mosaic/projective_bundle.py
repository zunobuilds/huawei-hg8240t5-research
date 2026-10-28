"""Sparse analytic projective bundle refinement on measured image correspondences."""
import numpy as np
from scipy import sparse
from scipy.optimize import least_squares

def refine(T,anchor,edges,max_evaluations=100):
 n=len(T);others=[i for i in range(n) if i!=anchor];offset={i:k for k,i in enumerate(others)}
 ii=np.concatenate([np.full(len(e['p']),e['i'],int) for e in edges]);jj=np.concatenate([np.full(len(e['p']),e['j'],int) for e in edges]);p=np.concatenate([e['p'] for e in edges]);q=np.concatenate([e['q'] for e in edges]);count=len(p)
 def unpack(x):
  t=np.tile(np.eye(3),(n,1,1))
  for i,k in offset.items():t[i]=np.r_[x[k*8:(k+1)*8],1].reshape(3,3)
  return t
 def warp(t,ids,pts):
  m=t[ids];den=m[:,2,0]*pts[:,0]+m[:,2,1]*pts[:,1]+1
  den=np.where(abs(den)<1e-12,np.where(den<0,-1e-12,1e-12),den)
  uv=np.einsum('nij,nj->ni',m[:,:2,:2],pts)+m[:,:2,2]
  return uv/den[:,None],den
 def residual(x):
  t=unpack(x);u,_=warp(t,ii,p);v,_=warp(t,jj,q);return (u-v).ravel()
 rows=[];cols=[];parts=[]
 for ids,pts,sign in [(ii,p,1),(jj,q,-1)]:
  keep=ids!=anchor;idx=np.flatnonzero(keep);base=np.array([offset[int(i)] for i in ids[keep]])*8
  for axis in range(2):
   columns=[axis*3,axis*3+1,axis*3+2,6,7]
   for col in columns:
    rows.append(idx*2+axis);cols.append(base+col);parts.append((ids,pts,sign,keep,axis,col))
 row=np.concatenate(rows);col=np.concatenate(cols)
 def jacobian(x):
  t=unpack(x);data=[]
  projections={}
  for ids,pts,sign,keep,axis,k in parts:
   key=sign
   if key not in projections:projections[key]=warp(t,ids,pts)
   uv,den=projections[key]
   if k in (6,7):v=-uv[:,axis]*pts[:,k-6]/den
   elif k%3==2:v=1/den
   else:v=pts[:,k%3]/den
   data.append(sign*v[keep])
  return sparse.coo_matrix((np.concatenate(data),(row,col)),shape=(count*2,len(others)*8)).tocsr()
 initial=np.concatenate([T[i].ravel()[:8] for i in others])
 result=least_squares(residual,initial,jac=jacobian,loss='soft_l1',f_scale=3,x_scale='jac',max_nfev=max_evaluations,tr_solver='lsmr',tr_options={'maxiter':300})
 return unpack(result.x),result
