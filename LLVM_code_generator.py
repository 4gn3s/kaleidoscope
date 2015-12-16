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

    def generate_llvm(self, node):
        assert isinstance(node, (PrototypeNode, FunctionNode))
        return self.generate(node)

    def generate(self, node):
        method = 'generate' + re.sub('([A-Z]+)', r'_\1', node.__class__.__name__).lower()
        return getattr(self, method)(node)

    def generate_number_expression(self, node):
        return ir.Constant(ir.DoubleType(), node.value)

    def generate_variable_expression(self, node):
        return self.symbol_table[node.name]

    def generate_if_expression(self, node):
        conditional = self.generate(node.condition)
        cmp = self.builder.fcmp_ordered(
            '!=', conditional, ir.Constant(ir.DoubleType(), 0.0))

        # conditional branch to either then_bb or else_bb depending on cmp
        then_bb = self.builder.function.append_basic_block('then')
        else_bb = ir.Block(self.builder.function, 'else')
        merge_bb = ir.Block(self.builder.function, 'ifcont')
        self.builder.cbranch(cmp, then_bb, else_bb)

        self.builder.position_at_start(then_bb)
        then_branch = self.generate(node.then_branch)
        self.builder.branch(merge_bb)

        then_bb = self.builder.block
        self.builder.function.basic_blocks.append(else_bb)

        self.builder.position_at_start(else_bb)
        else_branch = self.generate(node.else_branch)
        self.builder.branch(merge_bb)

        self.builder.function.basic_blocks.append(merge_bb)
        self.builder.position_at_start(merge_bb)
        phi = self.builder.phi(ir.DoubleType(), 'iftmp')
        phi.add_incoming(then_branch, then_bb)
        phi.add_incoming(else_branch, else_bb)
        return phi

    def generate_binary_operator_expression(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)

        if node.operator == '+':
            return self.builder.fadd(left, right, 'addtmp')
        elif node.operator == '-':
            return self.builder.fsub(left, right, 'subtmp')
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
        return_value = self.generate(node.body)
        self.builder.ret(return_value)
        return func
