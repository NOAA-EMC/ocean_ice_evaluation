'''
make ensemble mean and sigma stats from ice model for sfs ensemble
Arguments are experiment name, date (as an 8 digit string), and run length (hours)

Robert Grumbine 1/6/2026
'''
import os
import sys

import numpy as np
import netCDF4 as nc

#---- Adjust these to your experiment ---------------------
exptname = sys.argv[1]
tag      = sys.argv[2]
runlen = int(sys.argv[3])
# 1 degree grid
nx = 360
ny = 320
# 0.25 degree grid

pinteresting = ['aice_h', 'hi_h', 'uvel_h', 'vvel_h', 'hs_h', 'Tsfc_h', 'albsni_h']
# available:
#    aice_h, hi_h, uvel_h, vvel_h
#    hs_h, Tsfc_h, albsni_h,
#    tmask, tarea, TLON, TLAT (nj, ni) -- should be identical for all members at all leads

#---------- Should need no changes below here
nparam = len(pinteresting)

for hh in range(24, runlen+1, 24):
  hhh=f"{hh:03d}"
  sums  = np.zeros((nparam, ny, nx))
  sumsq = np.zeros((nparam, ny, nx))
  sigma = np.zeros((nparam, ny, nx))

  for n in range(0,11):
    nnn=f"{n:03d}"
    #debug: print(nnn, hhh, flush=True)
    #fname=exptname+'/sfs.'+tag+'/00/mem'+nnn+\
    #        '/products/ice/netcdf/native/sfs.ice.t00z.native.f'+hhh+'.nc'
    #fname=exptname+'/sfs.'+tag+'/00/mem'+nnn+\
    #        '/products/ice/netcdf/native/sfs.t00z.tripolar.f'+hhh+'.nc'
    fname=exptname+'/sfs.'+tag+'/00/mem'+nnn+\
            '/products/ice/netcdf/native/sfs.t00z.native.f'+hhh+'.nc'
    if os.path.exists(fname):
        #debug: print('ok', flush=True)
      dset = nc.Dataset(fname,'r')
      #debug: print(dset.dimensions.items(), flush=True )

      # if in the list named as interesting, accumulate stats
      for p in range(0,nparam):
        #debug: print(p, pinteresting[p], n, hh, flush=True)
        tmp = dset.variables[pinteresting[p]][0,:,:]
        sums[p] += tmp
        tmp *= tmp
        sumsq[p] += tmp
    else:
      print("couldn't find ",fname, flush=True)
      sys.exit(1)

  #end nmembers
  for p in range(0, nparam):
    sums[p][sums[p] < 1.e10 ]  /= 11
    sums[p][sums[p] >= 1.e10 ]  = 0
    sums[p][np.isnan(sums[p])]  = 0

    sumsq[p][sumsq[p] < 1.e10 ] /= 11
    sumsq[p][sumsq[p] >= 1.e10 ] = 0
    sumsq[p][np.isnan(sumsq[p])]  = 0

    sigma[p] = sumsq[p] - sums[p]*sums[p]
    sigma[p][sigma[p] < 0] = 0
    sigma[p] = np.sqrt(sigma[p])
    print(pinteresting[p], hhh, sums[p].max(), sums[p].min(), \
            sigma[p].max(), sigma[p].min(), flush=True )
  # RG write out netcdf of mean, sigma
    dirname = exptname+'/sfs.'+tag+'/00/ensstat/products/ice/bin/1p00/'
    os.system('mkdir -p '+dirname)

    outname = dirname + '/sfs.t00z.mean'+pinteresting[p]+'.f'+hhh+'.bin'
    with open(outname,"wb") as fout:
      sums[p].tofile(fout)

    outname = dirname + '/sfs.t00z.sigma'+pinteresting[p]+'.f'+hhh+'.bin'
    #with open(outname,"wb") as fout:
    sigma[p].tofile(outname)

  del sums, sumsq, sigma
  print("")
