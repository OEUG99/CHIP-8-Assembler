class Node:

    def __init__(self, value=None):
        self.children = []
        self.value = value

    def __repr__(self):
        return f"Node({repr(self.children)})"


class NumberNode(Node):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class RegisterNode(Node):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class BinaryOperationNode(Node):

    def __init__(self, left_node, operation, right_node):
        super().__init__()
        self.left_node = left_node
        self.operation = operation
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node} {self.operation} {self.right_node})"


class EOLNode(Node):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class MnemonicNode(Node):

    def __init__(self, mnemonic):
        super().__init__()
        self.mnemonic = mnemonic

    def __repr__(self):
        return f"{self.mnemonic}"


class InstructionNode(Node):

    def __init__(self, mnemonic_node, first_operand=None, second_operand=None, third_operand=None):
        super().__init__()

        self.mnemonic_node = mnemonic_node
        self.first_operand = first_operand
        self.second_operand = second_operand
        self.third_operand = third_operand

    def __repr__(self):
        operand_string = f"{self.first_operand}, {self.second_operand}, {self.third_operand}"

        return f"{self.mnemonic_node}({operand_string})"


class AssignmentOperationNode(Node):

    def __init__(self, variable, operation, value_node):
        super().__init__()
        self.variable = variable
        self.operation = operation
        self.value_mode = value_node

    def __repr__(self):
        return f"({self.variable} {self.operation} {self.value_mode})"


class RelationalNode(Node):

    def __init__(self, left_node, operation, right_node):
        super().__init__()
        self.left_node = left_node
        self.operation = operation
        self.right_node = right_node

    def __repr__(self):
        return f"({self.left_node} {self.operation} {self.right_node})"


class IfStatementNode(Node):

    def __init__(self, condition, true_statement, false_statement=None):
        super().__init__()
        self.condition = condition
        self.true_statement = true_statement
        self.false_statement = false_statement

    def __repr__(self):
        return f"if({self.condition}, then {self.true_statement} else {self.false_statement})"


class WhileStatementNode(Node):

    def __init__(self, condition, true_statement):
        super().__init__()
        self.condition = condition
        self.true_statement = true_statement

    def __repr__(self):
        return f"while({self.condition}, then {self.true_statement})"

class MultiLineNode(Node):

    def __init__(self, expression_list):
        super().__init__()
        self.expression_list = expression_list

    def __repr__(self):
        return f"ml({', '.join([repr(i) for i in self.expression_list])})"


class Parser:

    def __init__(self):
        self.current_token = None
        self.token_sequences = None
        self.tokens = None
        self.scope_level = 0

    def parse_sequence(self, token_sequence):
        self.current_token_sequence = token_sequence
        self.tokens = iter(token_sequence)
        self.next_token()  # grab the first token.
        return self.expression()

    def parse_sequences(self, token_sequences):
        """
        Similar to parse_sequence(), but for multiple token sequences.

        :param token_sequences:
        :type token_sequences:
        :return:
        :rtype:
        """

        previous_node = Node()  # Create a head node to hold the abstract syntax tree.

        AST = previous_node  # We set the head node as the abstract syntax tree, to traverse it later.

        for token_sequence in token_sequences:
            previous_node = AST  # Set the previous node to the head node.
            new_node = self.parse_sequence(token_sequence)
            previous_node.children.append(new_node)

        return AST

    def next_token(self):
        try:
            self.current_token = next(self.tokens)  # Advance to next token
        except Exception:  # If Token Sequence ends...
            self.current_token = None  # No more tokens

    def current_token_is(self, type, value=None):
        if self.current_token is None:
            return False
        if self.current_token.type != type:
            return False
        if value is not None and self.current_token.value not in value:
            return False

        return True

    def eat(self, token_type):

        if self.current_token is None:
            return False

        if self.current_token.type == token_type:
            self.next_token()
        else:
            raise Exception(f"Invalid Syntax: Expected {token_type}, got {self.current_token.type}")

    def multiline_expressions(self):
        node_list = []

        self.eat("LBRACE")

        while not self.current_token_is("RBRACE") and self.scope_level > 0:

            if self.current_token_is("keyword", "IF"):
                self.scope_level -= 1
                node_list.append(self.conditional_statement("IF"))

            elif self.current_token_is("keyword", "WHILE"):
                self.scope_level -=1
                node_list.append(self.conditional_statement("WHILE"))
            else:
                node_list.append(self.expression())
                if self.current_token_is("EOL"):  # Check if the ';' token is reached.
                    self.eat("EOL")  # Consume the ';' token.

        self.next_token()
        return MultiLineNode(node_list)

    def conditional_statement(self, keyword):


        # First we consume the if keyword.
        self.eat("keyword")

        # Now we must parse the condition.
        self.next_token()  # advance to the next token, which is the start of the condition.
        condition = self.expression()  # now, the next token is a (, which is the start of an expression.
        self.eat("RPAREN")  # we are now at the end of the condition, so we eat the ) symbol.


        # now we must parse the multiline expression, which is the true statement.
        # we are now at the start of the multiline expression, are within {}.
        self.scope_level += 1
        true_statement = self.multiline_expressions()
        self.scope_level -= 1


        # we are now at the end of the multiline expression, so we eat the } symbol.

        if keyword == "IF":

            # We now check for the false statement (else statement).
            if self.current_token_is("keyword", ("ELSE",)):
                self.next_token()
                self.eat("LBRACE")
                self.scope_level += 1
                false_statement = self.multiline_expressions()
                self.scope_level -= 1
                self.eat("RBRACE")
                node = IfStatementNode(condition=condition, true_statement=true_statement, false_statement=false_statement)
                return node

            # if there is no else statement, we just return the if statement node.
            node = IfStatementNode(condition=condition, true_statement=true_statement)
            return node
        elif keyword == "WHILE":
            # if there is no else statement, we just return the if statement node.
            node = WhileStatementNode(condition=condition, true_statement=true_statement)
            return node


    def expression(self):

        node = self.term()


        if self.current_token_is("mnemonic"):
            if self.current_token is not "DRW":
                mnemonic = self.current_token.value
                self.next_token()

                node = InstructionNode(mnemonic_node=MnemonicNode(mnemonic),
                                       first_operand=self.factor(),
                                       second_operand=self.factor())
            else:
                mnemonic = self.current_token.value
                self.next_token()

                node = InstructionNode(mnemonic_node=MnemonicNode(mnemonic),
                                       first_operand=self.factor(),
                                       second_operand=self.factor(),
                                       third_operand=self.factor())

        if self.current_token_is("arithmetic_operator", ("+", "-")):
            operation = self.current_token.value
            self.next_token()
            node = BinaryOperationNode(left_node=node, operation=operation, right_node=self.term())

        if self.current_token_is("relational_operator"):
            operation = self.current_token.value
            self.next_token()
            node = RelationalNode(left_node=node, operation=operation, right_node=self.term())
            return node

        if self.current_token_is("keyword", ("IF",)):
            return self.conditional_statement("IF")

        if self.current_token_is("assignment_operator", ("=",)):

            operation = self.current_token.value
            self.next_token()
            return AssignmentOperationNode(variable=node, operation=operation, value_node=self.expression())

        return node

    def term(self):
        node = self.factor()

        while self.current_token_is("arithmetic_operator", ("*", "/")):
            operation = self.current_token.value
            self.next_token()
            node = BinaryOperationNode(left_node=node, operation=operation, right_node=self.factor())

        return node

    def factor(self):
        token = self.current_token

        print(token, self.scope_level)

        if token.type == "number":
            self.eat("number")
            return NumberNode(value=token.value)
        elif token.type == "register":
            self.eat("register")
            return RegisterNode(value=token.value)
        elif token.type == "LPAREN":  # If token is an opening parenthesis
            self.eat("LPAREN")
            node = self.expression()
            self.eat("RPAREN")
            return node
        elif token.type == "LBRACE":
            self.eat("LBRACE")
            node = self.multiline_expressions()
            self.eat("RBRACE")
            return node

