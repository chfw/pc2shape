# makeShape.py -- make shapefiles show regions covered by postcodes
#
# Copyright (c) 2007, David Stubbs
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution.
#     * Neither the name of David Stubbs nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import getopt
import re
import shapelib.shapelib as shp, shapelib.dbflib as dbf
import sys
import voronoi

"""Edge direction A to B (+ve)"""
AB = 1
"""Edge direction B to A (-ve)"""
BA = -1

def pullPolygon(pc, pcEdges):
    """Pulls a polygon from the list of edges passed into the function.

    Edges added to the polygon are removed from the list.

    Arguments:
      pc - the tag for the polygon: used for debugging only
      pcEdges - a list of edges. Each edge should be:
              ( (edgenum, vertex a, vertex b), edgedir )
         edgedir should be either the AB or BA constant

    Returns a tuple containing a integer indicating the polygon
    direction (-ve=anti-clockwise, +ve=clockwise), and a list
    of the vertices of the polygon in order. Depending on the input
    edges, the resulting list may or may not be closed.
    If the edge list is empty, None is returned.

    """

    if len(pcEdges) == 0:
      return (0, None)

    # initialise vertices list to first edge
    vertices = [pcEdges[0][0][1], pcEdges[0][0][2]]
    ABBA = pcEdges[0][1]
    first = vertices[0]
    last = vertices[1]
    del pcEdges[0]		# remove first edge

    # loop till we've used all the edges. Loop can break out
    # if it runs out of connected vertices.
    while len(pcEdges) > 0:

      # record length for progress checking
      before = len(pcEdges)

      # for each edge in the list see if we can attach it to
      # our shape.
      for e in pcEdges:
        if e[0][1] == first:
          vertices.insert(0, e[0][2])
          ABBA -= e[1]
          first = e[0][2]
          pcEdges.remove(e)
        elif e[0][2] == first:
          vertices.insert(0, e[0][1])
          ABBA += e[1]
          first = e[0][1]
          pcEdges.remove(e)
        elif e[0][1] == last:
          vertices.append(e[0][2])
          ABBA += e[1]
          last = e[0][2]
          pcEdges.remove(e)
        elif e[0][2] == last:
          vertices.append(e[0][1])
          ABBA -= e[1]
          last = e[0][1]
          pcEdges.remove(e)

      # check for any progress made => no progress = EOS
      if before == len(pcEdges):
        print "There are %s disconnected edges for '%s'" % (len(pcEdges), pc)
        break

    # return our results
    return (ABBA, vertices)

def groupEdges(edges, pcRE):
  """Groups edges into lists sharing a common tag.

  The edges are sorted into lists, where each edge in the list
  shares a common tag as matched by the first captured group of
  the regex. Only boundary edges are sorted (those where the
  captured group is different on each side of the edge).

  Arguments:
    edges - a list of edges as returned by the voronoi class
    pcRE - a compiled regex used to match against

  Returns a dictionary  group_name => [ (edge, edgedir) ... ]
  where edgedir is either AB or BA.

  """

  # dictionary to hold our collected regions
  matchingEdges = {}

  # loop through the edges to find qualifying ones
  # and add them to the relevant list
  for edge in edges:
    
    # find the 1st captured group for each edge side
    # if the regex doesn't match, we use an empty string
    m1 = pcRE.search(edge[3].tag)
    m2 = pcRE.search(edge[4].tag)
    pc1 = pc2 = ""
    if m1 != None:
      pc1 = m1.group(1)
    if m2 != None:
      pc2 = m2.group(1)

    # it is a boundary edge only if the tags are different
    if pc1 != pc2:
      print "boundary edge found %s -- %s (%s, %s)" % (pc1, pc2, edge[3].tag, edge[4].tag)
      edge[3].pc = pc1
      edge[4].pc = pc2
      if pc1 != "":
        if not matchingEdges.has_key(pc1):
          matchingEdges[pc1] = [(edge, AB)]
        else:
          matchingEdges[pc1].append((edge,AB))

      if pc2 != "":
        if not matchingEdges.has_key(pc2):
          matchingEdges[pc2] = [(edge, BA)]
        else:
          matchingEdges[pc2].append((edge, BA))

  return matchingEdges

def colourCodes(edges):
  connections = {}

  for (pc, pcEdges) in edges.iteritems():
    for edge, dir in pcEdges:
      pc1 = edge[3].pc
      pc2 = edge[4].pc
      if pc1 in connections:
        connections[pc1].add(pc2)
      else:
        connections[pc1] = set([pc2])
      if pc2 in connections:
        connections[pc2].add(pc1)
      else:
        connections[pc2] = set([pc1])

  graph = sorted(connections.iteritems(), lambda x, y: len(y[1])-len(x[1]))
  
  colours = { "ZZ": 20 }
  for node, neighbours in graph:
    cols_available = range(0,20)
    for n in neighbours:
      if n in colours and colours[n] in cols_available:
        cols_available.remove(colours[n])
    colours[node] = cols_available[0]

  return colours


def makeShapes(name, rawEdges, codeRegex):
  """Makes a shapefile of polylines for the given edges.

  The edges are grouped using groupEdges with the passed in
  edges and regex.

  The edges for each list are then built into polylines and
  anti-clockwise ones are written to a shapefile using the
  given name. The captured group from the regex is written
  to the shapefile dbf for each polyline.

  Arguments:
    name - the name of the shapefile (minus extension)
    rawEdges - the diagram to use, pulled straight from the
          voronoi diagram generator script
    codeRegex - the regex string to match: the first captured
          group will be used to collect regions

  Nothing is returned, but several shapefiles will be generated.

  """
  
  points = rawEdges[0]
  lines = rawEdges[1]
  edges = list(rawEdges[2])
  pcRE = re.compile(codeRegex)

  matchingEdges = groupEdges(edges, pcRE)
  colourMap = colourCodes(matchingEdges)

  # open the shape files
  # main shapefile containing the polylines
  shpFile = shp.create(name, shp.SHPT_ARC)
  dbfFile = dbf.create(name)
  dbfFile.add_field("NAME", dbf.FTString, 10, 0)
  dbfFile.add_field("COLOUR", dbf.FTString, 3, 0)

  # a shapefile containing all the raw edges for debugging
  edgeShpFile = shp.create(name+"_edges", shp.SHPT_ARC)
  edgeDbf = dbf.create(name+"_edges")

  # a shapefile containing the label points for each polyline region
  centerFile = shp.create(name+"_cen", shp.SHPT_POINT)
  centerDbf = dbf.create(name+"_cen")
  centerDbf.add_field("NAME", dbf.FTString, 10, 0)

  for (pc, pcEdges) in matchingEdges.iteritems():

    # dump all matching edges for debug
    for e in pcEdges:
      if e[0][1] >= 0 and e[0][2] >= 0:
        v1 = (points[e[0][1]][1], points[e[0][1]][0])
        v2 = (points[e[0][2]][1], points[e[0][2]][0])
        edgeObj = shp.SHPObject(shp.SHPT_ARC, 1, [[v1, v2]])
        edgeShpFile.write_object(-1, edgeObj)

    # try to sort the edges. The loop breaks out when pullPolygon
    # is completed
    while True:
      (ABBA, vertices) = pullPolygon(pc, pcEdges)
      if vertices == None:
        break

      print "Sorted '%s' into %s vertices, dir is %s, colour is %s" % (pc, len(vertices), ABBA, chr(ord("A")+colourMap[pc]))
      # only anti-clockwise polylines represent regions
      if ABBA > 0:
        print "Represents a hole: skipping"
        continue

      # from the vertex numbers pull the actual coordinates
      # vertex maybe "0" -- which is irritating... drop these for now
      regionPoints = []
      for i in vertices:
        print i,
        if i >= 0 and i < len(points):
          regionPoints.append((points[i][1], points[i][0]))
          print i, points[i],
        print "."

      # output line to the shapefile
      obj = shp.SHPObject(shp.SHPT_ARC, 1, [list(regionPoints)])
      n = shpFile.write_object(-1, obj)
      dbfFile.write_record(n, {'NAME': pc})
      dbfFile.write_record(n, {'COLOUR': chr(ord("A")+colourMap[pc])})
      print "object written (%s), extent %s" % (n, obj.extents())

      # calculate a centre point and write it to a shapefile
      min,max = obj.extents()
      cenP = shp.SHPObject(shp.SHPT_POINT, 1, [[ ( (min[0]+max[0])/2, (min[1]+max[1])/2 ) ]])
      m = centerFile.write_object(-1, cenP)
      centerDbf.write_record(m, {'NAME': pc})

  # close the shapefiles
  edgeShpFile.close()
  shpFile.close()
  dbfFile.close()
  centerFile.close()
  centerDbf.close()

def usage():
  print """
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
"""

if __name__=="__main__":

    try:
        optlist,args = getopt.getopt(sys.argv[1:],"thdp")
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    from mapnik import Projection, Coord
    p = Projection("+proj=merc")
    
    pts = []
    fp = sys.stdin
    if len(args) > 0:
        fp = open(args[0],'r')
    for line in fp:
        fld = line.split()
        c = Coord(float(fld[1]), float(fld[0]))
        c = p.forward(c)

        #x = float(fld[0])
        #y = float(fld[1])

        tag = " ".join(fld[2:])
        pts.append(voronoi.Site(c.y,c.x,0,tag))
    if len(args) > 0: fp.close()

    result = voronoi.computeVoronoiDiagram(pts)

    makeShapes("postcode-XX", result, "^([A-Z][A-Z]?).*")
    makeShapes("postcode-XXNN", result, "^([A-Z][A-Z]?[0-9][A-Z0-9]?).*")
    makeShapes("postcode-XXNN-N", result, "^([A-Z][A-Z]?[0-9][A-Z0-9]? [0-9]).*")
