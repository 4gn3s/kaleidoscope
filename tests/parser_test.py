import unittest

from AST import FunctionNode, BinaryOperatorExpression, NumberExpression, PrototypeNode
from kaleidoscope_parser import Parser


class TestParser(unittest.TestCase):
    def test_basic(self):
        self.parser = Parser()
        number = 19
        function = self.parser.parse(str(number))
        self.assertIsInstance(function, FunctionNode)
        self.assertIsInstance(function.body, NumberExpression)
        self.assertEqual(function.body.value, number)
        print(self.parser._flatten(function))

    def test_xyz(self):
        self.parser = Parser()
        function = self.parser.parse("x+y*z")
        self.assertIsInstance(function, FunctionNode)
        self.assertIsInstance(function.body, BinaryOperatorExpression)
        self.assertEqual(self.parser._flatten(function),
                         ['Function', ['Prototype', '', ''],
                          ['Binop', '+', ['Variable', 'x'],
                           ['Binop', '*', ['Variable', 'y'], ['Variable', 'z']]]])
        print(self.parser._flatten(function))

    def test_def_args(self):
        self.parser = Parser()
        function = self.parser.parse("def foo(x y) x + foo(y, 4.0)")
        self.assertIsInstance(function, FunctionNode)
        self.assertEqual(function.prototype.name, 'foo')
        self.assertEqual(function.prototype.arguments, ['x', 'y'])
        # self.assertIsInstance(function.body, BinaryOperatorExpression)
        print(self.parser._flatten(function))

    def test_extern(self):
        self.parser = Parser()
        function = self.parser.parse("extern sin(arg)")
        self.assertIsInstance(function, PrototypeNode)
        self.assertEqual(len(function.arguments), 1)
        print(self.parser._flatten(function))
