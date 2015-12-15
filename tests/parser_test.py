import unittest

from AST import FunctionNode, BinaryOperatorExpression, NumberExpression, PrototypeNode
from kaleidoscope_parser import Parser


class TestParser(unittest.TestCase):
    def test_basic(self):
        self.parser = Parser()
        number = 19
        ast = self.parser.parse(str(number))
        self.assertIsInstance(ast, FunctionNode)
        self.assertIsInstance(ast.body, NumberExpression)
        self.assertEqual(ast.body.value, number)
        print(self.parser._flatten(ast))

    def test_xyz(self):
        self.parser = Parser()
        ast = self.parser.parse("x+y*z")
        self.assertIsInstance(ast, FunctionNode)
        self.assertIsInstance(ast.body, BinaryOperatorExpression)
        self.assertEqual(self.parser._flatten(ast),
                         ['Function', ['Prototype', '', ''],
                          ['Binop', '+', ['Variable', 'x'],
                           ['Binop', '*', ['Variable', 'y'], ['Variable', 'z']]]])
        print(self.parser._flatten(ast))

    def test_def_args(self):
        self.parser = Parser()
        ast = self.parser.parse("def foo(x y) x + foo(y, 4.0)")
        self.assertIsInstance(ast, FunctionNode)
        self.assertEqual(ast.prototype.name, 'foo')
        self.assertEqual(ast.prototype.arguments, ['x', 'y'])
        # self.assertIsInstance(function.body, BinaryOperatorExpression)
        print(self.parser._flatten(ast))

    def test_extern(self):
        self.parser = Parser()
        ast = self.parser.parse("extern sin(arg)")
        self.assertIsInstance(ast, PrototypeNode)
        self.assertEqual(len(ast.arguments), 1)
        print(self.parser._flatten(ast))
