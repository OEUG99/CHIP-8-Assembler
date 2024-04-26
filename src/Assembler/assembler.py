from src.Assembler.lexer import Lexer
from src.Assembler.parser import Parser

class Assembler:

    def __init__(self):
        self.lexer = Lexer()

    def assemble(self, file_name):
        token_sequence_list = self.lexer.analyze_file(file_name)

        print("TOKEN_SEQUENCE_LIST:")
        print(token_sequence_list)
        print('\n')


        parser = Parser(token_sequence_list)
        nodes = parser.parse_expression()
        nodes.print_tree()







