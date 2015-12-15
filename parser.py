from AST import NumberExpression, VariableExpression, FunctionCallExpression, PrototypeNode, FunctionNode, \
    BinaryOperatorExpression
from lexer import CharacterToken, NumberToken, IdentifierToken, EOFToken, DefToken, ExternToken
from operators import Operators


class ParserException(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = None
        self.operators_precendence = Operators()
        self.next()

    def next(self):
        self.current = self.tokens.next()

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
        if self.current != CharacterToken(')'):
            raise ParserException("Expected ')'")
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
        if self.current != CharacterToken(')'):
            return VariableExpression(identifier_name)

        self.next()  # consume '('
        arguments = []
        while self.current != CharacterToken(')'):
            arguments.append(self.parse_expression())
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
        elif isinstance(self.current, CharacterToken('(')):
            return self.parse_parenthesis_expression()
        else:
            raise ParserException("Unknown token when parsing primary")

    def parse_prototype_expression(self):
        """
        prototype ::= id '(' id* ')'
        """
        if not isinstance(self.current, IdentifierToken):
            raise ParserException("Expected function name in prototype")
        function_name = self.current.name
        self.next()
        if self.current != CharacterToken('('):
            raise ParserException("Expected '(' in function prototype")
        self.next()
        argument_names = []
        while isinstance(self.current, IdentifierToken):
            argument_names.append(self.current.name)
            self.next()
        if self.current != CharacterToken(')'):
            raise ParserException("Expected ')' in function prototype")
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
        prototype = PrototypeNode('', [])
        expression = self.parse_expression()
        return FunctionNode(prototype, expression)

    def parse(self):
        """
        top ::= definition | external | expression | EOF
        """
        # while True:
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
