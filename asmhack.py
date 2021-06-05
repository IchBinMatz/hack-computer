# dies ist ein Assembler für die Programmiersprache Hack
# aus dem Buch "The Elements of Computing - building a modern computer from
# first principles"
import re
import click
from pathlib import Path

SYMBOLS_BUILTIN = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576,
}

SYMBOLS_COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

SYMBOLS_DEST = {
    "null": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

SYMBOLS_JUMP = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

class Parser():
    
    A_COMMAND = "A_COMMAND"
    C_COMMAND = "C_COMMAND"
    L_COMMAND = "L_COMMAND"
    NO_COMMAND = "NO_COMMAND"
    def __init__(self, asm : Path) -> None:
        self.asm : str = ""
        with open(asm, "r") as f:
            self.asm = f.read()
        self.lines = self.asm.splitlines()

    def hasMoreCommand(self) -> bool:
        """Are there more commands in the input?"""
        return bool(self.lines)

    def advance(self):
        """Reads the next command from the input and makes it the
        current command. Should be called only if
        `hasMoreCommand()` is true.
        
        Initially there is no current command
        """
        self.currencommand = self.lines[0]
        self.lines.remove(self.lines[0])
        self.currencommand.strip()
        if self.commandType() == Parser.NO_COMMAND:
            print("no line")
            self.advance()
    
    def commandType(self) -> str:
        """Returns the type of the current command:
        
        * A_COMMAND for @Xxx where Xxx is either a symbol
        or a decimal number

        * C_COMMAND for `dest=comp;jump`

        * L_COMMAND (actually, pseudo-command) for (Xxx)
        where Xxx is a symbol.
        """
        patternA = re.compile(r"\s*@(\d+|[A-z]+\d*)\s*(//.*)*$")
        patternC = re.compile(r"([AMD]{0,23})=(0|-?1|[DAM][+-|&][1DA]|[!-]*[ADM]);(J(GT|EQ|GE|LT|NE|LE|MP))?\s*(//.*)*$")
        patternL = re.compile(r"\([A-z]\)\s*(//.*)*$")
        
        A = re.match(patternA,self.currencommand)
        C = re.match(patternC,self.currencommand)
        L = re.match(patternL,self.currencommand)

        self.current_symbol = ""
        self.current_dest = ""
        self.current_comp = ""
        self.current_jump = ""
        if A:
            self.current_symbol = A.group(1)
            return Parser.A_COMMAND
        elif C:
            self.current_dest = C.group(1)
            self.current_comp = C.group(2)
            self.current_jump = C.group(3)
            if not self.current_dest:
                self.current_dest = "null"
            return Parser.C_COMMAND
        elif L:
            self.current_symbol = L.group(1)
            if not self.current_jump:
                self.current_jump = "null"
            return Parser.L_COMMAND
        else:
            return Parser.NO_COMMAND

    def symbol(self) -> str:
        """Returns the symbol or decimal Xxx of the current
        command @Xxx or (Xxx).
        Should be called only when `commandType()` is
        A_COMMAND or L_COMMAND
        """
        return self.current_symbol 

    def dest(self) -> str:
        """Returns the `dest` mnemonic in the current- C_COMMAND
        (8 Possibilities). Should be called only when 
        `commandType()` is C_COMMAND
        """
        return self.current_dest

    def comp(self) -> str:
        """Returns the `comp` mnemonic in the current C_COMMAND
        (28 Possibilities). Should be called only when 
        `commandType()` is C_COMMAND
        """
        return self.current_comp
    
    def jump(self) -> str:
        """Returns the `jump` mnemonic in the current C_COMMAND
        (8 Possibilities). Should be called only when
        `commandType` is C_COMMAND
        """
        return self.current_jump



@click.command()
@click.argument(
    "asm-file", type=click.Path(exists=True, file_okay=True, dir_okay=False)
)
def main(asm_file):
    asm_file = Path(asm_file)
    if not asm_file.suffix == ".asm":
        print(asm_file.suffix)
        print("given file is not an asm-file")
        return 1
    hack : str = ""
    parser = Parser(asm_file)
    while parser.hasMoreCommand():
        parser.advance()
        ctype = parser.commandType
        line = ""
        if ctype == Parser.A_COMMAND:
            address = parser.symbol()
            line += f"{address:016b}"
            pass
        elif ctype == Parser.C_COMMAND:
            line += "111"
            line += SYMBOLS_COMP[parser.comp()]
            line += SYMBOLS_DEST[parser.dest()]
            line += SYMBOLS_JUMP[parser.jump()]
            pass
        elif ctype == Parser.L_COMMAND:
            pass
        print(line)
        hack += line
        hack += "\n"




if __name__ == "__main__":
    main()
