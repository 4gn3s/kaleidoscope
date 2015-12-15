import unittest
import pprint

from lexer import Lexer
from parser import Parser
from tests.settings import TESTFILE


class TestParser(unittest.TestCase):
    def test(self):
        with open(TESTFILE, 'r') as f:
            self.buffer = f.read()
        print(self.buffer)
        self.lexer = Lexer()
        self.parser = Parser(self.lexer.tokenize(self.buffer))
        self.parser.parse()
