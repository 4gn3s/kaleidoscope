import unittest
import pprint

from kaleidoscope_lexer import Lexer
from tests.settings import TESTFILE


class TestLexer(unittest.TestCase):
    def test(self):
        with open(TESTFILE, 'r') as f:
            self.buffer = f.read()
        print(self.buffer)
        self.lexer = Lexer()
        tokens = list(self.lexer.tokenize(self.buffer))
        pprint.pprint(tokens)
        self.assertEqual(len(tokens), 34)
