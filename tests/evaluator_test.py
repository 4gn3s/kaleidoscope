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
        self.evaluator.evaluate("def adder(x y) x+y")
        self.assertEqual(self.evaluator.evaluate("adder(5, 4)"), 9.0)
        self.assertEqual(self.evaluator.evaluate("adder(5, 4) + adder(3, 2)"), 14.0)

    def test_extern(self):
        self.evaluator.evaluate('extern ceil(x)')
        self.assertEqual(self.evaluator.evaluate('ceil(19.5)'), 20.0)

    def test_def_extern(self):
        self.evaluator.evaluate('extern ceil(x)')
        self.evaluator.evaluate('extern floor(x)')
        self.evaluator.evaluate("def eadder(x y) ceil(x) + floor(y)")
        self.assertEqual(self.evaluator.evaluate("eadder(5.5, 4.2)"), 10.0)

    def test_parenthesis(self):
        self.evaluator.evaluate("def testfun(x) (1+2+x)*(x+(1+2))")
        self.assertEqual(self.evaluator.evaluate("testfun(5)"), 64.0)

    def test_multiple_evaluates(self):
        self.evaluator.evaluate("def adder(x y) x+y")
        self.evaluator.evaluate("def testfun(x) (1+2+x)*(x+(1+2))")
        self.assertEqual(self.evaluator.evaluate("testfun(adder(1, 2)*3)"), 144.0)

    def test_if_else(self):
        self.evaluator.evaluate("def foo() 1+3")
        self.evaluator.evaluate("def bar() 25")
        self.evaluator.evaluate("def baz(x) if x then foo() else bar()")
        self.assertEqual(self.evaluator.evaluate("baz(1<2)"), 4.0)
        self.assertEqual(self.evaluator.evaluate("baz(1>2)"), 25.0)

    def test_if_else_params(self):
        self.evaluator.evaluate('def foo(a b) a * if a < b then a + 1 else b + 1')
        self.assertEqual(self.evaluator.evaluate('foo(3, 4)'), 12)
        self.assertEqual(self.evaluator.evaluate('foo(5, 4)'), 25)

    def test_nested_if(self):
        self.evaluator.evaluate('''
            def foo(a b c)
                if a < b
                    then if a < c then a * 2 else c * 2
                    else b * 2''')
        self.assertEqual(self.evaluator.evaluate('foo(1, 20, 300)'), 2)
        self.assertEqual(self.evaluator.evaluate('foo(10, 2, 300)'), 4)
        self.assertEqual(self.evaluator.evaluate('foo(100, 2000, 30)'), 60)

    def test_for(self):
        self.evaluator.evaluate('''
            def foo(a b c)
                if a < b
                    then for x = 1.0, x < b, c in x+a+c*b
                    else c * 2''')
        self.assertEqual(self.evaluator.evaluate('foo(1, 2, 3)'), 0)
        self.assertEqual(self.evaluator.evaluate('foo(3, 2, 30)'), 60)

    def test_putchard(self):
        self.evaluator.evaluate('def foo(a b) for x = 65, x < a, b in putchard(x)')
