# coding: utf-8

import re
import ast
import pandas as pd


class node:
    """
    Simple node class.
    """

    def __init__(self, string, **kwargs):
        self._string = str(string)
        self.ID = abs(int(self._string.strip()))
        self.__dict__.update(**kwargs)

        if self._string.strip().startswith('-'):
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

    def __str__(self, node_attrs=None, exclude_node_attrs=None):
        '''node_attrs: list of node attributes to include.
           exclude_node_attrs: list of node attributes to omit.'''

        txt_node = '{}{}'.format('-' if not self.stopping else '', self.ID,)

        if self.attrs:
            if node_attrs:
                attrs = {k: v for k, v in self.attrs.items()
                         if k in node_attrs}
            else:
                attrs = self.attrs

            if exclude_node_attrs:
                attrs = {k:v for k, v in attrs.items()
                         if k not in exclude_node_attrs}

            formatted_attrs = [f'{k}={v}' for k, v in attrs.items()]

            txt_attrs = ', '.join(formatted_attrs)

            if txt_attrs:
                txt_node = ', '.join([txt_node, txt_attrs])

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
    NodeLabel = 'N'  # Or 'NODE'

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

    def __str__(self, line_attrs=None, exclude_line_attrs=None,
            node_attrs=None, exclude_node_attrs=None):
        '''node_attrs: list of node attributes to include.
           exclude_node_attrs: list of node attributes to omit.
           line_attrs: list of line attributes to include.
           exclude_line_attrs: list of line attributes to omit.'''

        # String attributes are quoted, with exceptions
        formatted_attrs = []

        if line_attrs:
            l_attrs = {k: v for k, v in self.attrs.items()
                       if k in line_attrs}
        else:
            l_attrs = self.attrs

        if exclude_line_attrs:
            l_attrs = {k: v for k, v in l_attrs.items()
                       if k not in exclude_line_attrs}

        for k, v in l_attrs.items():
            if isinstance(v, str) and v not in self.unquoted:
                f = repr(v)  # This will enclose in the right quotes
            else:
                f = v
            formatted_attrs.append(f'{k}={f}')

        txt_attrs = ', '.join(formatted_attrs)

        # First nodes, and nodes after attributes, are labeled
        formatted_nodes = []
        first_node = True
        for n in self.nodes:
            if first_node:
                formatted_nodes.append('{}={}'.format(
                    self.NodeLabel, n.__str__(
                        node_attrs=node_attrs,
                        exclude_node_attrs=exclude_node_attrs)))
                first_node = False
            else:
                formatted_nodes.append(n.__str__(
                    node_attrs=node_attrs,
                    exclude_node_attrs=exclude_node_attrs))

            if node_attrs:
                n_attrs = {k: v for k, v in n.attrs.items()
                           if k in node_attrs}
            else:
                n_attrs = n.attrs

            if exclude_node_attrs:
                n_attrs = {k: v for k, v in n_attrs.items()
                           if k not in exclude_node_attrs}

            if n_attrs:
                # node has attributes printed, reset the flag:
                first_node = True

        txt_nodes = ', '.join(formatted_nodes)

        txt = 'LINE {}'.format(', '.join([txt_attrs, txt_nodes]))
        txt = txt.replace(', TF=', ',\n\tTF=')  # prettify

        return txt

    @property
    def stop_seq(self, sep='_'):
        '''Returns a concatenation of lines's stops.'''
        return sep.join([str(n.ID) for n in self.stops])

    @staticmethod
    def from_string(string, potential_seps=[' ', '\t', ',']):

        # Guess the separator as the most common of potential separators:
        formatted = re.sub('[=,][\s\n\t]+', ',', string)  # clean
        # Accounts for multiple separators.
        seps_count = [len(re.findall(f'{sep}+', formatted))
                      for sep in potential_seps]
        sep = potential_seps[seps_count.index(max(seps_count))]

        # Clean:
        string = string.replace('\n', '')
        string = string.replace('\x1a', '')  # EOF windows >_<
        string = re.sub(r'\ALINE\s+', '', string)
        string = re.sub('[\s,]*\Z', '', string)
        if sep == ' ':
            string = re.sub(f'{sep}*={sep}*', '=', string)

        # src for this amazing magic:
        # https://stackoverflow.com/a/16710842/2802352
        parts_pat = f'''(?:["](?:\\.|[^"])*["]|['](?:\\.|[^'])*[']|[^{sep}"]|[^{sep}'])+'''
        parts = re.findall(parts_pat, string)

        NodeLabel_pat = r'\A\s*N(?:ODES)?\b'

        nodes = []
        line_attrs = {}
        node_attrs = {}

        n = None
        attrs_section = True

        while parts:
            p = parts.pop(0)

            # Clean:
            p = re.sub('[\s,]*\Z', '', p)
            k, _, v = [part.strip() for part in p.partition('=')]

            try:
                # For numbers
                v = ast.literal_eval(v)
            except (ValueError, SyntaxError) as e:
                v = str(v)

            if bool(re.search(f'{NodeLabel_pat}\s*=\s*', p)):
                attrs_section = False

            if attrs_section:
                if k and v:
                    line_attrs.update({k: v})

            else:
                # Repalce the node label
                p = re.sub(f'{NodeLabel_pat}\s*=\s*', '', p)

                if '=' in p:
                    if bool(re.search(f'{NodeLabel_pat}', k)):
                        msg = f'Node declaration in attribute "{k}: {v}"'
                        msg += f'in node {n}, line:\n{line_attrs}'
                        raise AssertionError(msg)

                    # Still has '=', must be an attribute:
                    if k and v:
                        node_attrs.update({k: v})

                else:
                    # It is a node:
                    if n:
                        # Add the previous node, with the attrs read so far
                        nodes.append(node(n, **node_attrs))
                        node_attrs = {}  # reset

                    n = p  # Set the new node for future attrs to be read

        else:
            if n:
                # Add the last node (if it is not empty)
                nodes.append(node(n, **node_attrs))

        ln = line(nodes, **line_attrs)

        return ln


class system:
    """
    Simple system class. A system is a number of lines.
    """

    def __init__(self, content=None):
        if content:
            self.content = content
        else:
            self.content = []

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
        txt += f'\nLines:\n'
        txt += ', '.join([str(k) for k in self.lines])  # some might be ints
        txt += f'\nComments:\n'
        txt += '\n'.join(self.comments)
        return txt

    def __str__(self, sort=False, comments=True, **kwargs):
        '''Representation as the file itself.

            sort: if False, outputs is sorted with the same structure as
                  input content. If True, comments are first, then all lines
                  in NAME order.

            comments: output comments only if True.

            node_attrs: list of node attributes to include.
            exclude_node_attrs: list of node attributes to omit.
            line_attrs: list of line attributes to include.
            exclude_line_attrs: list of line attributes to omit.'''

        if sort:
            sorted_lines = [self.lines[ln].__str__(**kwargs)
                            for ln in sorted(self.lines)]
            txt_lines = '\n'.join(sorted_lines)

            if comments:
                txt_comments = [c for c in self.comments]
                txt = '\n'.join([txt_comments, txt_lines])

            else:
                txt = txt_lines

        else:
            if comments:
                txt_content = [x.__str__(**kwargs)
                               if not isinstance(x, str) else str(x)
                               for x in self.content]

            else:
                txt_content = [x.__str__(**kwargs)
                               for x in self.content
                               if not isinstance(x, str)]

            txt = '\n'.join(txt_content)

        return txt

    def save(self, path, sort=False, comments=True,
             node_attrs=None, exclude_node_attrs=None, 
             line_attrs=None, exclude_line_attrs=None):
        with open(path, 'w') as ofile:
            ofile.write(self.__str__(sort=sort, comments=comments,
                                     node_attrs=node_attrs,
                                     exclude_node_attrs=exclude_node_attrs,
                                     line_attrs=line_attrs,
                                     exclude_line_attrs=exclude_line_attrs))

    def lines_by_attr(self, attr, val):
        '''Returns a list of lines having a specific value in an attribute.'''
        lines = [ln for ln in self.lines.values()
                 if getattr(ln, attr) == val]
        return lines

    def lines_query(self, qry):
        '''Returns a list of lines meeting a SQL-like query. This relies on
        pandas DataFrame query:
            https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.query.html'''
        
        lns_names = self.df.query(qry)['NAME'].tolist()

        if lns_names:
            lns = [self.lines[n] for n in lns_names]
            return lns
        else:
            return []

    @property
    def df(self):
        '''Returns a dataframe with the attributes for each line.'''

        # Assume lines start on 1:
        data = {i: ln.attrs for i, ln in enumerate(self.lines.values(), 1)}
        df = pd.DataFrame.from_records(data).T

        # stops and nodes are objects!
        additional_attrs = 'stop_seq stops nodes'.split()
        for attr in additional_attrs:
            df[attr] = [getattr(ln, attr) for ln in self.lines.values()]

        return df

    @staticmethod
    def _extract_blocks(
            string,
            block_pat=r'(?s)(?:(;.*?|\n\s*)\n|LINE\s+(.*?)(?=\n\s*LINE|\n\s*;|\Z))'):
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
