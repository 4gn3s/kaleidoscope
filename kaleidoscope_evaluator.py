import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_double

from AST import FunctionNode
from LLVM_code_generator import LLVMGenerator
from kaleidoscope_parser import Parser


class Evaluator:
    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.parser = Parser()
        self.generator = LLVMGenerator()

        self.target = llvm.Target.from_default_triple()

    def evaluate(self, string):
        ast = self.parser.parse(string)
        self.generator.generate_llvm(ast)
        if not (isinstance(ast, FunctionNode) and ast.is_anonymous()):
            return None

        llvm_mod = llvm.parse_assembly(str(self.generator.module))
        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvm_mod, target_machine) as ee:
            ee.finalize_object()

            func = llvm_mod.get_function(ast.prototype.name)
            fptr = CFUNCTYPE(c_double)(ee.get_pointer_to_function(func))

            result = fptr()
            return result
