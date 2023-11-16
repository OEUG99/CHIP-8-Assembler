class Node:

    def __init__(self):
        self.children = []

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


class MnemoniccNode(Node):

    def __iter__(self, value, *args):
        super().__init__()
        self.value = value
        self.args = args


class AssignmentOperationNode:

    def __init__(self, variable, operation, value_node):
        super().__init__()
        self.variable = variable
        self.operation = operation
        self.value_mode = value_node

    def __repr__(self):
        return f"({self.variable} {self.operation} {self.value_mode})"


class Parser:

    def __init__(self):
        self.current_token = None
        self.token_sequences = None
        self.tokens = None

    def parse_sequence(self, token_sequence):
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





    def parse_old(self, token_sequences):
        self.token_sequences = iter(token_sequences)
        self.current_token_sequence = next(self.token_sequences)
        self.tokens = iter(self.current_token_sequence)
        self.next_token()  # grab the first token.
        return self.expression()

    def next_token(self):
        try:
            self.current_token = next(self.tokens)  # Advance to next token
        except Exception:  # If Token Sequence ends...
            try:
                self.tokens = iter(next(self.current_token_sequence))  # Start next Token Sequence
                self.current_token = next(self.tokens)  # Get the first token of the next sequence
            except Exception:  # If there are no more Token Sequences
                self.current_token = None  # No more tokens

    def current_token_is(self, type, value=None):
        if self.current_token is None:
            return False
        if self.current_token.type != type:
            return False
        if value is not None and self.current_token.value not in value:
            return False

        return True

    def expression(self):

        node = self.term()

        while self.current_token_is("arithmetic_operator", ("+", "-")):
            operation = self.current_token.value
            self.next_token()
            node = BinaryOperationNode(left_node=node, operation=operation, right_node=self.term())

        while self.current_token_is("assignment_operator", ("=",)):
            operation = self.current_token.value
            self.next_token()
            node = AssignmentOperationNode(variable=node, operation=operation, value_node=self.expression())

        return node

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.next_token()
        else:
            raise Exception("Invalid Syntax")

    def term(self):
        node = self.factor()

        while self.current_token_is("arithmetic_operator", ("*", "/")):
            operation = self.current_token.value
            self.next_token()
            node = BinaryOperationNode(left_node=node, operation=operation, right_node=self.factor())

        return node

    def factor(self):
        token = self.current_token
        if token.type == "number":
            self.eat("number")
            return NumberNode(value=token.value)
        elif token.type == "register":
            self.eat("register")
            return RegisterNode(value=token.value)
        elif token.value == "(":  # If token is an opening parenthesis
            self.eat("(")
            node = self.expression()
            self.eat(")")
            return node
        elif token.type == "EOL":
            self.eat("EOL")
            return EOLNode(value=token.value)
