#!/bin/sh

#Wcoss and gaea
#source ~/env3.12/bin/activate
#ursa
source ~/rg/env3.13/bin/activate

#GFSv17
#export expt=gfs
#stream2: 20240601-20240911
#stream3: 20241201-20250326
#realtime: 20251121-20260211
#tag=20240601
#while [ $tag -le 20250401 ]
#sfsbeta01
export expt=sfs
for tag in 20100301 20110301 20120301 20130301 20210301 20220301 20230301
do
  echo $tag

  if [ ! -f int.$tag ] ; then
    if [ -d sfs.$tag ] ; then
      time python3 integrals.py ./ sfs.$tag $tag > int.$tag
    fi
  fi

  if [ -f int.$tag ] ; then
    if [ ! -f overlay_$tag.png ] ; then
      yy=`echo $tag | cut -c1-4`
      mm=`echo $tag | cut -c5-6`
      dd=`echo $tag | cut -c7-8`
      time python3 ufsfcst.py $yy $mm $dd int.$tag
      mv overlay.png overlay_$tag.png
    fi
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
