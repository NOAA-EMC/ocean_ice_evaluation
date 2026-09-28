import sys

import numpy as np
import netCDF4 as nc

def H(x):
    x[x < 0] = 0

def trim(x):
    x[x < -1.e5] = 0
    x[x > 1.e5 ] = 0

fin = nc.Dataset(sys.argv[1], "r")
lats = fin.variables['TLAT'][:,:]
lons = fin.variables['TLON'][:,:]
div = fin.variables['divu'][0,:,:]
hi  = fin.variables['hi'][0,:,:]
fin.close()

trim(div)
trim(hi)
#print('div ',div.max(), div.min() )
#print('hi  ',hi.max(), hi.min() )

div /= 86400.  # convert from per day to per second
H(div)
index1 = div
#print('div ',div.max(), div.min() )

u = div*hi
#print('u ',u.max(), u.min() )
y = u > 0
print("count of div*hi > 0 points?",y.sum() )

x = hi > 0
print("count of hi > 0 points?",x.sum() )

count = y.sum()

#----------------------------------------------------------------
def perc(x, count, crit):
  m = x > crit
  #debug: print("perc ",m.sum(), 1.-m.sum()/count, flush=True)
  return 1.-m.sum()/count

#interval halving to find critical value for a given pdf point
def halving(x, count, point):
    xmin = x.min()
    xmax = x.max()

    p = 0
    toler =  (xmax - xmin)/1.e9
    xtry = xmin + (xmax - xmin)/2.
    i = 0

    while ((xmax - xmin) > toler and i < 64):
      i += 1
      xtry = xmin + (xmax - xmin)/2.
      p = perc(x, count, xtry)
      #debug: print('i, p',i,p,flush=True)
      if (p > point):
        xmax = xtry
      else:
        xmin = xtry
    #debug: print("passes: ",i, flush=True)
    return xtry


#----------------------------------------------------------------
print("\n\n\ndiv")
print('dviu .5 ',halving(div, count, 0.5))
print('dviu .9 ',halving(div, count, 0.9))
print('dviu .99 ',halving(div, count, 0.99))
#debug: sys.exit(0)

index2 = u*u                 # pressure, dimensionally with rho
hi3 = np.power(hi, 3)
index3 = index2*hi3          # work, dimensionally with rho
index4 = index3*div          # power, dimensionally with rho

print('\n\n\npress')
print('press .5 ',halving(index2, count, 0.5))
print('press .9 ',halving(index2, count, 0.9))
print('press .99 ',halving(index2, count, 0.99))
print(perc(index2, count, 0.5) )

#debug: sys.exit(0)
print('\n\n\nwork')
print('work .5 ',halving(index3, count, 0.5))
print('work .9 ',halving(index3, count, 0.9))
print('work .99 ',halving(index3, count, 0.99))


print('\n\n\npower')
print('power .5 ',halving(index4, count, 0.5))
print('power .9 ',halving(index4, count, 0.9))
print('power .99 ',halving(index4, count, 0.99))



#debug: sys.exit(0)
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def show(x, i, bins):
  vmax = x.max()
  vmin = x.min()
  bounds = np.array(bins)
  norm   = matplotlib.colors.BoundaryNorm(boundaries = bounds, ncolors=256)
  proj = ccrs.PlateCarree()

  ax  = plt.axes(projection = proj)
  fig = plt.figure(figsize = (9,3) )
  ax = fig.add_subplot(1,1,1, projection = proj)
  cmap = matplotlib.colormaps.get_cmap('jet')

  xlocs = list(range(-180,181,30))
  ylocs = list(range(-90, 91, 15))
  ax.set_extent((-180, -60, 60, 90), crs = ccrs.PlateCarree() )

  ax.coastlines(resolution='10m')
  ax.gridlines(crs = proj, xlocs = xlocs)
  cs = ax.pcolormesh(lons, lats, x, cmap = cmap, norm = norm, transform = proj)
  cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=0.04)
  #cb.set_label('color bar label', fontsize=12)

  plt.savefig('figure_'+f"{i:d}"+".png")
  plt.close()


bins = [0, 1.e-7, 7.e-6, 1.3e-4, 11e-4, index1.max() ]
show(index1, 1, bins)

bins = [0, 1.e-13, 2.e-11, 2.e-9, 4.e-8, index2.max() ]
show(index2, 2, bins)

bins = [0, 1.e-13, 3.e-11, 2.e-9, 1.6e-7, index3.max() ]
show(index3, 3, bins)

bins = [0, 1.e-15, 1.e-14, 1.3e-13, 1.3e-11, index4.max() ]
show(index4, 4, bins)

