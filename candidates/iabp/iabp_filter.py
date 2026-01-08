'''
read in a buoy file and extract all valid locations within a time window.
then write those back out
qc:
    skip if latitude > 90 or < -90
    wrap in to -180, 180
'''

import sys
import datetime

#-------------------------------------------------------------------------
# Utility functions for detecting whether file has other variables than position
def hasbp(fwords):
    ''' hasbp(fwords) -- fwords is line.split() of the buoy's header line '''
    return  'BP' in fwords
def hasts(fwords):
    ''' hasts(fwords) -- fwords is line.split() of the buoy's header line '''
    return  'Ts' in fwords
def hasta(fwords):
    ''' hastafwords) -- fwords is line.split() of the buoy's header line '''
    return  'Ta' in fwords

def nearcycle(fcycle, fincr):
  ''' nearcycle(cycle, fincr) checks to see if fincr (increment since 
      start of day) is 'near' the cycle time (hours since 00 UTC)
      cycle is hours, fincr is a timedelta. 
      RG: 'near' should be an argument. Taken as 30 min for now
      RG: Does not currently deal with wrapping across 00 UTC, 
        e.g. 2359 won't be 'near' 0000 '''
  return (abs(fincr.total_seconds()%86400 - fcycle*3600) <= 1800)

#-------------------------------------------------------------------------
# Change these
start = datetime.date(2025,1,1)
end   = datetime.date(2025,5,18)
cycle = 0 # hours UTC

#-------------------------------------------------------------------------
# Should need no changes below here

dt = datetime.timedelta(1)

# Open file
try:
  fin = open(sys.argv[1], "r", encoding='utf-8')
except:
  print("could not open ",sys.argv[1])
  sys.exit(1)

# IABP format is header line and then N lines of data. Position DOY may not match obs DOY
# Read and echo the header line
try:
    line = fin.readline()
    print(line,end="")
    # The additional variables are not being used at this point, this is a preadaptation
    # BP is buoy pressure, Ts is surface (skin) temperature, Ta is atmospheric temperature
    words = line.split()
    if hasbp(words):
        print('buoy ',sys.argv[1], 'has BP in index position ',words.index('BP'), file=sys.stderr )
        BP = words.index('BP')
    if hasts(words):
        print('buoy ',sys.argv[1], 'has Ts in index position ',words.index('Ts'), file=sys.stderr )
        Ts = words.index('Ts')
    if hasta(words):
        print('buoy ',sys.argv[1], 'has Ta in index position ',words.index('Ta'), file=sys.stderr )
        Ta = words.index('Ta')
except:
    print("readline failed",line)
    sys.exit(1)

#-------------------------------------------------------------------------
for more in fin:
  words = more.split()
  #debug: print(words[1], words[5], words[6], words[7], flush=True )
  if (float(words[6]) <= -90. or float(words[6]) >= 90.0):
      continue
  lon = float(words[7])
  if (lon < -180):
      lon += 360.
  elif (lon > 180):
      lon -= 360.
  lat = float(words[6])

  #RG: Add logic to determine whether we're near a given 'cycle' time, e.g. 00z
  obs = datetime.date(int(words[1]), 1, 1)
  incr = (float(words[5])-1.) * dt
  obs += incr
  #if (obs >= start and obs <= end and nearcycle(cycle, incr) ):
  if (end >= obs >= start and nearcycle(cycle, incr) ):
    print(words[1], words[5], lat, lon, flush=True)
