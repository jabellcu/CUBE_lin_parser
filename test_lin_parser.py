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
            self.assertEqual(fakeOutput.getvalue().strip(), '7730, {}')
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_num_pass)
            self.assertEqual(fakeOutput.getvalue().strip(), '-7730, {}')
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_str_stop)
            self.assertEqual(fakeOutput.getvalue().strip(), '7730, {}')
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            print(self.node_str_pass)
            self.assertEqual(fakeOutput.getvalue().strip(), '-7730, {}')
            
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
    
    pass

class TestSystem(unittest.TestCase):
    """Test system class."""
    
    pass


if __name__ == '__main__':
    #src: https://medium.com/@vladbezden/using-python-unittest-in-ipython-or-jupyter-732448724e31
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

