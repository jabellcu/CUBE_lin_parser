# coding: utf-8

import lin_parser

from io import StringIO
import unittest
from unittest.mock import patch


class TestNode(unittest.TestCase):
    """Test node class."""

    node_num_stop = lin_parser.node(7730)
    node_num_pass = lin_parser.node(-7730)
    node_str_stop = lin_parser.node('7730')
    node_str_pass = lin_parser.node('-7730')

    test_nodes = [node_num_stop, node_num_pass, node_str_stop, node_str_pass]

    def test_print(self):
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_num_stop)
            self.assertEqual(fakeOutput.getvalue().strip(), '7730')
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_num_pass)
            self.assertEqual(fakeOutput.getvalue().strip(), '-7730')
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_str_stop)
            self.assertEqual(fakeOutput.getvalue().strip(), '7730')
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_str_pass)
            self.assertEqual(fakeOutput.getvalue().strip(), '-7730')

    def test_ID(self):
        for n in self.test_nodes:
            self.assertEqual(n.ID, 7730)

    def test_stopping(self):
        self.assertTrue(self.node_num_stop.stopping)
        self.assertFalse(self.node_num_pass.stopping)
        self.assertTrue(self.node_str_stop.stopping)
        self.assertFalse(self.node_str_pass.stopping)


class TestLine(unittest.TestCase):
    """Test line class."""

    def test_from_string(self):
        string_tests = {

            # These tests contain what should be valid data records

            'spaces_SingleQuote_basic':
            ''' NAME=1 LONGNAME='variable spaces, single quotes' OTHER='nota, eso' HEADWAY=60 MODE=2 ONEWAY=T,
          OPERATOR=89 SEATCAP=252 CRUSHCAP=430 LOADDISTFAC=60 CROWDCURVE=10 N=80801 ON=288,
          VOL=288 N=-80800 VOL=288 N=-80511 VOL=288''',

            'spaces_DoubleQuote_basic':
            ''' NAME=2, LONGNAME='comma, single quotes', OTHER='nota, eso', HEADWAY=60, MODE=2, ONEWAY=T,
          OPERATOR=89, SEATCAP=252, CRUSHCAP=430, LOADDISTFAC=60, CROWDCURVE=10, N=80801, ON=288,
          VOL=288, N=-80800, VOL=288, N=-80511, VOL=288''',

            'spaces_SingleQuote_adv':
            ''' NAME=3 LONGNAME="varia'ble spa''ces, double quotes" OTHER="no\\t\'a, \"eso" HEADWAY=60 MODE=2 ONEWAY=T,
          OPERATOR =  89 SEATCAP =  252 CRUSHCAP=430 LOADDISTFAC=60 CROWDCURVE=10 N=80801 ON=288,
          VOL=288 N=-80800 VOL=288 N=-80511 VOL=288  ''',

            'spaces_DoubleQuote_adv_soft':
            ''' NAME=4, LONGNAME='comm"a, single quotes test', OTHER='nota, eso', HEADWAY=60, MODE=2, ONEWAY=T,
          OPERATOR =  89, SEATCAP =  252, CRUSHCAP=430, LOADDISTFAC=60, CROWDCURVE=10, N=80801, ON=288,
          VOL=288, N=-80800, VOL=288, N=-80511, VOL=288,  ''',
          }

        for test, string in string_tests.items():
            print(test)
            ln = lin_parser.line.from_string(string)

            self.assertEqual(len(ln.attrs), 11)
            self.assertEqual(len(ln.nodes), 3)


class TestSystem(unittest.TestCase):
    """Test system class."""

    pass


if __name__ == '__main__':
    # src: https://medium.com/@vladbezden/using-python-unittest-in-ipython-or-jupyter-732448724e31
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
