class Assembler:

    def __init__(self):
        print("Assembler initialized.")
        self.intermediate_buffer = ()
        self.final_buffer = []
        self.starting_address = None   # this is the address where the program will start executing from.
        self.program_counter = 0x200
        self.sprite_counter = 0x000
        self.label_table = dict()

    def fetch_opcode(self, words) -> str:

        def determine_SE(tuple):
            # determine which opcode based on the final parameter

            operand_1 = tuple[1]
            operand_2 = tuple[2]

            result = None

            if operand_2.startswith("#"):
                # it's SE VX, #
                result = '3{}{}'.format(operand_1, operand_2)
            elif operand_2.startswith("V"):
                # it's SE VX, VY
                result = '5{}{}0'.format(operand_1, operand_2)
            else:
                raise ValueError('SE instruction is invalid.')

            # remove the 'vx' and 'vy' from the opcode and the # from the second parameter then return.
            return result.replace('#', '').replace('V', '')

        def determine_ADD(tuple):

            operand_1 = tuple[1]
            operand_2 = tuple[2]

            result = None

            if operand_1.capitalize() == "I":
                # it's ADD I, VX
                result = 'F{}1E'.format(operand_2)

            if operand_2.startswith('V'):
                # it's ADD VX, VY
                result = '8{}{}4'.format(operand_1, operand_2)

            if operand_2.startswith('#'):
                # it's ADD VX, #
                result = '7{}{}'.format(operand_1, operand_2)

            if result is None:
                raise ValueError('ADD instruction is invalid.')
            else:
                # remove the 'vx' and 'vy' from the opcode and the # from the second parameter then return.
                return result.replace('#', '').replace('V', '')

        def determine_SNE(tuple):

            operand_1 = tuple[1]
            operand_2 = tuple[2]

            result = None

            if operand_2.startswith("#"):
                # it's SNE VX, #
                result = '4{}{}'.format(operand_1, operand_2)
            elif operand_2.startswith("V"):
                # it's SNE VX, VY
                result = '9{}{}0'.format(operand_1, operand_2)
            else:
                raise ValueError('SNE instruction is invalid.')

            # remove the 'vx' and 'vy' from the opcode and the # from the second parameter then return.
            return result.replace('#', '').replace('V', '')

        def determine_JP(tuple):

            operand_1 = tuple[1]
            operand_2 = tuple[2] if len(tuple) > 2 else None

            result = None

            if operand_1.startswith("V"):
                # it's JP VX, #
                result = 'B{}{}'.format(operand_1, operand_2)
            elif operand_1.startswith("0x"):
                # it's JP #
                operand_1 = operand_1.replace('0x', '')  # remove the 0x from the hex value  before we insert it
                result = '1{}'.format(operand_1)
            else:
                raise ValueError('JP instruction is invalid.')

            # remove the 'vx' and 'vy' from the opcode and the # from the second parameter then return.
            return result.replace('#', '').replace('V', '')

        def determine_LD(tuple_):

            operand_1 = str(tuple_[1])
            operand_2 = str(tuple_[2])

            result = None

            if operand_1.startswith("V") and operand_2.startswith("#"):
                # it's LD VX, #
                operand_2 = operand_2.replace('#', '')
                operand_2 = int(operand_2, 16)
                result = '6{}{}'.format(operand_1, operand_2)
            elif operand_1.startswith("V") and operand_2.startswith("V"):
                # it's LD VX, VY
                result = '8{}{}0'.format(operand_1, operand_2)
            elif operand_1.startswith("I") and operand_2.startswith("0x"):
                # it's LD I, #
                operand_2 = operand_2.replace('0x', '')
                operand_2 = int(operand_2, 16)
                operand_2 = hex(operand_2).replace('0x', '')
                result = 'A{}'.format(operand_2)
            elif operand_1.startswith("[I]") and operand_2.startswith("V"):
                # it's LD [I], VX
                result = 'F{}55'.format(operand_2)
            elif operand_1.startswith("V") and operand_2.startswith("[I]"):
                # it's LD VX, [I]
                result = 'F{}65'.format(operand_1)
            elif operand_1.startswith("V") and operand_2.startswith("DT"):
                # it's LD VX, DT
                result = 'F{}07'.format(operand_1)
            elif operand_1.startswith("V") and operand_2.startswith("K"):
                # it's LD VX, K
                result = 'F{}0A'.format(operand_1)
            elif operand_1.startswith("DT") and operand_2.startswith("V"):
                # it's LD DT, VX
                result = 'F{}15'.format(operand_2)
            elif operand_1.startswith("ST") and operand_2.startswith("V"):
                # it's LD ST, VX
                result = 'F{}18'.format(operand_2)
            elif operand_1.startswith("F") and operand_2.startswith("V"):
                # it's LD F, VX
                result = 'F{}29'.format(operand_2)
            elif operand_1.startswith("B") and operand_2.startswith("V"):
                # it's LD B, VX
                result = 'F{}33'.format(operand_2)

            if result is None:
                raise ValueError('LD instruction is invalid.')
            elif result is not None:
                # remove the 'vx' and 'vy' from the opcode and the # from the second parameter then return.
                result = result.replace('#', '').replace('V', '')
                return result

        opcode_table = {
            # all non-repeating opcodes
            'CLS': '00E0',
            'DRW': 'D{}{}{}',
            'OR': '8{}{}1',
            'RET': '00EE',
            'RND': 'C{}{}',
            'SHL': '8{}{}E',
            'SHR': '8{}{}6',  # Need to check if this template works do it second parameter being optional
            'SKNP': 'E{}A1',
            'SKP': 'E{}9E',
            'SUB': '8{}{}5',
            'SUBN': '8{}{}7',
            'SYS': '0{}{}',
            'XOR': '8{}{}3',
        }

        operand = words[0]
        param1 = words[1]
        param2 = words[2] if len(words) > 2 else None
        param3 = words[3] if len(words) > 3 else None

        result = None

        # fetch the opcode from the opcode table

        if operand in opcode_table:
            unformatted_opcode = opcode_table[operand]

            if param3 is not None:
                # if there are 3 parameters, then we need to format the opcode with all 3 parameters
                result = unformatted_opcode.format(param1, param2, param3).replace('V', '').replace('#', '')
            else:
                # now we format the opcode based on the number of parameters, we also remove the 'vx' and 'vy' from the opcode
                result = unformatted_opcode.format(param1, param2)

        # if the opcode is not in the opcode table, then it is an opcode that shares mnemonics with other opcodes
        # so we need to determine which opcode it is based on the final parameter

        if operand == 'ADD':
            result = determine_ADD(words)
        elif operand == 'SE':
            result = determine_SE(words)
        elif operand == 'SNE':
            result = determine_SNE(words)
        elif operand == 'JP':
            result = determine_JP(words)
        elif operand == 'LD':
            result = determine_LD(words)

        if result is None:
            raise ValueError('Opcode is invalid.')

        # convert to hex and return
        return result

    def handle_directives(self, line):

        directive = line.split()[0]
        parameters = line.split()[1:]

        if directive == '.db':
            # it's a directive

            for parameter in parameters:

                if parameter.startswith("0x"):
                    # it's a hex value
                    parameter = parameter.replace("0x", "")
                    self.intermediate_buffer += (parameter,)
                elif parameter.startswith("#"):
                    # it's a decimal value
                    parameter = parameter.replace("#", "")
                    parameter = parameter.zfill(4)
                self.intermediate_buffer += (parameter,)

                # Every time a .db directive is used, it gets stored first in memory. In order to prevent
                # the interpreter from accidentally executing the data, we need to store the starting address
                # this way we can jump to the starting address after the data has been stored in memory.
                self.starting_address = self.program_counter

                self.program_counter += 1   # go to next address in memory for next instruction


    def read_file(self):

        # read the source file remove all comments.
        with open("source.txt", "r") as file:
            contents = file.read()


        lines = contents.splitlines()

        clean_lines = []

        for count, line in enumerate(lines):

            # remove all all commas.
            line = line.replace(',', '')

            # remove all comments
            if ";" in line:
                line = line.split(";")[0]
                # remove trailing whitespace
                line = line.rstrip()

            clean_lines.append(line)

        lines = clean_lines

        # first pass, handle labels and directives
        # we will build a new list with the lines that are not labels or directives, to use in second pass
        for count, line in enumerate(lines):

            if line == "":
                continue

                # check if it's a directive ignore whitespace
            if line.endswith(":"):
                # it's a new label

                label = line.replace(":", "")
                self.label_table[label] = hex(self.program_counter)
                continue

            if line.startswith("."):
                # it's a directive

                self.handle_directives(line)
                continue

            # Add the line to the intermediate buffer if it's not a label or directive.
            self.intermediate_buffer += (line,)

        print("Intermediate buffer -- first pass: " + str(self.intermediate_buffer))

        # second pass, handle instructions
        for line in self.intermediate_buffer:

            words = line.split()

            # check if its a hex value
            if self.is_hex(line):
                self.final_buffer += (line,)
                self.program_counter += 1
                continue

            # ignore blank lines.
            if len(words) == 0:
                continue

            opcode_obtained = False  # flag to mark if opcode has been processed
            for count, word in enumerate(words):

                key = word[1:]  # remove the $ from the label
                if word.startswith("$") and key in self.label_table:
                    # it's a label
                    words[count] = self.label_table[key]
                    opcode_hex = self.fetch_opcode(words)
                    self.final_buffer += (opcode_hex,)
                    self.program_counter += 2
                    opcode_obtained = True
                    break  # exit the loop early if opcode has been added

            # Only generate opcode if not already done when processing a label
            if not opcode_obtained:
                opcode_hex = self.fetch_opcode(words)
                self.final_buffer += (opcode_hex,)
                self.program_counter += 2


        # if the starting address is not 0x200, then we need to add a JP instruction to jump to the starting address
        # this is due to usage of directives and labels being declared before any instructions are processed. To
        # prevent the interpreter from executing the data (which is not a valid instruction), we need to jump over it.
        if self.starting_address is not None:
            jp_hex = f"1{hex(self.starting_address).replace('0x', '')}"
            self.final_buffer.insert(0, jp_hex)
        print("second pass -- intermediate buffer: " + str(self.final_buffer))

    def write_file(self):
        # convert to bytes and write to file
        with open("output.c8", "wb") as file:
            bytes_ = bytearray()

            for line in self.final_buffer:
                bytes_.append(int(line[:2], 16))
                bytes_.append(int(line[2:], 16))

            print(bytes_)

            file.write(bytes_)

    def convert_to_hex(self, decimal_value):
        return hex(decimal_value).replace('0x', '').upper()

    def is_hex(self, s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False
