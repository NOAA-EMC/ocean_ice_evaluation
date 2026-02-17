#!/bin/sh

source ~/env3.12/bin/activate

#stream2: 20240601-20240911
#stream3: 20241201-20250326
#realtime: 20251121-20260211
tag=20240601
while [ $tag -le 20250401 ]
do
  echo $tag

  if [ ! -f int.$tag ] ; then
    if [ -d gfs.$tag ] ; then
      time python3 integrals.py gfs.$tag $tag > int.$tag
    fi
  fi

  if [ -f int.$tag ] ; then
    if [ ! -f overlay_$tag.png ] ; then
      yy=`echo $tag | cut -c1-4`
      mm=`echo $tag | cut -c5-6`
      dd=`echo $tag | cut -c7-8`
      time python3 gfsfcst.py $yy $mm $dd int.$tag
      mv overlay.png overlay_$tag.png
    fi
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
