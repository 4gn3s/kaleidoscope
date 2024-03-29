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
        self._add_builtins(self.generator.module)

        self.target = llvm.Target.from_default_triple()

    def _add_builtins(self, module):
        import llvmlite.ir as ir
        # Add the declaration of putchar
        putchar_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        putchar = ir.Function(module, putchar_ty, 'putchar')

        # Add putchard
        putchard_ty = ir.FunctionType(ir.DoubleType(), [ir.DoubleType()])
        putchard = ir.Function(module, putchard_ty, 'putchard')
        irbuilder = ir.IRBuilder(putchard.append_basic_block('entry'))
        ival = irbuilder.fptoui(putchard.args[0], ir.IntType(32), 'intcast')
        irbuilder.call(putchar, [ival])
        irbuilder.ret(ir.Constant(ir.DoubleType(), 0))

    def evaluate(self, string, optimize=True):
        ast = self.parser.parse(string)
        self.generator.generate_llvm(ast)
        if not (isinstance(ast, FunctionNode) and ast.is_anonymous()):
            return None

        # print("-------------- Generated -------------------")
        # print(str(self.generator.module))
        llvm_mod = llvm.parse_assembly(str(self.generator.module))

        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 2
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvm_mod)
            # print("-------------- Optimized -------------------")
            # print(str(llvm_mod))

        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvm_mod, target_machine) as ee:
            ee.finalize_object()

            func = llvm_mod.get_function(ast.prototype.name)
            fptr = CFUNCTYPE(c_double)(ee.get_pointer_to_function(func))

            result = fptr()
            return result
