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

    def test_from_string_gen(self):
        print()
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
            self.assertEqual(len(ln.stops), 1)

    def test_from_string_real(self):
        print()
        string_tests = {

            # These tests contain what should be valid data records

            'Old DM - Output format':
            ''' NAME=10 LONGNAME='Altrincham - Warburton - Warrington' CIRCULAR=F,
       HEADWAY=40 MODE=1 ONEWAY=1 OPERATOR=1 SEATCAP=27 CRUSHCAP=55 LOADDISTFAC=100,
       CROWDCURVE=5 USERA1=5_E_I_1_A_1_60 N=1791 ON=30 VOL=30 TF=1.71 N=1792 ON=40 VOL=70,
       N=-7184 VOL=70 N=-1804 VOL=70 N=-1812 VOL=70 N=8088 ON=0 OFF=0,
       VOL=70 N=-1805 VOL=70 N=-7160 VOL=70 N=1807 ON=1 VOL=71 N=1809 ON=1 OFF=20,
       VOL=51 N=-6719 VOL=51 N=-7158 VOL=51 N=-4066 VOL=51 N=-8094 VOL=51 N=2420,
       OFF=8 VOL=43 N=1808 ON=0 OFF=37 VOL=6 N=1810 OFF=0 VOL=6 N=-14101 VOL=6,
       N=1800 VOL=6 N=7181 VOL=6 N=7170 VOL=6 N=-7180 VOL=6 N=-7179 VOL=6 N=-7176,
       VOL=6 N=7175 OFF=6 VOL=0 N=7177 VOL=0 N=2418 VOL=0 N=1801 VOL=0 N=-1798,
       VOL=0 N=12984 VOL=0 N=10264 VOL=0 N=10263 VOL=0 N=-10043 VOL=0 N=10262,
       VOL=0 N=10271 VOL=0 TF=4.16 N=10293 VOL=0 TF=5.65 N=10288 VOL=0 N=10290,
       OFF=0 ''',

            'Old DS - std format, short lines':
            ''' NAME="10", LONGNAME="Altrincham - Warburton - Warrington",
     USERA1="5_E_I_1_A_1_60", MODE=1, OPERATOR=1, ONEWAY=T,
     CIRCULAR=F, HEADWAY[1]=40, SEATCAP=27, CRUSHCAP=55,
     LOADDISTFAC=100, CROWDCURVE[1]=5, N=1791, TF=1.71, N=1792,
     -7184, -1804, -1812, 8088, -1805, -7160, 1807, 1809,
     -6719, -7158, -4066, -8094, 2420, 1808, 1810, -14101, 1800,
     7181, 7170, -7180, -7179, -7176, 7175, 7177, 2418, 1801, -1798,
     12984, 10264, 10263, -10043, 10262, 10271, TF=4.16, N=10293,
     TF=5.65, N=10288, 10290''',

            'New Base - std format, long lines':
            ''' NAME=12, LONGNAME="Altrincham - Warburton - Warrington", USERA1="5_E_I_1_A_1_60", MODE=1, OPERATOR=5, ONEWAY=T, CIRCULAR=F, HEADWAY=50.0, SEATCAP=74, CRUSHCAP=88, LOADDISTFAC=70, CROWDCURVE=3, N=1791, TF=2.39, N=1792,-7184,-1804,-1812,8088,-1805,-7160,1807,1809,-6719,-7158,-4066,-8094,2420,1808,1810, -14101,1800,7181,7170,-7180,-7179,-7176,7175,7177,2418,1801,-1798,12984,10264,10263, -10043,10262,10271,
TF=4.17, N=10293,
TF=8.46, N=10288,10290 ''',

            'New DS - std format, short lines':
            ''' NAME="10", MODE=1, OPERATOR=1, ONEWAY=T, HEADWAY=40,
     LONGNAME="Altrincham - Warburton - Warrington", SEATCAP=27,
     CRUSHCAP=55, LOADDISTFAC=100, CROWDCURVE=5, CIRCULAR=F,
     USERA1="5_E_I_1_A_1_60", NODES=1791, TF=1.71, NODES=1792,
     -7184, -1804, -1812, 8088, -1805, -7160, 1807, 1809, -6719,
     -7158, -4066, -8094, 2420, 1808, 1810, -14101, 1800, 7181,
     7170, -7180, -7179, -7176, 7175, 7177, 2418, 1801, -1798,
     12984, 10264, 10263, -10043, 10262, 10271, 10293, 10288, 10290''',
          }

        for test, string in string_tests.items():
            print(test)
            ln = lin_parser.line.from_string(string)

            self.assertEqual(len(ln.attrs), 12)
            self.assertEqual(len(ln.nodes), 38)
            self.assertEqual(len(ln.stops), 23)


class TestSystem(unittest.TestCase):
    """Test system class."""
    print()


if __name__ == '__main__':
    # src: https://medium.com/@vladbezden/using-python-unittest-in-ipython-or-jupyter-732448724e31
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
