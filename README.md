pc2shape
========

# DISCLAIMER

## NO GUARANTEE GRANTED. I DID NOT PROMISE TO SOLVE ANY OF YOUR PROBLEMS BY THIS SHARING ALTHOUGH I HOPE IT HELPS YOU IN ANY WAY.

# Intallation


1. install shapelib

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

# Shapelib - the only troublesome dependency:

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
