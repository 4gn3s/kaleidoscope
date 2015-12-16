from AST import NumberExpression, VariableExpression, FunctionCallExpression, PrototypeNode, FunctionNode, \
    BinaryOperatorExpression
from kaleidoscope_lexer import CharacterToken, NumberToken, IdentifierToken, EOFToken, DefToken, ExternToken, Lexer, \
    OpenParenthesisToken, ClosedParenthesisToken
from operators import Operators


class ParserException(Exception):
    pass


class Parser:
    def __init__(self):
        self.tokens = None
        self.current = None
        self.operators_precendence = Operators()

    def next(self):
        self.current = next(self.tokens)

    def parse_number_expression(self):
        """
        numberexpr ::= number
        """
        result = NumberExpression(self.current.value)
        self.next()
        return result

    def parse_parenthesis_expression(self):
        """
        parenexpr ::= '(' expression ')'
        """
        self.next()  # consume '('
        contents = self.parse_expression()
        if self.current != ClosedParenthesisToken():
            raise ParserException("Expected ')', got " + str(self.current))
        self.next()  # consume ')'
        return contents

    def parse_expression(self):
        """
        expression ::= primary binoprhs
        """
        left = self.parse_primary_expression()
        return self.parse_binary_op(left, 0)

    def parse_binary_op(self, left, left_precedence):
        """
        binoprhs ::= (operator primary)*
        """
        while True:
            precedence = self.operators_precendence.get(self.current)
            if precedence < left_precedence:
                return left
            operator = self.current.char
            self.next()
            right = self.parse_primary_expression()
            next_precedence = self.operators_precendence.get(self.current)
            if precedence < next_precedence:
                right = self.parse_binary_op(right, precedence + 1)
            left = BinaryOperatorExpression(operator, left, right)

    def parse_identifier_expression(self):
        """
        identifierexpr ::= identifier | identifier '(' expression* ')'
        """
        identifier_name = self.current.name
        self.next()
        if self.current != OpenParenthesisToken():
            return VariableExpression(identifier_name)

        self.next()  # consume '('
        arguments = []
        if self.current != ClosedParenthesisToken():
            while True:
                arguments.append(self.parse_expression())
                if self.current == ClosedParenthesisToken():
                    break
                if self.current != CharacterToken(','):
                    raise ParserException("Expected ',' or ')' in the argument list")
                self.next()
        self.next()  # consume ')'
        return FunctionCallExpression(identifier_name, arguments)

    def parse_primary_expression(self):
        """
        primary ::= identifierexpr | numberexpr | parenexpr
        """
        if isinstance(self.current, IdentifierToken):
            return self.parse_identifier_expression()
        elif isinstance(self.current, NumberToken):
            return self.parse_number_expression()
        elif self.current == OpenParenthesisToken():
            return self.parse_parenthesis_expression()
        else:
            raise ParserException("Unknown token when parsing primary: " + str(self.current))

    def parse_prototype_expression(self):
        """
        prototype ::= id '(' id* ')'
        """
        if not isinstance(self.current, IdentifierToken):
            raise ParserException("Expected function name in prototype")
        function_name = self.current.name
        self.next()
        if self.current != OpenParenthesisToken():
            raise ParserException("Expected '(' in function prototype")
        self.next()
        argument_names = []
        while isinstance(self.current, IdentifierToken):
            argument_names.append(self.current.name)
            self.next()
        if self.current != ClosedParenthesisToken():
            raise ParserException("Expected ')' in function prototype")
        self.next()
        return PrototypeNode(function_name, argument_names)

    def parse_definition(self):
        """
        definition ::= 'def' prototype expression
        """
        self.next()
        prototype = self.parse_prototype_expression()
        expression = self.parse_expression()
        return FunctionNode(prototype, expression)

    def parse_external(self):
        """
        external ::= 'extern' prototype
        """
        self.next()
        return self.parse_prototype_expression()

    def parse_toplevel_expression(self):
        """
        toplevelexpr ::= expression
        """
        expression = self.parse_expression()
        return FunctionNode.create_anonymous(expression)

    def parse(self, string):
        """
        top ::= definition | external | expression | EOF
        """

        lexer = Lexer()
        self.tokens = lexer.tokenize(string)
        self.next()

        if isinstance(self.current, EOFToken):
            pass
        elif isinstance(self.current, DefToken):
            print('Parsed a function definition.')
            return self.parse_definition()
        elif isinstance(self.current, ExternToken):
            print('Parsed an extern.')
            return self.parse_external()
        else:
            print('Parsed a top-level expression.')
            return self.parse_toplevel_expression()

    def _flatten(self, ast):
        if isinstance(ast, NumberExpression):
            return ['Number', ast.value]
        elif isinstance(ast, VariableExpression):
            return ['Variable', ast.name]
        elif isinstance(ast, BinaryOperatorExpression):
            return ['Binop', ast.operator,
                    self._flatten(ast.left), self._flatten(ast.right)]
        elif isinstance(ast, FunctionCallExpression):
            args = [self._flatten(arg) for arg in ast.arguments]
            return ['Call', ast.function, args]
        elif isinstance(ast, PrototypeNode):
            return ['Prototype', ast.name, ' '.join(ast.arguments)]
        elif isinstance(ast, FunctionNode):
            return ['Function',
                    self._flatten(ast.prototype), self._flatten(ast.body)]
        else:
            raise TypeError('unknown type in _flatten: {0}'.format(type(ast)))
