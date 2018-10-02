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

    # This class variable allows to update all lines easily if needed
    unquoted = ['T', 'F']

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

        formatted_attrs = []
        for k, v in self.attrs.items():
            if isinstance(v, str) and v not in self.unquoted:
                f = f'"{v}"'
            else:
                f = v
            formatted_attrs.append(f'{k}={f}')

        txt_attrs = ', '.join(formatted_attrs)
        txt_nodes = ', '.join(str(n) for n in self.nodes)

        txt = 'LINE {}'.format(', '.join([txt_attrs, txt_nodes]))
        txt = txt.replace(', TF=', ',\n\tTF=')  # prettify

        return txt

    @staticmethod
    def from_string(string):

        # Clean first:
        string = string.replace('\n', '')
        string = re.sub(r'\ALINE\s+', '', string)

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

            # Clean:
            k, _, v = [part.strip() for part in p.partition('=')]
            try:
                # For numbers
                v = ast.literal_eval(v)
            except (ValueError, SyntaxError) as e:
                # For strings, make sure they are enclosed in double quotes:
                v = f'"{v}"'
                v = ast.literal_eval(v)

            if bool(re.search('N(?:ODES)?\s*=', p)):
                attrs_section = False

            if attrs_section:
                if k and v:
                    line_attrs.update({k: v})

            else:
                p = re.sub('^\s*N(?:ODES)?\s*=\s*', '', p)

                if '=' in p:
                    if k and v:
                        node_attrs.update({k: v})
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

    def __init__(self, content):
        self.content = content

    @property
    def comments(self):
        return [x for x in self.content if isinstance(x, str)]

    @property
    def lines(self):
        return {x.NAME: x for x in self.content if isinstance(x, line)}

    def __repr__(self):
        '''Object's summary.'''
        txt = f'System with {len(self.lines.keys())} lines, '
        txt += f'and {len(self.comments)} comments.'
        txt += f'\nLines:'
        txt += ', '.join(self.lines.keys())
        txt += f'\nComments:'
        txt += '\n'.join(self.comments)
        return txt

    def __str__(self):
        '''Representation as the file itself.'''
        return '\n'.join([str(x) for x in self.content])

    def save(self, path):
        with open(path, 'w') as ofile:
            ofile.write(str(self))

    @staticmethod
    def _extract_blocks(
            string, block_pat=r'(?s)(?:(;.*?)\n|LINE\s*(.*?)(?=LINE|;|\Z))'):
        '''Returns a list of tuples [(comment, line), (), ...] for each
        record. Returns an empty string for comments or lines not found in
        each record.'''
        block_re = re.compile(block_pat)
        blocks = block_re.findall(string)
        return blocks

    @staticmethod
    def from_string(string):

        blocks = system._extract_blocks(string)

        content = []
        for comment_txt, line_txt in blocks:
            if comment_txt:
                content.append(comment_txt)

            if line_txt:
                ln = line.from_string(line_txt)
                content.append(ln)

        s = system(content)

        return s

    @staticmethod
    def read_file(path):
        with open(path, 'r') as ifile:
            content = ifile.read()

        s = system.from_string(content)

        return s
