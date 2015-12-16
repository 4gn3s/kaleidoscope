import unittest

from kaleidoscope_evaluator import Evaluator


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def test_basic(self):
        self.assertEqual(self.evaluator.evaluate("3"), 3.0)
        self.assertEqual(self.evaluator.evaluate("3+3*4"), 15.0)
        self.assertEqual(self.evaluator.evaluate("3*4-2+5/5"), 11.0)

    def test_def(self):
        self.assertIsNone(self.evaluator.evaluate("def adder(x y) x+y"))
        self.assertEqual(self.evaluator.evaluate("adder(5, 4)"), 9.0)
        self.assertEqual(self.evaluator.evaluate("adder(5, 4) + adder(3, 2)"), 14.0)

    def test_extern(self):
        self.assertIsNone(self.evaluator.evaluate('extern ceil(x)'))
        self.assertEqual(self.evaluator.evaluate('ceil(19.5)'), 20.0)

    def test_def_extern(self):
        self.assertIsNone(self.evaluator.evaluate('extern ceil(x)'))
        self.assertIsNone(self.evaluator.evaluate('extern floor(x)'))
        self.assertIsNone(self.evaluator.evaluate("def eadder(x y) ceil(x) + floor(y)"))
        self.assertEqual(self.evaluator.evaluate("eadder(5.5, 4.2)"), 10.0)

    def test_parenthesis(self):
        self.assertIsNone(self.evaluator.evaluate("def testfun(x) (1+2+x)*(x+(1+2))"))
        self.assertEqual(self.evaluator.evaluate("testfun(5)"), 64.0)
