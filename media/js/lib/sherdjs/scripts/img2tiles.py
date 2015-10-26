#!/usr/bin/python
"""
batch processing might look something like this:
ls *.jpg *.JPG |grep -v preview|grep -v thumbnail|grep -v 2000x2000 |awk -F. '{print "img2tiles.py \"" $1 "." $2 "\" \"tiles/" $1"\""}' |bash

"""
import os
import math
import sys
from subprocess import call

from PIL import Image
simulate = False

imglocation = sys.argv[1]
dest_dir = '.'
if len(sys.argv) > 2:
    dest_dir = sys.argv[2]
    if not os.path.isdir(dest_dir) and not simulate:
        os.makedirs(dest_dir)

FILE_ZDIR = '%s/z%d'
FILE_YDIR = '%s/y%d'
FILE_TMP = '%s/%s-%d.png'
FILE_FINAL = '%s/y%d/x%d.png'

pil_image = Image.open(imglocation)
w,h = pil_image.size
wzoom = math.ceil(math.log(w,2) -8 )
hzoom = math.ceil(math.log(h,2) -8 )
maxzoom = max(wzoom,hzoom)

tiles_across = math.ceil(w/256.0) 
tiles_down = math.ceil(h/256.0)
print 'width: %d, height: %d' % (w,h)
print wzoom, hzoom, maxzoom
tile = 256.0

for zoom in range(int(maxzoom),-1,-1):#count down
    print tiles_across, tiles_down
    tiles_squared = tiles_across*tiles_down
    z_dir = FILE_ZDIR % (dest_dir,zoom)
    #MAKE Z DIR
    if not os.path.isdir(z_dir):
        if not simulate:
            os.makedirs(z_dir)

    #IMAGEMAGICK CALLS
    tsize = int(tile)
    perc = 256*100.0/tsize
    convert_calls = [
        ['convert','-crop','%dx%d' % (tsize,tsize),'+gravity',imglocation, 
         FILE_TMP.replace('%d','%%d') % (z_dir,'a')],
        ['convert','-resize','%.4f%%x%.4f%%' % (perc,perc)],
        ]

    print convert_calls[0]
    if not simulate:
        call(convert_calls[0])
    else:
        print convert_calls[1]

    for i in range(0, int(tiles_squared)):
        convert_calls[1][3:5] = [FILE_TMP % (z_dir,"a",i),
                                 FILE_TMP % (z_dir,"ba",i)
                                 ]
        if simulate:
            print convert_calls[1]
        else:
            call(convert_calls[1])
            os.remove( FILE_TMP % (z_dir,"a",i) )

    #MAKE Y DIRS
    for ys in range(0,int(tiles_down)):
        y_dir = FILE_YDIR % (z_dir,ys)
        if not os.path.isdir(y_dir):
            if simulate:
                print "mkdir %s" % y_dir
            else:
                os.makedirs(y_dir) #y coord

    #RENAME FILES INTO Y DIRS
    for i in range(0, int(tiles_squared)):
        x = i % tiles_across
        y = i / tiles_across

        fname = FILE_TMP % (z_dir,"ba",i)
        new_name = FILE_FINAL % (z_dir,y,x)
        #print "mv %s %s" %(fname,new_name)
        if not simulate:
            if os.path.isfile(fname): 
                os.rename(fname, new_name)
            else:
                print 'Failed!'
                print fname


    #if tail-recursion is awesome, then
    # changing state at the bottom of a loop for the next
    # one, must also be awesome....
    tiles_across = math.ceil(tiles_across/2.0)
    tiles_down = math.ceil(tiles_down/2.0)
    tile = tile * 2

