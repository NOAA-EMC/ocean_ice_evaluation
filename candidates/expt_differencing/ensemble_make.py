'''
make ensemble mean and sigma stats from ice model for sfs ensemble
'''
import os

import numpy as np
import netCDF4 as nc


tag='20231101'
nx = 360
ny = 320
pinteresting = ['aice_h', 'hi_h', 'uvel_h', 'vvel_h']

for hh in range(24, 8790, 24):
#for hh in range(24, 49, 24):
  hhh=f"{hh:03d}"
  sums  = np.zeros((len(pinteresting), ny, nx))
  sumsq = np.zeros((len(pinteresting), ny, nx))
  sigma = np.zeros((len(pinteresting), ny, nx))

  for n in range(0,11):
    nnn="{:03d}".format(n)
    #debug: print(nnn, hhh, flush=True)
    fname='sfs.'+tag+'/00/mem'+nnn+'/products/ice/netcdf/native/sfs.ice.t00z.native.f'+hhh+'.nc'
    if os.path.exists(fname):
        #debug: print('ok', flush=True)
      dset = nc.Dataset(fname,'r')
      #debug: print(dset.dimensions.items(), flush=True )

      # if in the list named as interesting, accumulate stats
      for p in range(0,len(pinteresting)):
        #debug: print(p, pinteresting[p], n, hh, flush=True)
        tmp = dset.variables[pinteresting[p]][0,:,:]
        sums[p] += tmp
        tmp *= tmp
        sumsq[p] += tmp

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
