'''
difference two experiments and wonder about significance of differences
RG: currently just reading a single experiment
'''

import os

import numpy as np
import netCDF4 as nc

#-------------------------------------------------------------------

tag='20231101'
nx = 360
ny = 320
pinteresting = ['aice_h', 'hi_h', 'uvel_h', 'vvel_h']

#base_model1, base_model2
#ens1_summary, ens2_summary (mean, sigma) [24,8784]

#delta base_model1 - base_model2
# pooled variance estimator =
#  ((n1-1)*sigma1^2 + (n2-1)sigma2^2)/(n1+n2-2) = sigma_pooled^2
# n1 = n2 = 11 in our case
#delta/sigma_pooled -- maps
sums = np.zeros((ny,nx))
sumsq = np.zeros((ny,nx))
sigma = np.zeros((ny,nx))

for hh in range(24, 8790, 24):
  hhh=f"{hh:03d}"

  for n in range(0,11):
    nnn=f"{n:03d}"
    fname='sfs.'+tag+'/00/mem'+nnn+'/products/ice/netcdf/native/sfs.ice.t00z.native.f'+hhh+'.nc'
    if os.path.exists(fname):
      dset = nc.Dataset(fname,'r')

      # if in the list named as interesting, accumulate stats
      for p in range(0,len(pinteresting)):
        tmp = dset.variables[pinteresting[p]][0,:,:]
        sums[p] += tmp
        tmp *= tmp
        sumsq[p] += tmp
      dset.close()

  #end nmembers
  for p in range(0, len(pinteresting)):
    sums[p][sums[p] < 1.e10 ]  /= 11
    sums[p][sums[p] >= 1.e10 ]  = 0
    sums[p][np.isnan(sums[p])]  = 0

    sumsq[p][sumsq[p] < 1.e10 ] /= 11
    sumsq[p][sumsq[p] >= 1.e10 ] = 0
    sumsq[p][np.isnan(sumsq[p])]  = 0

    sigma[p] = sumsq[p] - sums[p]*sums[p]
    sigma[p][sigma[p] < 0] = 0
    sigma[p] = np.sqrt(sigma[p])
    print(pinteresting[p], hhh, sums[p].max(), sums[p].min(), sigma[p].max(), sigma[p].min() )
  # RG write out netcdf of mean, sigma

  del sums, sumsq, sigma
