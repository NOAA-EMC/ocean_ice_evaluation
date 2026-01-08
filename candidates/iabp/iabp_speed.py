'''
read in a thinned buoy file and its positions
examine displacements for extreme values (high or low)

check: 
delta t is reasonable
speed is reasonable
time is monotonic in data file

fix:
use real distance computation
'''

#from math import sin, cos, atan2, sqrt, pi
import sys
import datetime

from utility import harcdis, bearing
import latpt

#-----------------------------------------------------------------
## to add to utility
#def bearing(x1, x2):
#    dlon = x2.lon - x1.lon
#    # must change to radians
#    rpdg = pi/180.
#    theta = atan2(sin(dlon*rpdg)*cos(x2.lat*rpdg) ,
#                  cos(x1.lat*rpdg)*sin(x2.lat*rpdg) -
#                  sin(x1.lat*rpdg)*cos(x2.lat*rpdg)*cos(dlon*rpdg) )
#    return theta/rpdg

#-----------------------------------------------------------------
# format is header line and then N lines of data. Position DOY may not match obs DOY
start = datetime.datetime(2025,1,1)
end   = datetime.datetime(2025,4,23)
splim = 1.0   # fastest allowed ice drift
dtlim = 1800. # minimum time separation between obs
#-----------------------------------------------------------------

# Open file
try:
  fin = open(sys.argv[1], "r", encoding='utf-8')
except:
  print("could not open ",sys.argv[1])
  sys.exit(1)

# Read and echo the header line
try:
    line = fin.readline()
except:
    print("readline failed")
    sys.exit(1)
#-----------------------------------------------------------------

dt  = datetime.timedelta(1)
k   = 0
for more in fin:
  words = more.split()
  obs = datetime.datetime(int(words[0]), 1, 1)
  obs += (float(words[1])-1.) * dt
  position = ( float(words[2]), float(words[3]) )
  #print(position)
  if (k == 0):
    prev_obs = obs
    prev_position = position
  else:
    #RG: watch this for days vs hours, monotonicity, ...
    delta = (obs - prev_obs).total_seconds()
    dlat = position[0]-prev_position[0]
    dlon = position[1]-prev_position[1]

    if (obs > prev_obs):
      #speed = calculate_distance(position, prev_position) /delta
      p1 = latpt.latpt(position[0], position[1])
      p2 = latpt.latpt(prev_position[0], prev_position[1])
      dist  = harcdis(p1, p2)*1000. # harcdis is in km
      speed = dist /delta
      direction = bearing(p1, p2)
    else:
      speed = 0.
      direction = 0.

    if (dlat != 0 and dlon != 0 and delta >= 3600 and speed <= splim):
      print(f"{k:5d}", obs.strftime("%Y%m%d"), obs.strftime("%H%M%S"), \
            f"{delta:5.0f}", f"{dist:7.2f}", f"{direction:.5f}", f"{speed:.5f}" )
    elif (speed > splim):
      print(k,'zzz',position, prev_position, delta, dlat, dlon, speed)

    prev_position = position
    prev_obs      = obs

  k += 1
