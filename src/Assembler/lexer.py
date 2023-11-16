import re
from typing import Union


class Token:

    def __init__(self, type, value):
        self.type = type
        self.value = value
        self.__check_validity()

    def __check_validity(self):
        if self.type == "hex":
            # check it is a valid hex number and not over 8 bits:
            if int(self.value, 16) > 0xFFF:
                raise ValueError("Hex number is too large for 16 bit system")
            else:
                self.value = int(self.value, 16)  # convert hex string to int

    def __repr__(self):
        return f"Token({repr(self.type)}, {repr(self.value)})"



class TokenSequence:

    def __init__(self, obj=None):
        if obj is None:
            obj = []
        self.tokens = obj

    def enqueue(self, token: Token):
        self.tokens.append(token)

    def dequeue(self, __index=0):

        if len(self.tokens) == 0:
            return None

        return self.pop(__index)

    def pop(self, __index=-1):
        return self.tokens.pop(__index)

    def __len__(self):
        return len(self.tokens)

    def __repr__(self):
        return f"TokenSequence({repr(self.tokens)})"

    def __next__(self):
        result = self.dequeue()

        if len(self.tokens) == 0:
            raise Exception()

        return result

    def __iter__(self):
        return self





opcode_Mnemonic = {
    "LD",
    "ADD",
    "SUB",
    "OR",
    "AND",
    "XOR",
    "SHR",
    "SUBN",
    "SHL",
    "RND",
    "DRW",
    "SKP",
    "SKNP",
    "JP",
    "CALL",
    "SE",
    "SNE",
    "CLS",
    "RET",
    "SYS",
}

derective_Mnemonic = {
    "DB",
}

operators = {
    "arithmetic": {
        "+",
        "-",
        "*",
        "/",
        "%",
    },

    "assignment": {
        "=",
    },

    "relational": {
        "==",
        "!=",
        ">",
        "<",
        ">=",
        "<=",
    },
    "logical": {
        "&&",
        "||",
        "!",
        "AND",
        "OR",
        "NOT",
    }
}

kewords = {
    "IF",
    "ELSE",
    "WHILE",
}


class Lexer:

    def __init__(self):
        pass

    @staticmethod
    def analyze_string(string: str) -> Union[TokenSequence, None]:
        """
        Analyzes a line of code and returns a list of tokens
        :param string:
        :type string:
        :return:
        :rtype:
        """

        token_sequence = TokenSequence()

        lexemes = re.findall(r"([a-zA-Z0-9_:&]+|[+\-*/=><\(\)\n;])", string)

        for lexeme in lexemes:

            # determine if lexeme is a new line
            if lexeme == ";":
                token_sequence.enqueue(Token("EOL", lexeme))
                continue

            # Determine if lexeme is a math operator
            if lexeme in operators["arithmetic"]:
                token_sequence.enqueue(Token("arithmetic_operator", lexeme))
                continue

            # Determine if lexeme is an assignment operator:
            elif lexeme in operators["assignment"]:
                token_sequence.enqueue(Token("assignment_operator", lexeme))
                continue

            # if lexeme is a directive
            if lexeme in derective_Mnemonic:
                token_sequence.enqueue(Token("directive", lexeme))
                continue

            # Determine if lexeme is a mnemonic
            if lexeme in opcode_Mnemonic:
                token_sequence.enqueue(Token("mnemonic", lexeme))
                continue

            # Determine if lexeme is a v-register
            v_register_match = re.match(r"([Vv]+\d{1,2})", lexeme)
            if v_register_match is not None:
                token_sequence.enqueue(Token("register", v_register_match.group()))
                continue

            # Determine if lexeme is the [I] register. (memory address register)
            if re.match(r"^\s*\[(I|i)\]\s*$", lexeme):  # Match [I] or [i] ignoring case and spaces
                # Add token to the token list
                # we declare its type as i_memory_register and not register because it is 16 bits, other
                # registers are 8 bits. This is important for the assembler to know.
                token_sequence.enqueue(Token("i_memory_register", lexeme.strip().upper()))
                continue

            # Determine if lexeme is the [I] register. (memory address register)
            if re.match(r"^\s*\[(I|i)\],?\s*$", lexeme):  # Match [I] or [i], ignoring case and spaces, optional comma
                # Add token to the token list, stripping off any whitespace, comma and converting to uppercase
                token_sequence.enqueue(Token("i_memory_register", lexeme.strip().upper().rstrip(',')))
                continue

            # Determine if lexeme is the DT register.
            dt_register_match = re.match(r"\b[DTdt](?=,)?", lexeme)
            if dt_register_match is not None:
                token_sequence.enqueue(Token("dt_register", dt_register_match.group()))
                continue

            # Determine if lexeme is the ST register.
            st_register_match = re.match(r"\b[STst](?=,)?", lexeme)
            if st_register_match is not None:
                token_sequence.enqueue(Token("st_register", st_register_match.group()))
                continue

            # Determine if lexeme is the F register. (flag register)
            f_register_match = re.match(r"\b[Ff](?=,)?", lexeme)
            if f_register_match is not None:
                token_sequence.enqueue(Token("f_register", f_register_match.group()))
                continue

            # Determine if lexeme is the K register. (keyboard register)
            k_register_match = re.match(r"\b[Kk](?=,)?", lexeme)
            if k_register_match is not None:
                token_sequence.enqueue(Token("k_register", k_register_match.group()))
                continue

            # Determine if lexeme is the B register. (binary coded decimal register)
            b_register_match = re.match(r"\b[Bb](?=,)?", lexeme)
            if b_register_match is not None:
                token_sequence.enqueue(Token("b_register", b_register_match.group()))
                continue

            # Determine if lexeme is a hex number
            hex_number_match = re.match(r"0x([0-9aA-ff]*)", lexeme)
            if hex_number_match is not None:
                token_sequence.enqueue(Token("number", hex_number_match.group()))
                continue

            # Determine if lexeme is a decimal number
            decimal_number_match = re.match(r"\b[0-9]+\b", lexeme)
            if decimal_number_match is not None:
                # Convert decimal number to hex
                hex_number = hex(int(decimal_number_match.group()))
                token_sequence.enqueue(Token("number", hex_number))
                continue

            # determine if lexeme is a label reference
            label_reference_match = re.match(r"\&[A-Za-z_-]*", lexeme)
            if label_reference_match is not None:
                value = label_reference_match.group().strip('&')
                token_sequence.enqueue(Token("label_reference", value))
                continue

            # Deterine if lexeme is a label
            label_match = re.match(r"^[aA-zZ_]+(?=:)", lexeme)
            if label_match is not None:
                token_sequence.enqueue(Token("label", label_match.group()))
                continue

        if len(token_sequence) == 0:
            return None

        return token_sequence

    def analyze_file(self, file_path: str):
        """
        Analyzes a file and returns a list of token sequences
        :param file_path:
        :type file_path:
        :return:
        :rtype:
        """

        result = []

        with open(file_path, 'rb') as file:
            # read the source file remove all comments.
            with open(file_path, "r") as file:
                contents = file.read()

                lines = contents.splitlines()

                for line in lines:
                    token_sequence = self.analyze_string(line)
                    if token_sequence is not None:
                        result.append(token_sequence)

            return result
