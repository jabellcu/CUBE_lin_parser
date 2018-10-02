# coding: utf-8

import re
import ast


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
        return {k: v for k, v in self.__dict__.items()
                if '_' not in k and 'ID' != k and 'stopping' != k}

    def __repr__(self):
        '''Object's summary.'''
        return '{}{}, {}'.format('-' if not self.stopping else '', self.ID,
                                 self.attrs)

    def __str__(self):
        txt_node = '{}{}'.format('-' if not self.stopping else '', self.ID,)
        if self.attrs:
            txt_attrs = ', '.join([f'{k}={v}' for k, v in self.attrs.items()])
            return ', '.join([txt_node, txt_attrs])
        else:
            return txt_node


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
        return {k: v for k, v in self.__dict__.items()
                if '_' not in k and 'nodes' != k}

    @property
    def stops(self):
        '''Returns a list of the nodes that are actual stops'''
        return [node for node in self.nodes if node.stopping]

    def __repr__(self):
        '''Object's summary.'''
        txt = 'Line with {} nodes (of which {} are stops).'.format(
                len(self.nodes), len(self.stops))
        txt += f'\n{self.attrs}'
        return txt

    def __str__(self):
        txt_attrs = ', '.join([f'{k}={v}' for k, v in self.attrs.items()])
        txt_nodes = ', '.join(str(n) for n in self.nodes)
        txt = ', '.join([txt_attrs, txt_nodes])
        txt = txt.replace(', TF=', ',\n\tTF=')  # prettify
        return txt

    @staticmethod
    def from_string(string):

        string = string.replace('\n', '')  # Clean
        # src for this amazing magic:
        # https://stackoverflow.com/a/16710842/2802352
        parts = re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', string)

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
                if k and v:
                    try:
                        line_attrs.update({k.strip(): ast.literal_eval(v)})
                    except ValueError:
                        line_attrs.update({k.strip(): v.strip()})

            else:
                p = re.sub('^\s*N(?:ODES)?\s*=\s*', '', p)

                if '=' in p:
                    k, _, v = p.partition('=')
                    if k and v:
                        try:
                            node_attrs.update({k.strip(): ast.literal_eval(v)})
                        except ValueError:
                            node_attrs.update({k.strip(): v.strip()})
                else:
                    if n:
                        # Add the previous node, with the attrs read so far
                        nodes.append(node(n, **node_attrs))
                        node_attrs = {}

                        if not parts:
                            # Add the last node if there are no more attrs
                            nodes.append(node(p))

                    n = p  # Set the new node for future attrs to be read

        ln = line(nodes, **line_attrs)

        return ln


class system:
    """
    Simple system class. A system is a number of lines.
    """

    def __init__(self, lines):
        self.lines = lines

    def __repr__(self):
        '''Object's summary.'''
        txt = f'System with {len(self.lines.keys())} lines.'
        if hasattr(self, 'comments'):
            txt += f'\n{self.comments}'
        return txt

    def __str__(self):
        '''Representation as the file itself.'''
        if hasattr(self, 'comments'):
            txt = '\n'.join(self.comments)
        else:
            txt = ''
        txt += '\n'.join([str(ln) for ln in self.lines.values()])
        return txt

    def save(self, path):
        with open(path, 'w') as ofile:
            ofile.write(str(self))

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
