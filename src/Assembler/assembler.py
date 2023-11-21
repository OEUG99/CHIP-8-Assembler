from src.Assembler.lexer import Lexer
from src.Assembler.parser import Parser

class Assembler:

    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def assemble(self, file_name):
        token_sequence_list = self.lexer.analyze_file(file_name)



        AST = self.parser.parse_sequence(token_sequence_list)
        print(AST)
