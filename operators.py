from lexer import CharacterToken


class Operators:

    def get(self, token):
        if isinstance(token, CharacterToken):
            return self._operators().get(token.char, -1)
        return -1

    def _operators(self):
        return {
            '<': 10,
            '+': 20,
            '-': 20,
            '*': 40,
            '/': 40
        }
