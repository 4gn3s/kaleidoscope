# Kaleidoscope compiler to LLVM

Based on [http://www.llvmpy.org/llvmpy-doc/dev/doc/kaleidoscope/index.html](http://www.llvmpy.org/llvmpy-doc/dev/doc/kaleidoscope/index.html).
Written in Python 3.4

## Kaleidoscope grammar

    program          : [[statement | expression] Delimiter ? ]*;
    statement        : [declaration | definition];
    declaration      : extern prototype;
    definition       : def prototype expression;
    prototype        : Ident OpeningParenthesis [Ident Comma ?]* ClosingParenthesis;
    expression       : [primary_expr (Op primary_expr)*];
    primary_expr     : [Ident | Number | call_expr | parenthesis_expr];
    call_expr        : Ident OpeningParenthesis [expression Comma ?]* ClosingParenthesis;
    parenthesis_expr : OpeningParenthesis expression ClosingParenthesis;
