import numpy
from matplotlib.nxutils import points_inside_poly
from util import GatingNode

from enthought.traits.api import HasTraits, List, ListInt, Array

class Gate(HasTraits):
    """An object representing a gatable region"""
    vert = Array()
    chan = ListInt(minlen=2, maxlen=2)
    def __init__(self, vert, channels):
        """
        An object representing a gatable region
        
        vert = numpy.array((k,2)): verticies of gating region
        channels = touple of indicies of channels to gate on
        """
        self.vert = vert
        self.chan = channels
        
    def gate(self, fcm, chan = None):
        """
        return gated region of FCM data
        """
        if chan is None:
            chan = self.chan
        idxs = points_in_poly(self.vert, fcm.view()[:, chan])

        # matplotlib has points in poly routine in C
        # no faster than our numpy version
        # idxs = points_inside_poly(fcm.pnts[:, chan], self.vert)
        
        node = GatingNode("", fcm.get_cur_node(), idxs)
        fcm.add_view(node)
        return fcm
        
class QuadGate(Gate):
    """
    An object to divide a region to four quadrants
    """
    def __init__(self, vert, channels):
        self.vert = vert
        self.chan = channels
        
    def gate(self, fcm, chan = None):
        """
        return gated region
        """
        if chan is None:
            chan = self.chan
        # I (+,+), II (-,+), III (-,-), and IV (+,-)
        x = fcm.view()[:,chan[0]]
        y = fcm.view()[:,chan[1]]
        quad = {}
        quad[1] = (x>self.vert[0]) & (y>self.vert[1]) # (+,+)
        quad[2] = (x<self.vert[0]) & (y>self.vert[1]) # (-,+)
        quad[3] = (x<self.vert[0]) & (y<self.vert[1]) # (-,-)
        quad[4] = (x>self.vert[0]) & (y<self.vert[1]) # (+,-)
        root = fcm.get_cur_node()
        name = root.name
        for i in quad.keys():
            if True in quad[i]:
                fcm.tree.visit(name)
                node = GatingNode("q%d" % i, root, quad[i])
                fcm.add_view(node)
        

def points_in_poly(vs, ps):
    """Return boolean index of events from ps that are inside polygon with vertices vs.

    vs = numpy.array((k, 2))
    ps = numpy.array((n, 2))
    """

    # optimization to check only events within bounding box
    # for polygonal gate - useful if gating region is small
    # area_ratio_threshold = 0.5
    # area_gate_bb = numpy.prod(numpy.max(vs, 0) - numpy.min(vs, 0))
    # area_gate_ps = numpy.prod(numpy.max(ps, 0) - numpy.min(ps, 0))
    # if area_gate_bb/area_gate_ps < area_ratio_threshold:
    #     idx = numpy.prod((ps > numpy.min(vs, 0)) & (ps < numpy.max(vs, 0)),1)
    #     ps = ps[idx.astype('bool'), :]

    j = len(vs) - 1
    inPoly = numpy.zeros((len(vs), len(ps)), 'bool')

    for i, v in enumerate(vs):
        inPoly[i,:] |= ((v[0] < ps[:,0]) & (vs[j,0] >= ps[:,0])) | ((vs[j,0] < ps[:,0]) & (v[0] >= ps[:,0]))
        inPoly[i,:] &= (v[1] + (ps[:,0] - v[0])/(vs[j,0] - v[0])*(vs[j,1] - v[1]) < ps[:,1])
        j = i

    return numpy.bitwise_or.reduce(inPoly, 0)

if __name__ == '__main__':
    vertices = numpy.array([[2,2],[10,2],[10,10],[2,10]], 'd')
    points = numpy.random.uniform(0, 10, (10000000, 2))

    import time
    start = time.clock()
    inside =  points_in_poly(vertices, points)
    print "Time elapsed: ", time.clock() - start
    print numpy.sum(inside)

