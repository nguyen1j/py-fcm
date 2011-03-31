from numpy import reshape, max, loadtxt, eye
from numpy.linalg import solve, inv
from fcmexceptions import CompensationError
from util import TransformNode
from StringIO import StringIO

def get_spill(text):
    """Extracts spillover matrix from FCS text entry.

    Returns (spillover matrix S, column headers)
    """
    spill = text.split(',')
    n = int(spill[0])
    markers = spill[1:(n + 1)]
    markers = [item.strip().replace('\n', '') for item in markers]
    items = [item.strip().replace('\n', '') for item in spill[n + 1:]]
    S = reshape(map(float, items), (n, n))
    return S, markers

def compensate(fcm, S=None, markers=None, comp=False, scale=False):
    """Compensate data given spillover matrix S and markers to compensate
    If S, markers is not given, will look for fcm.annotate.text['SPILL']
    """
    if S is None and markers is not None:
        msg = 'Attempted compnesation on markers without spillover matrix'
        raise CompensationError(msg)
    if S is None:
        S, m = get_spill(fcm.annotate.text['SPILL'])
        if markers is None:
            markers = m
    idx = fcm.name_to_index(markers)

    c = _compensate(fcm.view()[:, idx], S, comp, scale)
    new = fcm.view()[:]
    new[:, idx] = c
    node = TransformNode('', fcm.get_cur_node, new)
    fcm.add_view(node)
    return new

def _compensate(data, spill, comp=False, scale=False):
    if scale and not comp:
        spill = spill / max(spill)
    if comp:
        spill = inv(spill)

    #return dot(data,spill)
    # return solve(spill,data.T).T

    return solve(spill.T, data.T).T

def gen_spill_matrix(tubes, unstained):
    """
    Generates spill matrix and indexs capabale of being passed to loadFCS
    takes a dictionary of FCMData objects with keys corresponding to the 
    channel short name, and a FCMData object corresponding to the unstained
    beads.
    returns a list of channel short names, and an a spillover matrix
    """
    names = {}
    files = {}
    for j in tubes.keys():
        data = tubes[j]
        files[j] = data
        d = None
        try:
            #look up which channel we actually are.
            for m,n in data.notes.text.viewitems():
                if m.startswith('p') and m.endswith('n'):
                    if j == n:
                        d = int(m[1:-1])-1
                        names[d] = j
                elif m.startswith('p') and m.endswith('s'):
                    if j == n:
                        d = int(m[1:-1])-1
                        names[d] = j
        except KeyError:
            pass
        except AttributeError:
            pass

        if d is None:
            raise ValueError('Cant look up the channel name')
    
    
    idxs = names.keys()
    idxs.sort()
    base = unstained[:,idxs].mean(0)
    spill = eye(len(idxs))
    for k,d in enumerate(idxs):
        
        data = files[names[d]]
        norm = (data[:, idxs].mean(0)-base)[k]
        
        spill[k, :] = (data[:, idxs].mean(0)-base) / norm
        
    return [names[i] for i in idxs], spill


def load_compensate_matrix(file_name):
    """
    Load a compensation matrix from a text file like those generated by flowjo
    Returns a list of markers and a compensation matrix
    
    """

    file = open(file_name, mode='Ur')
    unused = file.readline()
    file.readline() # skip <\t>\n line
    markers = file.readline().strip('\n').split('\t')
    size = len(markers)
    mat = ''
    for unused in range(size):
        mat = mat + file.readline()

    return(markers, loadtxt(StringIO(mat)))
