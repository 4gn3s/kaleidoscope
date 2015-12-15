import llvmlite.binding as llvm

from LLVM_code_generator import LLVMGenerator
from kaleidoscope_parser import Parser


class Evaluator:
    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.parser = Parser()
        self.codegen = LLVMGenerator()

        self.target = llvm.Target.from_default_triple()

    def evaluate(self, string):
        ast = self.parser.parse(string)
        self.codegen.generate(ast)
        print('LLVM IR')
        print(str(self.codegen.module))
