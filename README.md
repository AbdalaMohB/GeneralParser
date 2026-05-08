# GeneralParser
A parser that uses your context free grammar (as a python dictionary) to detect errors in files.

## Usage
To use GeneralParser replace the cfgmap variable inside parse.py with your own context free grammar using the premade one as a blueprint.

### DO NOT change or remove the stmt and block rules as they are essential. The stmthead and meta rules may be modified, but not removed.

* Place your statements inside of stmthead.
* Any statement that should not appear inside a block should be placed in the meta rule.
* The parser requires a separator between statements be defined to function (The default is a semi colon, but it may be changed).
* Due to the provided lex.py not making tokens out of spaces and newlines, they cannot be used as statement separators by default.
* The provided gui.py is a simple tkinter gui that shows errors as you type.

This program is best used for simple syntax verification or for testing or when flexibility is more important than performance. It should not be used in performance critical applications as it is made in an interpreted language for increased flexibility.
