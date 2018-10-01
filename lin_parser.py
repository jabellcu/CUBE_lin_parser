# coding: utf-8

import re

class node:
    """
    Simple node class.
    """
    
    def __init__(self, string, **kwargs):
        string = str(string)
        self.ID = abs(int(string))
        self.__dict__.update(**kwargs)
        
        if string.startswith('-'):
            self.stopping = False
        else:
            self.stopping = True
    
    @property
    def attrs(self):
        '''Returns a dictionary with user-defined attributes.'''
        return {k:v for k,v in self.__dict__.items()
                if '_' not in k and 'ID' != k and 'stopping' != k }
    
    def __str__(self):
        return '{}{}, {}'.format('-' if not self.stopping else '', self.ID,
                self.attrs)


class line:
    """
    Simple line class. A line is a sequence of nodes, but each line can have
    it's own properties.
    """
    
    def __init__(self, nodes, **kwargs):
        self.nodes = nodes  # a list of node objects
        self.__dict__.update(**kwargs)

    @property
    def attrs(self):
        '''Returns a dictionary with user-defined attributes.'''
        return {k:v for k,v in self.__dict__.items()
                if '_' not in k and 'nodes' != k}

    @property
    def stops(self):
        '''Returns a list of the nodes that are actual stops'''
        return [node for node in self.nodes if node.stopping]

    def __str__(self):
        msg = 'Line with {} nodes (of which {} are stops).'.format(
                len(self.nodes), len(self.stops))
        msg += f'\n{self.attrs}'
        return msg
    
    @staticmethod
    def from_string(string):
        parts = [x.strip() for x in string.split(',')]  # clean
        
        nodes = []
        line_attrs = {}
        node_attrs = {}
        
        n = None
        attrs_section = True
        
        while parts:
            p = parts.pop(0)
            
            if bool(re.search('N(?:ODES)?\s*=', p)):
                attrs_section = False
            
            if attrs_section:
                k, _, v = p.partition('=')
                try:
                    line_attrs.update({k.strip(): eval(v.strip())})
                except:
                    line_attrs.update({k.strip(): v.strip()})
                
            else:
                p = re.sub('^N(?:ODES)?\s*=\s*', '', p)
                
                if '=' in p:
                    k, _, v = p.partition('=')
                    try:
                        node_attrs.update({k.strip(): eval(v.strip())})
                    except:
                        node_attrs.update({k.strip(): v.strip()})
                
                else:
                    if n:
                        # Add a node with the number and attrs read so far
                        nodes.append(node(n, **node_attrs))
                        node_attrs = {}
                    
                    n = p  # Set the new node for future attrs to be read
        
        l = line(nodes, **line_attrs)
        
        return l


class system:
    """
    Simple system class. A system is a number of lines.
    """
    
    def __init__(self, lines):
        self.lines = lines
    
    def __str__(self):
        msg = f'System with {len(self.lines.keys())} lines.'
        if hasattr(self, 'comments'):
            msg += f'\n{self.comments}'
        return msg

    @staticmethod
    def _extract_lines(string, line_pat=r'(?s)LINE (.*?)(?=LINE|;|\Z)'):
        line_re = re.compile(line_pat)
        
        records = line_re.findall(string)
        lines = set([line.from_string(r) for r in records])
        # Assumes all lines have a NAME, and that this is unique.
        lines = {l.NAME: l for l in lines}
        
        return lines
    
    @staticmethod
    def _extract_comments(string, comment_pat=r'(?s);.*?(?=LINE|\Z)'):
        comment_re = re.compile(comment_pat)
        
        comments = comment_re.findall(string)
        
        return comments
    
    @staticmethod
    def from_string(string):

        lines = system._extract_lines(string)
        comments = system._extract_comments(string)
        
        s = system(lines)
        if comments:
            s.comments = comments
        
        return s
    
    @staticmethod
    def read_file(path):
        with open(path, 'r') as ifile:
            content = ifile.read()
        
        s = system.from_string(content)
        
        return s

