'''
difference two experiments and wonder about significance of differences
Arguments are experiment1 name, experiment2 name, date (as an 8 digit 
    string), and run length (hours)

This version is for working with output of tofile (binary) on same system

Robert Grumbine 1/6/2026
'''

import os
import sys
from math import sqrt
import copy

import numpy as np
import netCDF4 as nc

#-------------------------------------------------------------------
expt1  = sys.argv[1]
expt2  = sys.argv[2]
tag    = sys.argv[3]
runlen = int(sys.argv[4])
# 1 degree grid
nx = 360
ny = 320
# 0.25 degree grid

pinteresting = ['aice_h', 'hi_h', 'uvel_h', 'vvel_h', 'hs_h', 'Tsfc_h', 'albsni_h']
# available:
#    aice_h, hi_h, uvel_h, vvel_h
#    hs_h, Tsfc_h, albsni_h,
#    tmask, tarea, TLON, TLAT (nj, ni)

n1 = 11 #ensemble members
n2 = 11
#-------------------------------------------------------------------
nparam = len(pinteresting)
#base_model1, base_model2
#ens1_summary, ens2_summary (mean, sigma) [24,8784]

#delta base_model1 - base_model2
# pooled variance estimator =
#  ((n1-1)*sigma1^2 + (n2-1)sigma2^2)/(n1+n2-2) = sigma_pooled^2
#delta/sigma_pooled -- maps
def pool(fn1, fn2, fsigma1, fsigma2):
  ''' pool constructs the pooled estimator of variance: pool(n1, n2, sigma1, sigma2)'''
  fpool = np.zeros(fsigma1.shape)
  fpool = (fn1-1)*fsigma1*fsigma1
  fpool += (fn2-1)*fsigma2*fsigma2
  fpool /= (fn1+fn2-2)
  return fpool


delta  = np.zeros((ny, nx))
mean1  = np.zeros((ny, nx))
mean2  = np.zeros((ny, nx))
sigma1 = np.zeros((ny, nx))
sigma2 = np.zeros((ny, nx))

for hh in range(24, runlen+1, 24):
  hhh=f"{hh:03d}"

  dname1 = expt1+'/sfs.'+tag+'/00/ensstat/products/ice/bin/1p00/'
  dname2 = expt2+'/sfs.'+tag+'/00/ensstat/products/ice/bin/1p00/'
  if (not os.path.exists(dname1) or not os.path.exists(dname2)):
    print("missing at least one path of:\n",dname1,"\n", dname2)
    sys.exit(1)

  for p in range(0,nparam):
    outname1 = dname1 + '/sfs.t00z.mean'+pinteresting[p]+'.f'+hhh+'.bin'
    outname2 = dname2 + '/sfs.t00z.mean'+pinteresting[p]+'.f'+hhh+'.bin'
    #debug: print(len(tmp), tmp.shape)
    if os.path.exists(outname1) :
      tmp = np.fromfile(outname1, count=-1, dtype=np.float64)
    else:
      print(outname1, 'does not exist')
      sys.exit(1)
    #debug: print(hhh, len(tmp), tmp.shape)
    mean1 = np.reshape(tmp, (ny,nx))
    #debug: print(len(mean1), mean1.shape, mean1.max(), mean1.min() )

    tmp = np.fromfile(outname2, dtype=np.float64)
    mean2 = np.reshape(tmp, (ny,nx))
    print(hhh, "mean", pinteresting[p], f"{mean1.max():.4f}", \
            f"{mean1.min():.4f}", f"{mean2.max():.4f}", f"{mean2.min():.4f}", end=" ")
    delta = mean1
    delta -= mean2
    print(f"{delta.max():.4f}", f"{delta.min():.4f}" )

    outname1 = dname1 + '/sfs.t00z.sigma'+pinteresting[p]+'.f'+hhh+'.bin'
    with open(outname1,"rb") as fout1:
      tmp = np.fromfile(fout1, dtype=float)
      sigma1 = np.reshape(tmp, (ny, nx))
    outname2 = dname2 + '/sfs.t00z.sigma'+pinteresting[p]+'.f'+hhh+'.bin'
    with open(outname2,"rb") as fout2:
      tmp = np.fromfile(fout2, dtype=float)
      sigma2 = np.reshape(tmp, (ny, nx))
    print(hhh, "sigma", pinteresting[p], f"{sigma1.max():.4f}", \
            f"{sigma1.min():.4f}", f"{sigma2.max():.4f}", f"{sigma2.min():.4f}", end=" ")

    tmp = pool(n1, n2, sigma1, sigma2)
    tmp = np.sqrt(tmp)
    print(f"{tmp.max():.4f}", f"{tmp.min():.4f}")

    tstat = delta[tmp > 0] / tmp[tmp > 0]
    tstat /= sqrt(1/float(n1) + 1./float(n2) )
    print(hhh, pinteresting[p], "tstat: ",f"{tstat.max():.4f}", f"{tstat.min():.4f}",end=" ")
    tstat = np.abs(tstat)
    print(f"{tstat[tstat > 0].sum() / len(tstat[tstat > 0]):.4f}")

    # map of delta, tstat -- put in ?
