# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/WorkflowGraph/pydot.py
# Compiled at: 2005-10-20 11:39:16
"""Graphviz's dot language Python interface. (Python 2.1 edition)

This module provides with a full interface to create handle modify
and process graphs in Graphviz's dot language.

References:

pydot Homepage: http://www.dkbza.org/pydot.html
Graphviz:       http://www.research.att.com/sw/tools/graphviz/
DOT Language:   http://www.research.att.com/~erg/graphviz/info/lang.html

Programmed and tested with Graphviz 1.12 and Python 2.3.3 on GNU/Linux
by Ero Carrera (c) 2004 [ero@dkbza.org]

Distributed under MIT license [http://opensource.org/licenses/mit-license.html].
"""
from __future__ import nested_scopes
__author__ = 'Ero Carrera'
__version__ = '0.9.4 (Python 2.1)'
__license__ = 'MIT'
import os, tempfile, copy
from types import StringType, UnicodeType
True = 1
False = 0

def graph_from_edges(edge_list, node_prefix='', directed=False):
    """Creates a basic graph out of an edge list.
        
        The edge list has to be a list of tuples representing
        the nodes connected by the edge.
        The values can be anything: bool, int, float, str.
        
        If the graph is undirected by default, it is only
        calculated from one of the symmetric halves of the matrix.
        """
    if directed:
        graph = Dot(type='digraph')
    else:
        graph = Dot(type='graph')
    for edge in edge_list:
        e = Edge(node_prefix + str(edge[0]), node_prefix + str(edge[1]))
        graph.add_edge(e)

    return graph
    return


def graph_from_adjacency_matrix(matrix, node_prefix='', directed=False):
    """Creates a basic graph out of an adjacency matrix.
        
        The matrix has to be a list of rows of values
        representing an adjacency matrix.
        The values can be anything: bool, int, float, as long
        as they can evaluate to True or False.
        """
    node_orig = 1
    if directed:
        graph = Dot(type='digraph')
    else:
        graph = Dot(type='graph')
    for row in matrix:
        if not directed:
            skip = matrix.index(row)
            r = row[skip:]
        else:
            skip = 0
            r = row
        node_dest = skip + 1
        for e in r:
            if e:
                graph.add_edge(Edge(node_prefix + str(node_orig), node_prefix + str(node_dest)))
            node_dest += 1

        node_orig += 1

    return graph
    return


def graph_from_incidence_matrix(matrix, node_prefix='', directed=False):
    """Creates a basic graph out of an incidence matrix.
        
        The matrix has to be a list of rows of values
        representing an incidence matrix.
        The values can be anything: bool, int, float, as long
        as they can evaluate to True or False.
        """
    node_orig = 1
    if directed:
        graph = Dot(type='digraph')
    else:
        graph = Dot(type='graph')
    for row in matrix:
        nodes = []
        c = 1
        for node in row:
            if node:
                nodes.append(c * node)
            c += 1
            nodes.sort()

        if len(nodes) == 2:
            graph.add_edge(Edge(node_prefix + str(abs(nodes[0])), node_prefix + str(nodes[1])))

    if not directed:
        graph.set_simplify(True)
    return graph
    return


def find_graphviz():
    """Locate Graphviz's executables in the system.

        Attempts  to locate  graphviz's  executables in a Unix system.
        It will look for 'dot', 'twopi' and 'neato' in all the directories
        specified in the PATH environment variable.
        It will return a dictionary containing the program names as keys
        and their paths as values.
        """
    progs = {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': ''}
    if not os.environ.has_key('PATH'):
        return None
    sep = '/'
    for path in os.environ['PATH'].split(os.pathsep):
        for prg in progs.keys():
            if os.path.exists(path + sep + prg):
                progs[prg] = path + sep + prg
            elif os.path.exists(path + sep + prg + '.exe'):
                progs[prg] = path + sep + prg + '.exe'

    return progs
    return


class Common:
    """Common information to several classes.
        
        Should not be directly used, several classes are derived from
        this one.
        """
    __module__ = __name__
    chars_ID = None
    parent_graph = None

    def char_range(self, a, b):
        """Generate a list containing a range of characters.
                
                Returns a list of characters starting from 'a' up to 'b'
                both inclusive.
                """
        return map(chr, range(ord(a), ord(b) + 1))
        return

    def is_ID(self, s):
        """Checks whether a string is an dot language ID.
                
                It will check whether the string is solely composed
                by the characters allowed in an ID or not.
                """
        if not self.chars_ID:
            self.chars_ID = self.char_range('a', 'z') + self.char_range('A', 'Z') + self.char_range('0', '9') + ['_']
        for c in s:
            if c not in self.chars_ID:
                return False

        return True
        return


class Error(Exception):
    """General error handling class.
        """
    __module__ = __name__

    def __init__(self, value):
        self.value = value
        return

    def __str__(self):
        return self.value
        return


class Node(Common):
    """A graph node.
        
        This class represents a graph's node with all its attributes.
        
        node(name, attribute=value, ...)
        
        name: node's name
        
        All the attributes defined in the Graphviz dot language should
        be supported.
        """
    __module__ = __name__
    attributes = [
     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 
     17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 
     31, 32, 33]

    def __init__(self, name, **attrs):
        self.name = name
        for attr in self.attributes:
            setattr(self, attr, None)
            setattr(self, 'set_' + attr, (lambda x, a=attr: setattr(self, a, x)))
            setattr(self, 'get_' + attr, (lambda a=attr: getattr(self, a)))

        for (attr, val) in attrs.items():
            setattr(self, attr, val)

        return

    def set_name(self, node_name):
        """Set the node's name."""
        self.name = node_name
        return

    def get_name(self):
        """Get the node's name."""
        return self.name
        return

    def set(self, name, value):
        """Set an attribute value by name.
                
                Given an attribute 'name' it will set its value to 'value'.
                There's always the possibility of using the methods:
                        set_'name'(value)
                which are defined for all the existing attributes.
                """
        if name in self.attributes:
            self.__dict__[name] = value
            return True
        return False
        return

    def to_string(self):
        """Returns a string representation of the node in dot language.
                """
        if not isinstance(self.name, StringType):
            self.name = str(self.name)
        if self.name == 'node' or self.name == 'edge':
            node = self.name
        else:
            node = '"' + self.name + '"'
        node_attr = None
        for attr in self.attributes:
            if self.__dict__.has_key(attr) and getattr(self, attr) is not None:
                if not node_attr:
                    node_attr = ''
                else:
                    node_attr += ', '
                node_attr += attr + '='
                val = self.__dict__[attr]
                if (isinstance(val, StringType) or isinstance(val, UnicodeType)) and not self.is_ID(val):
                    node_attr += '"' + val + '"'
                else:
                    node_attr += str(val)

        if node_attr:
            node += ' [' + node_attr + ']'
        node += ';'
        return node
        return


class Edge(Common):
    """A graph edge.
        
        This class represents a graph's edge with all its attributes.
        
        edge(src, dst, attribute=value, ...)
        
        src: source node's name
        dst: destination node's name
        
        All the attributes defined in the Graphviz dot language should
        be supported.
        
        Attributes can be set through the dynamically generated methods:
        
         set_[attribute name], i.e. set_label, set_fontname
         
        or using the instance's attributes:
        
         Edge.[attribute name], i.e. edge_instance.label, edge_instance.fontname
        """
    __module__ = __name__
    attributes = [
     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 
     17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 
     31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 
     45, 46, 47, 48]

    def __init__(self, src, dst, **attrs):
        self.src = src
        self.dst = dst
        for attr in self.attributes:
            setattr(self, attr, None)
            setattr(self, 'set_' + attr, (lambda x, a=attr: setattr(self, a, x)))
            setattr(self, 'get_' + attr, (lambda a=attr: getattr(self, a)))

        for (attr, val) in attrs.items():
            setattr(self, attr, val)

        return

    def get_source(self):
        """Get the edges source node name."""
        return self.src
        return

    def get_destination(self):
        """Get the edge's destination node name."""
        return self.dst
        return

    def __eq__(self, edge):
        """Compare two edges.
                
                If the parent graph is directed, arcs linking
                node A to B are considered equal and A->B != B->A
                
                If the parent graph is undirected, any edge
                connecting two nodes is equal to any other
                edge connecting the same nodes, A->B == B->A
                """
        if not isinstance(edge, Edge):
            raise Error, "Can't compare and edge to a non-edge object."
        if self.parent_graph.type == 'graph':
            if self.src == edge.src and self.dst == edge.dst or self.src == edge.dst and self.dst == edge.src:
                return True
        elif self.src == edge.src and self.dst == edge.dst:
            return True
        return False
        return

    def set(self, name, value):
        """Set an attribute value by name.
                
                Given an attribute 'name' it will set its value to 'value'.
                There's always the possibility of using the methods:
                        set_'name'(value)
                which are defined for all the existing attributes.
                """
        if name in self.attributes:
            self.__dict__[name] = value
            return True
        return False
        return

    def parse_node_ref(self, node_str):
        if not isinstance(node_str, StringType):
            node_str = str(node_str)
        if node_str[0] == '"' and node_str[-1] == '"' and node_str[0].count('"') % 2 != 0:
            return node_str
        node_port_idx = node_str.rfind(':')
        if node_port_idx > 0 and node_str[0] == '"' and node_str[node_port_idx - 1] == '"':
            return node_str
        node_str = node_str.replace('"', '')
        if node_port_idx > 0:
            a = node_str[:node_port_idx]
            b = node_str[node_port_idx + 1:]
            if self.is_ID(a):
                node = a
            else:
                node = '"' + a + '"'
            if self.is_ID(b):
                node += ':' + b
            else:
                node += ':"' + b + '"'
            return node
        return '"' + node_str + '"'
        return

    def to_string(self):
        """Returns a string representation of the edge in dot language.
                """
        src = self.parse_node_ref(self.src)
        dst = self.parse_node_ref(self.dst)
        edge = src
        if self.parent_graph and self.parent_graph.type and self.parent_graph.type == 'digraph':
            edge += ' -> '
        else:
            edge += ' -- '
        edge += dst
        edge_attr = None
        for attr in self.attributes:
            if self.__dict__.has_key(attr) and getattr(self, attr) is not None:
                if not edge_attr:
                    edge_attr = ''
                else:
                    edge_attr += ', '
                edge_attr += attr + '='
                val = self.__dict__[attr]
                if (isinstance(val, StringType) or isinstance(val, UnicodeType)) and not self.is_ID(val):
                    edge_attr += '"' + val + '"'
                else:
                    edge_attr += str(val)

        if edge_attr:
            edge += ' [' + edge_attr + ']'
        edge += ';'
        return edge
        return


class Graph(Common):
    """Class representing a graph in Graphviz's dot language.

        This class implements the methods to work on a representation
        of a graph in Graphviz's dot language.
        
        graph(graph_name='G', type='digraph', strict=False, suppress_disconnected=False, attribute=value, ...)
        
        graph_name:
                the graph's name
        type:
                can be 'graph' or 'digraph'
        suppress_disconnected:
                defaults to False, which will remove from the
                graph any disconnected nodes.
        simplify:
                if True it will avoid displaying equal edges, i.e.
                only one edge between two nodes. removing the
                duplicated ones.
                
        All the attributes defined in the Graphviz dot language should
        be supported.
        
        Attributes can be set through the dynamically generated methods:
        
         set_[attribute name], i.e. set_size, set_fontname
         
        or using the instance's attributes:
        
         Graph.[attribute name], i.e. graph_instance.label, graph_instance.fontname
        """
    __module__ = __name__
    attributes = [
     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 
     17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 
     31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 
     45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]

    def __init__(self, graph_name='G', type='digraph', strict=False, suppress_disconnected=False, simplify=False, **attrs):
        if type not in ['graph', 'digraph']:
            raise Error, 'Invalid type. Accepted graph types are: graph, digraph, subgraph'
        self.type = type
        self.graph_name = graph_name
        self.strict = strict
        self.suppress_disconnected = suppress_disconnected
        self.simplify = simplify
        self.node_list = []
        self.edge_list = []
        self.edge_src_list = []
        self.edge_dst_list = []
        self.subgraph_list = []
        self.parent_graph = self
        for attr in self.attributes:
            setattr(self, attr, None)
            setattr(self, 'set_' + attr, (lambda x, a=attr: setattr(self, a, x)))
            setattr(self, 'get_' + attr, (lambda a=attr: getattr(self, a)))

        for (attr, val) in attrs.items():
            setattr(self, attr, val)

        return

    def set_simplify(self, simplify):
        """Set whether to simplify or not.
                
                If True it will avoid displaying equal edges, i.e.
                only one edge between two nodes. removing the
                duplicated ones.
                """
        self.simplify = simplify
        return

    def get_simplify(self):
        """Get whether to simplify or not.
                
                Refer to set_simplify for more information.
                """
        return self.simplify
        return

    def set_type(self, graph_type):
        """Set the graph's type, 'graph' or 'digraph'."""
        self.type = graph_type
        return

    def get_type(self):
        """Get the graph's type, 'graph' or 'digraph'."""
        return self.type
        return

    def set_name(self, graph_name):
        """Set the graph's name."""
        self.graph_name = graph_name
        return

    def get_name(self):
        """Get the graph's name."""
        return self.graph_name
        return

    def set_strict(self, val):
        """Set graph to 'strict' mode.
                
                This option is only valid for top level graphs.
                """
        self.strict = val
        return

    def get_strict(self, val):
        """Get graph's 'strict' mode (True, False).
                
                This option is only valid for top level graphs.
                """
        return self.strict
        return

    def set_suppress_disconnected(val):
        """Suppress disconnected nodes in the output graph.
                
                This option will skip nodes in the graph with no  incoming or outgoing
                edges. This option works also for subgraphs and has effect only in the
                current graph/subgraph.
                """
        self.suppress_disconnected = val
        return

    def get_suppress_disconnected(val):
        """Get if suppress disconnected is set.
                
                Refer to set_suppress_disconnected for more information.
                """
        self.suppress_disconnected = val
        return

    def set(self, name, value):
        """Set an attribute value by name.
                
                Given an attribute 'name' it will set its value to 'value'.
                There's always the possibility of using the methods:
                
                        set_'name'(value)
                        
                which are defined for all the existing attributes.
                """
        if name in self.attributes:
            self.__dict__[name] = value
            return True
        return False
        return

    def get(self, name):
        """Get an attribute value by name.
                
                Given an attribute 'name' it will get its value.
                There's always the possibility of using the methods:
                
                        get_'name'()
                        
                which are defined for all the existing attributes.
                """
        return self.__dict__[name]
        return

    def add_node(self, graph_node):
        """Adds a node object to the graph.

                It takes a node object as its only argument and returns
                None.
                """
        if not isinstance(graph_node, Node):
            raise Error, 'add_node received a non node class object'
        self.node_list.append(graph_node)
        graph_node.parent_graph = self.parent_graph
        return

    def get_node(self, name):
        """Retrieved a node from the graph.
                
                Given a node's name the corresponding Node
                instance will be returned.
                
                If multiple nodes exist with that name, a list of
                Node instances is returned.
                If only one node exists, the instance is returned.
                None is returned otherwise.
                """
        match = [_[1] for node in self.node_list if node.name == name]
        l = len(match)
        if l == 1:
            return match[0]
        elif l > 1:
            return match
        else:
            return None
        return

    def get_node_list(self):
        """Get the list of Node instances.
                
                This method returns the list of Node instances
                composing the graph.
                """
        return self.node_list
        return

    def add_edge(self, graph_edge):
        """Adds an edge object to the graph.
                
                It takes a edge object as its only argument and returns
                None.
                """
        if not isinstance(graph_edge, Edge):
            raise Error, 'add_edge received a non edge class object'
        self.edge_list.append(graph_edge)
        graph_edge.parent_graph = self.parent_graph
        if graph_edge.src not in self.edge_src_list:
            self.edge_src_list.append(graph_edge.src)
        if graph_edge.dst not in self.edge_dst_list:
            self.edge_dst_list.append(graph_edge.dst)
        return

    def get_edge(self, src, dst):
        """Retrieved an edge from the graph.
                
                Given an edge's source and destination the corresponding
                Edge instance will be returned.
                
                If multiple edges exist with that source and destination,
                a list of Edge instances is returned.
                If only one edge exists, the instance is returned.
                None is returned otherwise.
                """
        match = [_[1] for edge in self.edge_list if edge.src == src and edge.dst == dst]
        l = len(match)
        if l == 1:
            return match[0]
        elif l > 1:
            return match
        else:
            return None
        return

    def get_edge_list(self):
        """Get the list of Edge instances.
                
                This method returns the list of Edge instances
                composing the graph.
                """
        return self.edge_list
        return

    def add_subgraph(self, sgraph):
        """Adds an edge object to the graph.
                
                It takes a subgraph object as its only argument and returns
                None.
                """
        if not isinstance(sgraph, Subgraph) and not isinstance(sgraph, Cluster):
            raise Error, 'add_subgraph received a non subgraph class object'
        self.subgraph_list.append(sgraph)
        sgraph.set_graph_parent(self.parent_graph)
        return None
        return

    def get_subgraph(self, name):
        """Retrieved a subgraph from the graph.
                
                Given a subgraph's name the corresponding
                Subgraph instance will be returned.
                
                If multiple subgraphs exist with the same name, a list of
                Subgraph instances is returned.
                If only one Subgraph exists, the instance is returned.
                None is returned otherwise.
                """
        match = [_[1] for sgraph in self.subgraph_list if sgraph.graph_name == name]
        l = len(match)
        if l == 1:
            return match[0]
        elif l > 1:
            return match
        else:
            return None
        return

    def get_subgraph_list(self):
        """Get the list of Subgraph instances.
                
                This method returns the list of Subgraph instances
                in the graph.
                """
        return self.subgraph_list
        return

    def set_graph_parent(self, parent):
        """Sets a graph and its elements to point the the parent.
                
                Any subgraph added to a parent graph receives a reference
                to the parent to access some common data.
                """
        self.parent_graph = parent
        for elm in self.edge_list:
            elm.parent_graph = parent

        for elm in self.node_list:
            elm.parent_graph = parent

        for elm in self.subgraph_list:
            elm.parent_graph = parent
            elm.set_graph_parent(parent)

        return

    def to_string(self, indent=''):
        """Returns a string representation of the graph in dot language.
                
                It will return the graph and all its subelements in string from.
                """
        graph = indent + ''
        if self.__dict__.has_key('strict'):
            if self == self.parent_graph and self.strict:
                graph += 'strict '
        graph += self.type + ' ' + self.graph_name + ' {\n'
        for attr in self.attributes:
            if self.__dict__.has_key(attr) and getattr(self, attr) is not None:
                graph += indent + '\t' + attr + '='
                val = self.__dict__[attr]
                if isinstance(val, StringType) and not self.is_ID(val):
                    graph += '"' + val + '"'
                else:
                    graph += str(val)
                graph += ';\n'

        for elm in self.node_list:
            if elm.name == 'node' or elm.name == 'edge':
                graph += indent + '\t' + elm.to_string() + '\n'

        for elm in self.subgraph_list:
            graph += elm.to_string(indent + '\t') + '\n'

        for elm in self.node_list:
            if elm.name == 'node' or elm.name == 'edge':
                continue
            if self.suppress_disconnected:
                if elm.name not in self.edge_src_list + self.edge_dst_list:
                    continue
            graph += indent + '\t' + elm.to_string() + '\n'

        edges_done = []
        for elm in self.edge_list:
            if self.simplify and elm in edges_done:
                continue
            graph += indent + '\t' + elm.to_string() + '\n'
            edges_done.append(elm)

        graph += indent + '}\n'
        return graph
        return


class Subgraph(Graph):
    """Class representing a subgraph in Graphviz's dot language.

        This class implements the methods to work on a representation
        of a subgraph in Graphviz's dot language.
        
        subgraph(graph_name='subG', suppress_disconnected=False, attribute=value, ...)
        
        graph_name:
                the subgraph's name
        suppress_disconnected:
                defaults to false, which will remove from the
                subgraph any disconnected nodes.
        All the attributes defined in the Graphviz dot language should
        be supported.
        
        Attributes can be set through the dynamically generated methods:
        
         set_[attribute name], i.e. set_size, set_fontname
         
        or using the instance's attributes:
        
         Subgraph.[attribute name], i.e.
                subgraph_instance.label, subgraph_instance.fontname
        """
    __module__ = __name__
    attributes = Graph.attributes + ['rank']

    def __init__(self, graph_name='subG', suppress_disconnected=False, simplify=False, **attrs):
        self.type = 'subgraph'
        self.graph_name = graph_name
        self.suppress_disconnected = suppress_disconnected
        self.node_list = []
        self.edge_list = []
        self.edge_src_list = []
        self.edge_dst_list = []
        self.subgraph_list = []
        for attr in self.attributes:
            setattr(self, attr, None)
            setattr(self, 'set_' + attr, (lambda x, a=attr: setattr(self, a, x)))
            setattr(self, 'get_' + attr, (lambda a=attr: getattr(self, a)))

        for (attr, val) in attrs.items():
            setattr(self, attr, val)

        return


class Cluster(Graph):
    """Class representing a cluster in Graphviz's dot language.

        This class implements the methods to work on a representation
        of a cluster in Graphviz's dot language.
        
        cluster(graph_name='subG', suppress_disconnected=False, attribute=value, ...)
        
        graph_name:
                the cluster's name (the string 'cluster' will be always prepended)
        suppress_disconnected:
                defaults to false, which will remove from the
                cluster any disconnected nodes.
        All the attributes defined in the Graphviz dot language should
        be supported.
        
        Attributes can be set through the dynamically generated methods:
        
         set_[attribute name], i.e. set_color, set_fontname
         
        or using the instance's attributes:
        
         Cluster.[attribute name], i.e.
                cluster_instance.color, cluster_instance.fontname
        """
    __module__ = __name__
    attributes = [
     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    def __init__(self, graph_name='subG', suppress_disconnected=False, **attrs):
        self.type = 'subgraph'
        self.graph_name = 'cluster_' + graph_name
        self.suppress_disconnected = suppress_disconnected
        self.node_list = []
        self.edge_list = []
        self.edge_src_list = []
        self.edge_dst_list = []
        self.subgraph_list = []
        for attr in self.attributes:
            setattr(self, attr, None)
            setattr(self, 'set_' + attr, (lambda x, a=attr: setattr(self, a, x)))
            setattr(self, 'get_' + attr, (lambda a=attr: getattr(self, a)))

        for (attr, val) in attrs.items():
            setattr(self, attr, val)

        return


class Dot(Graph):
    """A container for handling a dot language file.

        This class implements methods to write and process
        a dot language file. It is a derived class of
        the base class 'Graph'.
        """
    __module__ = __name__
    progs = None
    formats = [
     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 
     17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]

    def __init__(self, **args):
        Graph.__init__(self, **args)
        for frmt in self.formats:
            setattr(self, 'create_' + frmt, (lambda prog='dot', f=frmt: self.create(prog, f)))
            f = self.__dict__['create_' + frmt]
            f.__doc__ = "Refer to docstring from 'create' for more information."

        for frmt in self.formats + ['raw']:
            setattr(self, 'write_' + frmt, (lambda path, prog='dot', f=frmt: self.write(path, prog, f)))
            f = self.__dict__['write_' + frmt]
            f.__doc__ = "Refer to docstring from 'write' for more information."

        return

    def write(self, path, prog='dot', format='raw'):
        """Writes a graph to a file.

                Given a filename 'path' it will open/create and truncate
                such file and write on it a representation of the graph
                defined by the dot object and in the format specified by
                'format'.
                The format 'raw' is used to dump the string representation
                of the Dot object, without further processing.
                The output can be processed by any of graphviz tools, defined
                in 'prog', which defaults to 'dot'
                Returns True or False according to the success of the write
                operation.
                
                There's also the preferred possibility of using:
                
                        write_'format'(path, prog='program')
                        
                which are automatically defined for all the supported formats.
                [write_ps(), write_gif(), write_dia(), ...]
                """
        dot_fd = open(path, 'w+b')
        if format == 'raw':
            dot_fd.write(self.to_string())
        else:
            dot_fd.write(self.create(prog, format))
        dot_fd.close()
        return True
        return

    def create(self, prog='dot', format='ps'):
        """Creates and returns a Postscript representation of the graph.

                create will write the graph to a temporary dot file and process
                it with the program given by 'prog' (which defaults to 'twopi'),
                reading the Postscript output and returning it as a string is the
                operation is successful.
                On failure None is returned.
                
                There's also the preferred possibility of using:
                
                        create_'format'(prog='program')
                        
                which are automatically defined for all the supported formats.
                [create_ps(), create_gif(), create_dia(), ...]
                """
        if self.progs is None:
            self.progs = find_graphviz()
            if self.progs is None:
                return None
        if not self.progs.has_key(prog):
            return None
        tmp_name = tempfile.mktemp()
        self.write(tmp_name)
        (stdin, stdout, stderr) = os.popen3('"' + self.progs[prog] + '" -T' + format + ' ' + tmp_name, 'b')
        stdin.close()
        data = stdout.read()
        stdout.close()
        os.unlink(tmp_name)
        return data
        return
