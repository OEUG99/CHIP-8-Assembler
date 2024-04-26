class Node:

    def __init__(self, value=None):
        self.children = []
        self.value = value

    def append(self, node):
        self.children.append(node)

    def __repr__(self):
        return f"Node({repr(self.children)})"

    def print_tree(self, depth=0):
        print(f"{depth}  " * depth, end="| ")
        print(f"{self.value}")
        for child in self.children:
            child.print_tree(depth + 1)


class ArithmeticNode(Node):
    def __init__(self, operator):
        super().__init__(value=operator)


class AssignmentNode(Node):
    def __init__(self, operator):
        super().__init__(value="=")


class RelationalNode(Node):
    def __init__(self, operator):
        super().__init__(value="=")


class Scope:
    def __init__(self):
        self.variables = {}

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def get_variable(self, name):
        return self.variables.get(name)


class Parser:

    def __init__(self, token_list):
        self.token_list = token_list
        self.current_token = self.token_list.dequeue()
        self.tree = Node(value="dumby")
        self.head = self.tree
        self.context_stack = []
        self.scopes = [Scope()]  # Initialize with global scope

    def push_context(self, context):
        self.context_stack.append(context)

    def pop_context(self):
        return self.context_stack.pop()

    def current_context(self):
        if self.context_stack:
            return self.context_stack[-1]
        else:
            return None

    def enter_scope(self):
        self.scopes.append(Scope())

    def current_scope(self):
        return self.scopes[-1]

    def exit_scope(self):
        return self.scopes.pop()

    def eat(self, token_type):

        if self.current_token.type == token_type:
            self.current_token = self.token_list.dequeue()
        else:
            raise SyntaxError('Invalid syntax')

    def parse_lines(self):
        while not self.token_list.is_empty():
            self.head = self.tree
            expression = self.parse_expression()

            # Check for end of line delimiter
            if self.current_token.type == 'EOL':
                self.eat('EOL')
            elif self.current_token.type == 'EOF':
                self.eat('EOF')
                return self.tree

            else:
                raise SyntaxError(
                    f'Expected semicolon at the end of expression -- {self.current_token.type, self.current_token.value}')

            # You can do something with the parsed expression, such as adding it to a list
            # or processing it further
            print("Parsed expression:", expression)

    def parse_term(self):
        node_left = self.parse_factor()

        while self.current_token.type == "arithmetic_operator" and self.current_token.value in ("*", "/"):
            operator_token = self.current_token
            self.eat(operator_token.type)
            node_right = self.parse_factor()

            # Create term node with operator and left/right nodes
            term_node = Node(value=operator_token.value)
            term_node.children.append(node_left)
            term_node.children.append(node_right)

            # Update left node for next iteration
            node_left = term_node

        return node_left

    def parse_factor(self):
        token = self.current_token
        if token.type == 'register':
            self.eat("register")
            # Create and return a node for the register value
            return Node(value=token.value)  # Assuming token.value holds the register value
        elif token.type == "number":
            self.eat("number")
            return Node(value=token.value)
        elif token.type == "EOF":
            self.eat("EOF")
            return Node(value=token.value)
        elif token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expression()
            self.eat("RPAREN")
            return node
        else:
            raise SyntaxError('Invalid syntax')

    def parse_expression(self):
        token = self.current_token

        if token.type in ['number', 'register']:
            next_token = self.token_list.peek()
            if next_token.type == "arithmetic_operator" and next_token.value in (
                    "+", "-"):  # + or - because * / are terms
                return self.parse_arithmetic_expressions()
        elif token.type == "LPAREN":
            return self.parse_term()

    def parse_arithmetic_expressions(self):
        node_left = self.parse_term()

        while self.current_token.type == "arithmetic_operator":

            operator_token = self.current_token
            self.eat("arithmetic_operator")
            node_right = self.parse_term()

            # Create a sub-tree for the operation.
            operator_node = ArithmeticNode(operator=operator_token)
            operator_node.children.append(node_left)
            operator_node.children.append(node_right)

            # Append sub-tree to the current head node if it's not the root node.
            if self.head != self.tree:
                self.head.children.append(operator_node)
            else:
                # If it's the root node, update the head to the operator node.
                self.head = operator_node
                self.tree = operator_node

            # For cases when there are multple arthmetic operation in one line
            # we need to set left to the previous operator.
            node_left = operator_node

        return node_left


    def parse_if_expressions(self):
        self.eat("keyword")
        condition = self.parse_expression()
        pass


    def parse_scope_block_expression(self):
        self.eat('LBRACE')
        self.enter_scope()  # Enter a new scope

        # Parse expressions within the scope block
        expressions = []
        while self.current_token.type != '}':  # looping through all expressions until we meet close scope.
            expression = self.parse_expression()
            expressions.append(expression)

        self.eat('}')  # Consume the '}' token
        exited_scope = self.exit_scope()  # Exit the current scope

        # Handle variable declarations within the scope block
        # Note: this might not be needed since we only have registers to work with.
        for var in exited_scope.variables.values():
            self.current_scope().add_variable(var)

        return expressions

    def parse_relational_operator(self):
        node_left = self.parse_term()

        while self.current_token.value in ['>', '<', '<=', '>=', "==", "!="]:
            operator_node = Node(value=self.current_token.value)
            self.eat(self.current_token.type)

            node_right = self.parse_expression()

            operator_node.append(node_left)
            operator_node.append(node_right)

            # Append the operator node to the current head node if it's not the root node
            if self.head != self.tree:
                self.head.children.append(operator_node)
            else:
                # If it's the root node, update the head to the operator node
                self.head = operator_node
                self.tree = operator_node

            node_left = operator_node

        else:
            return node_left  # Return the operator node

    def parse_assignment_expressions(self):
        node_left = self.parse_term()

        while self.current_token.type == "assignment_operator":
            self.eat("assignment_operator")
            node_right = self.parse_expression()

            # Create a sub-tree for the operation.
            operator_node = Node(value="=")
            operator_node.children.append(node_left)
            operator_node.children.append(node_right)

            # Append sub-tree to the current head node if it's not the root node.
            if self.head != self.tree:
                self.head.children.append(operator_node)
            else:
                # If it's the root node, update the head to the operator node.
                self.head = operator_node
                self.tree = operator_node

            # For cases when there are multple arthmetic operation in one line
            # we need to set left to the previous operator.
            node_left = operator_node

        return node_left
