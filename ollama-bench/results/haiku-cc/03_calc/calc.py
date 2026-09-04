class Tokenizer:
    """Tokenizes arithmetic expressions into a stream of tokens."""

    def __init__(self, expr):
        self.expr = expr
        self.pos = 0

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1

    def get_next_token(self):
        """Get the next token from the expression."""
        self.skip_whitespace()

        if self.pos >= len(self.expr):
            return None

        char = self.expr[self.pos]

        # Handle operators and parentheses
        if char in '+-*/()':
            self.pos += 1
            return char

        # Handle numbers (integers, decimals, and .5 format)
        if char.isdigit() or char == '.':
            start = self.pos
            while self.pos < len(self.expr) and (self.expr[self.pos].isdigit() or self.expr[self.pos] == '.'):
                self.pos += 1
            return float(self.expr[start:self.pos])

        # Unknown character
        raise ValueError(f"Unknown character: {char}")


class Parser:
    """Recursive-descent parser for arithmetic expressions."""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.get_next_token()

    def parse(self):
        """Parse the entire expression."""
        if self.current_token is None:
            raise ValueError("Empty expression")
        result = self.expr()
        if self.current_token is not None:
            raise ValueError("Unexpected token after expression")
        return result

    def expr(self):
        """Parse addition and subtraction (lowest precedence)."""
        result = self.term()

        while self.current_token in ['+', '-']:
            op = self.current_token
            self.current_token = self.tokenizer.get_next_token()
            right = self.term()
            if op == '+':
                result = result + right
            else:
                result = result - right

        return result

    def term(self):
        """Parse multiplication and division (higher precedence)."""
        result = self.factor()

        while self.current_token in ['*', '/']:
            op = self.current_token
            self.current_token = self.tokenizer.get_next_token()
            right = self.factor()
            if op == '*':
                result = result * right
            else:
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                result = result / right

        return result

    def factor(self):
        """Parse factor (delegates to unary)."""
        return self.unary()

    def unary(self):
        """Parse unary plus and minus operators."""
        if self.current_token in ['+', '-']:
            op = self.current_token
            self.current_token = self.tokenizer.get_next_token()
            result = self.unary()
            if op == '-':
                return -result
            else:
                return result

        return self.primary()

    def primary(self):
        """Parse primary expressions (numbers and parenthesized expressions)."""
        # Handle numbers
        if isinstance(self.current_token, float):
            result = self.current_token
            self.current_token = self.tokenizer.get_next_token()
            return result

        # Handle parenthesized expressions
        if self.current_token == '(':
            self.current_token = self.tokenizer.get_next_token()
            result = self.expr()
            if self.current_token != ')':
                raise ValueError("Missing closing parenthesis")
            self.current_token = self.tokenizer.get_next_token()
            return result

        # Unexpected end of expression
        if self.current_token is None:
            raise ValueError("Unexpected end of expression")

        # Unexpected token
        raise ValueError(f"Unexpected token: {self.current_token}")


def evaluate(expr: str) -> float:
    """
    Evaluate an arithmetic expression given as a string.

    Supports:
    - Operators: +, -, *, /
    - Parentheses for grouping
    - Unary minus (e.g., -3 * -2)
    - Integer and decimal literals (2, 3.5, .5)
    - Standard operator precedence (* / before + -)
    - Left-to-right associativity
    - Arbitrary whitespace

    Returns a float.

    Raises:
    - ValueError: For invalid input (unbalanced parentheses, unknown characters,
                  empty string, trailing operators, etc.)
    - ZeroDivisionError: For division by zero
    """
    if not expr or not expr.strip():
        raise ValueError("Empty expression")

    tokenizer = Tokenizer(expr)
    parser = Parser(tokenizer)
    return parser.parse()
