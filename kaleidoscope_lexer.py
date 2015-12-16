import re


class Token:
    def __init__(self):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


class DefToken(Token):
    pass


class ExternToken(Token):
    pass


class EOFToken(Token):
    pass


class NumberToken(Token):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return self.__class__.__name__ + " value=" + str(self.value)


class IdentifierToken(Token):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.__class__.__name__ + " name=" + self.name


class CharacterToken(Token):
    def __init__(self, char):
        super().__init__()
        self.char = char

    def __eq__(self, other):
        return isinstance(other, CharacterToken) and self.char == other.char

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return self.__class__.__name__ + " char=" + self.char


class OpenParenthesisToken(CharacterToken):
    def __init__(self):
        super().__init__(char = '(')


class ClosedParenthesisToken(CharacterToken):
    def __init__(self):
        super().__init__(char = ')')


class Lexer:
    def __init__(self):
        self.regex_comment = re.compile('#.*')
        self.regex_number = re.compile('(\d+(\.\d*)?|\.\d+)([eE]\d+)?')
        self.regex_identifier = re.compile('[a-zA-Z][a-zA-Z0-9]*')

    def tokenize(self, text):
        while text:
            if text[0].isspace():
                text = text[1:]
                continue

            match_comment = self.regex_comment.match(text)
            match_number = self.regex_number.match(text)
            match_identifier = self.regex_identifier.match(text)

            if match_comment:
                comment = match_comment.group(0)
                text = text[len(comment):]
            elif match_number:
                number = match_number.group(0)
                yield NumberToken(float(number))
                text = text[len(number):]
            elif match_identifier:
                identifier = match_identifier.group(0)
                if identifier == 'def':
                    yield DefToken()
                elif identifier == 'extern':
                    yield ExternToken()
                else:
                    yield IdentifierToken(identifier)
                text = text[len(identifier):]
            else:
                yield CharacterToken(text[0])
                text = text[1:]

        yield EOFToken()
