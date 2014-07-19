Post Code to Shapefile
=======================

# DISCLAIMER

*NO GUARANTEE GRANTED. I DID NOT PROMISE TO SOLVE ANY OF YOUR PROBLEMS BY THIS SHARING ALTHOUGH I HOPE IT HELPS YOU IN ANY WAY.*

# Intallation

1. install shapelib

shapelib was included for quick start only. If you happen to view this repository in distant future, say 2018, you are on your own. Please refer to later section for clues.

```
 tar xzvf shapelib-1.3.0.tgz
 cd shapelib-1.3.0/pyshapelib-0.3
 python setup.py build
 python setup.py install
```

2. install mapnik2 

 please follow this detailed <a href="http://wiki.openstreetmap.org/wiki/Mapnik/Installation">wiki link</a>

3. install requirements

```
  pip install `cat requirements.txt`
```

Then you are ready to use the makeShapeColoured.py

# clues for Shapelib

Please follow the page here to get latest code of Shapelib:

```
http://download.osgeo.org/shapelib/
```

Please download pyshapelib-0.3:

```
https://mail.python.org/pipermail/python-announce-list/2004-May/003129.html
```

# License

With the repect to makeShape.py, I used BSD license. Please respect individual licenses of the included code

# KNOWN PROBLEM 

```
Traceback (most recent call last):
  File "makeShapeColoured.py", line 349, in <module>
    result = voronoi.computeVoronoiDiagram(pts)
  File "/home/kev/osm/voronoi.py", line 746, in computeVoronoiDiagram
    voronoi(siteList,context)
  File "/home/kev/osm/voronoi.py", line 206, in voronoi
    edge = Edge.bisect(bot,newsite)
  File "/home/kev/osm/voronoi.py", line 404, in bisect
    newedge.a = dx/dy
ZeroDivisionError: float division
```

It means that you have duplicated geocoordinates in your input. Remove them!!

Reference:

http://web.archiveorange.com/archive/v/shBzDhEFxm5GxY3hiK5b

# Usage

Create shapefiles of postcode boundaries from a list of postcodes:

Usage:
	makeShape.py [filename]

If filename is not supplied then list is read from stdin.

The post code list should be supplied with one post code per line:
   <latitude> <longitude> <post code>

Example:
   51.5 0.15 SE16
   51.51 0.154 SE16 9XX

The result will be several shapefiles. For each file described
below there will be .shp .shx .dbf

  postcode-XX: shapefiles for the first two letters
  postcode-XXNN: shapefiles for the post code first part
  postcode-XXNN-N: shapefiles for the post code minus the last
        two letters

  postcode-XX_cen (etc): label positions for each region
  postcode-XX_edges (etc): all edges unsorted for each region

# ORIGINAL README

This code takes a list of postcodes and outputs a pile of
shapefiles representing postcode regions.

For licensing read the file comments at the top, but basically:
  makeShape.py (BSD license)
  voronoi.py (derived from Bell Labs code)
  mapnik-postcodes.xml (PD, do with as you please)
  mangleNPEData.sh (PD, do with as you please)

Dependencies:
  python
  mapnik (with Projection python bindings)
  pyshapelib (and therefore shapelib)

To generate a map first get a list of postcodes with lon/lats.
Suggested sources:
   http://www.npemap.org.uk/
   http://www.freethepostcode.org/

Make the data into a suitable form for input into makeShape.py
See: 'python makeShape.py -h' for details.

(If you got your data from NPE maps site you can run it through
the mangleNPEData.sh script)

Run makeShape.py on your data. You will now have a pile of
postcode shapefiles in your directory.

You can then use mapnik, or any other tool of your choice, to
visualise the data. I used the generate_tiles script from OSM
to make google style tiles for overlay on a slippy map. The
mapnik-postcodes.xml mapnik map description file can be used
in conjunction with this.
