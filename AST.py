class Node:
    pass


class ExpressionNode(Node):
    pass


class NumberExpression(ExpressionNode):
    def __init__(self, value):
        self.value = value


class VariableExpression(ExpressionNode):
    def __init__(self, name):
        self.name = name


class BinaryOperatorExpression(ExpressionNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right


class FunctionCallExpression(ExpressionNode):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments


class IfExpression(ExpressionNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class PrototypeNode(Node):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FunctionNode(Node):
    def __init__(self, prototype, body):
        self.prototype = prototype
        self.body = body

    _anonymous_counter = 0

    @classmethod
    def create_anonymous(cls, expression):
        cls._anonymous_counter += 1
        return cls(
                PrototypeNode('anonymous_{0}'.format(cls._anonymous_counter), []),
                expression
        )

    def is_anonymous(self):
        return "anonymous" in self.prototype.name
