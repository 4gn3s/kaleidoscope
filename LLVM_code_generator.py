import re

import llvmlite.ir as ir

from AST import FunctionNode, PrototypeNode


class LLVMError(Exception):
    pass


class LLVMGenerator:
    def __init__(self):
        self.module = ir.Module()
        self.builder = None
        self.symbol_table = {}

    def generate(self, node):
        assert isinstance(node, (PrototypeNode, FunctionNode))
        method = 'generate' + re.sub('([A-Z]+)', r'_\1', node.__class__.__name__).lower()
        return getattr(self, method)(node)

    def generate_number_expression(self, node):
        return ir.Constant(ir.DoubleType(), node.value)

    def generate_variable_expression(self, node):
        return self.symbol_table[node.name]

    def generate_binary_operator_expression(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)

        if node.operator == '+':
            return self.builder.fadd(left, right, 'addtmp')
        elif node.operator == '-':
            return self.builder.fsum(left, right, 'subtmp')
        elif node.operator == '*':
            return self.builder.fmul(left, right, 'multmp')
        elif node.operator == '/':
            return self.builder.fdiv(left, right, 'divtmp')
        elif node.operator == '>':
            cmp = self.builder.fcmp_unordered('>', left, right, 'cmptmp')
            return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')
        elif node.operator == '<':
            cmp = self.builder.fcmp_unordered('<', left, right, 'cmptmp')
            return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')
        else:
            raise LLVMError("Unknown binary operator " + str(node.operator))

    def generate_function_call_expression(self, node):
        function = self.module.globals.get(node.function, None)
        if not function or not isinstance(function, ir.Function):
            raise LLVMError("Call to unknown function " + str(node.function))
        if len(function.args) != len(node.arguments):
            raise LLVMError("Function call with incorrect arguments count " + str(node.function))
        arguments = [self.generate(arg) for arg in node.arguments]
        return self.builder.call(function, arguments, 'calltmp')

    def generate_prototype_node(self, node):
        function = node.name
        func_ty = ir.FunctionType(ir.DoubleType(), [ir.DoubleType()] * len(node.arguments))
        func = None
        if function in self.module.globals:
            existing_func = self.module.globals[function]
            if not isinstance(existing_func, ir.Function):
                raise LLVMError("Function or global name collision " + str(function))
            if not existing_func.is_declaration():
                raise LLVMError("Redefinition of function " + str(function))
            if len(existing_func.args) != len(func_ty.args):
                raise LLVMError("Redefinition of function " +
                                str(function) + " with different arguments count")
            func = self.module.globals[function]
        else:
            func = ir.Function(self.module, func_ty, function)
        for i, arg in enumerate(func.args):
            arg.name = node.arguments[i]
            self.symbol_table[arg.name] = arg
        return func

    def generate_function_node(self, node):
        self.symbol_table = {}
        func = self.generate(node.prototype)
        bb_entry = func.append_basic_block('entry')
        self.builder = ir.IRBuilder(bb_entry)
        retval = self.generate(node.body)
        self.builder.ret(retval)
        return func
