import re
import logging
import os
from warnings import warn

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(message)s',
                    filename=os.path.join('.', 'fcm.log'),
                    filemode='a')

def fcmlog(func):
    """This decorator logs call to methods with full argument list."""
    def g(*args, **kwargs):
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        logging.info(func.func_name + '(' + ', '.join(
                '%s=%r' % entry
                for entry in zip(argnames,args) + kwargs.items()) + ')')
        return func(*args, **kwargs)
    return g
        
class Node(object):
    """
    base node object
    """

    def __init__(self, name, parent, data):
        self.name = name
        self.parent = parent
        self.data = data
        self.prefix= 'n'
    
    def view(self):
        """
        return the view of the data associated with this node
        """
        
        return self.data
    
    def pprint(self, depth):
        return "  "*depth + self.name + "\n"
    
    def __getattr__(self, name):
        if name == 'channels':
            return self.parent.channels
        else:
            raise AttributeError("'%s' has no attribue '%s'" %(str(self.__class__), name))
    
class RootNode(Node):
    """
    Root Node
    """
    def __init__(self, name, data, channels):
        self.name = name
        self.parent = None
        self.data = data
        self.channels = channels
        self.prefix='root'
        
class TransformNode(Node):
    """
    Transformed Data Node
    """
    
    def __init__(self, name, parent,  data):
        self.name = name
        self.parent = parent
        self.data = data
        self.prefix = 't'
        
class SubsampleNode(Node):
    """
    Node of subsampled data
    """
    
    def __init__(self, name, parent, param):
        self.name = name
        self.parent = parent
        self.param = param
        self.prefix = 's'
        if type(param) == tuple:
            self.channels = self.parent.channels[param[1]]
        
    def view(self):
        """
        return the view of the data associated with this node
        """
        return self.parent.view().__getitem__(self.param)
    
class DropChannelNode(Node):
    """
    Node of data removing specific channels
    """
    
    def __init__(self, name, parent, param, channels):
        self.name = name
        self.parent = parent
        self.param = param
        self.prefix = 'd'
        self.channels = channels
    
    def view(self):
        """
        return the view of the data associated with this node
        """
        return self.parent.view()[:,self.param]
    
    
class GatingNode(Node):
    """
    Node of gated data
    """
    
    def __init__(self, name, parent, data):
        self.name = name
        self.parent = parent
        self.data = data
        self.prefix = 'g'
        
    def view(self):
        """
        return the view of the data associated with this node
        """
        return self.parent.view()[self.data]
        
class Tree(object):
    '''Tree of data for FCMdata object.'''

    def __init__(self, pnts, channels):
        self.nodes = {}
        self.root = RootNode('root', pnts, channels)
        self.nodes['root'] = self.root
        self.current = self.root

    def parent(self):
        '''return the parent of a node'''
        return self.current.parent

    def children(self , node =None):
        '''return the children of a node'''
        if node == None:
            node = self.current
        return [i for i in self.nodes.values() if i.parent == node]

    def visit(self, name):
        '''visit a node in the tree'''
        if type(name) is type(''):
            self.current = self.nodes[name]
        else: 
            self.current = name

    def get(self, name = None):
        '''return the current node object'''
        if name is None:
            return self.current
        else:
            if name in self.nodes.keys():
                return self.nodes[name]
            else:
                raise KeyError, 'No node named %s' % name
    
    def view(self):
        '''Return a view of the current data'''
        return self.current.view()

    def add_child(self, name, node):
        '''Add a node to the tree at the currently selected node'''
        if name == '':
            prefix = node.prefix
            pat = re.compile(prefix + "(\d+)")
            matches = [pat.search(i) for i in self.nodes.keys()]
            matches = [i for i in matches if i is not None]
            if len(matches) is not 0:
                n = max([ int(i.group(1)) for i in matches])
                name = prefix + str(n+1)
            else:
                name = prefix + '1'
        if name in self.nodes.keys():
            raise KeyError, 'name, %s, already in use in tree' % name
        else:
            node.name = name
            self.nodes[name] = node
            node.parent = self.current
            self.current = self.nodes[name]
        
    def rename_node(self, old_name, new_name):
        """
        Rename a node name
        D(old,new) -> rename old to new
        """
        if not self.nodes.has_key(old_name):
            # we don't have old_name...
            raise KeyError, 'No node named %s' % old_name
        if self.nodes.has_key(new_name):
            raise KeyError, 'There already is a node name %s' % new_name
        else:
            self.nodes[new_name] = self.nodes[old_name] # move node
            self.nodes[new_name].name = new_name # fix it's name
            del self.nodes[old_name] # remove old node.
                

    def pprint(self):
        return self._rpprint(self.root, 0)
        
    def _rpprint(self, n, d):
        tmp = n.pprint(d)
        for i in self.children(n):
            tmp+= self._rpprint(i,d+1)
        return tmp
        
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    t = Tree(RootNode('root',[0,0,0]))
    t.add_child('gate1', RootNode('gate1',[1,2,3]))
    t.add_child('gate11', RootNode('gate11',[4,5,6]))
    t.visit('root')
    t.add_child('gate2', RootNode('gate2',[2,3,4]))
    t.add_child('gate21', RootNode('gate21',[3,4,5]))
    t.add_child('gate211', RootNode('gate211',[4,5,6]))

    parent = t.parent()
    print t.current
    print t.parent()
    t.visit(t.parent())
    print t.current
    print t.parent()
    t.visit('root')
    print t.current
    print t.children()
    print t.view()
    t.visit('gate2')
    print t.view()
    
    t.rename_node('gate1', 'foo')
    t.visit('foo')
    print t.current
    print t.view()

    
    
    
