import unittest

from kaleidoscope_evaluator import Evaluator


class TestEvaluator(unittest.TestCase):
    def test_basic(self):
        e = Evaluator()
        self.assertEqual(e.evaluate('3'), 3.0)
        self.assertEqual(e.evaluate('3+3*4'), 15.0)
