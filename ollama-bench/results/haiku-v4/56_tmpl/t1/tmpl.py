class TemplateError(Exception):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"{kind} at {pos}")


# ============================================================================
# PHASE 1: LEXING
# ============================================================================

class Token:
    def __init__(self, kind, body, pos, left_marker=False, right_marker=False):
        self.kind = kind  # 'text', 'interp', 'block', 'comment'
        self.body = body
        self.pos = pos
        self.left_marker = left_marker
        self.right_marker = right_marker


def lex(source):
    """Tokenize template into alternating text and tag tokens."""
    tokens = []
    i = 0

    while i < len(source):
        if i + 1 < len(source) and source[i] == '{':
            next_char = source[i + 1]
            if next_char in ('{', '%', '#'):
                tag_start = i
                opener = source[i:i+2]
                closer_map = {'{{': '}}', '{%': '%}', '{#': '#}'}
                closer = closer_map[opener]

                j = i + 2
                left_marker = False
                if j < len(source) and source[j] == '-':
                    left_marker = True
                    j += 1

                body_start = j
                while j < len(source):
                    if source[j:j+2] == closer:
                        break
                    j += 1

                if j >= len(source):
                    raise TemplateError("unclosed_tag", tag_start)

                body = source[body_start:j]
                right_marker = False
                if body and body[-1] == '-':
                    right_marker = True
                    body = body[:-1]

                kind = {'{{': 'interp', '{%': 'block', '{#': 'comment'}[opener]
                tokens.append(Token(kind, body, tag_start, left_marker, right_marker))
                i = j + 2
            else:
                # Regular character
                tokens.append(Token('text', source[i], i, False, False))
                i += 1
        else:
            # Collect consecutive text
            text_start = i
            while i < len(source):
                if i + 1 < len(source) and source[i] == '{' and source[i + 1] in ('{', '%', '#'):
                    break
                i += 1

            if i > text_start:
                tokens.append(Token('text', source[text_start:i], text_start, False, False))

    return tokens


def apply_whitespace_control(tokens):
    """Apply whitespace trimming based on markers."""
    # Group into text and tag sequences
    result = []
    i = 0

    while i < len(tokens):
        if tokens[i].kind == 'text':
            text = tokens[i].body
            pos = tokens[i].pos

            # Check if previous token is a tag with right marker
            if result and result[-1].kind in ('interp', 'block', 'comment') and result[-1].right_marker:
                text = text.lstrip(' \t\r\n\v\f')

            # Check if next token is a tag with left marker
            if i + 1 < len(tokens) and tokens[i + 1].kind in ('interp', 'block', 'comment') and tokens[i + 1].left_marker:
                text = text.rstrip(' \t\r\n\v\f')

            if text or not (result and result[-1].kind in ('interp', 'block', 'comment')):
                result.append(Token('text', text, pos, False, False))

            i += 1
        else:
            result.append(tokens[i])
            i += 1

    return result


def remove_comments(tokens):
    """Filter out comment tokens."""
    return [t for t in tokens if t.kind != 'comment']


# ============================================================================
# PHASE 2: EXPRESSION PARSING
# ============================================================================

class ExprParser:
    def __init__(self, text, tag_pos):
        self.text = text
        self.tag_pos = tag_pos
        self.pos = 0

    def error(self, kind):
        raise TemplateError(kind, self.tag_pos)

    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\r\n\v\f':
            self.pos += 1

    def peek(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek_word(self):
        """Peek at the next word without consuming it."""
        i = self.pos
        while i < len(self.text) and self.text[i] in ' \t\r\n\v\f':
            i += 1
        if i >= len(self.text):
            return None
        start = i
        while i < len(self.text) and (self.text[i].isalnum() or self.text[i] == '_'):
            i += 1
        return self.text[start:i]

    def parse(self):
        """Main entry point."""
        self.skip_ws()
        expr = self.parse_pipeline()
        self.skip_ws()
        if self.pos < len(self.text):
            self.error("syntax")
        return expr

    def parse_pipeline(self):
        """pipeline := disjunct ( "|" filter )*"""
        expr = self.parse_disjunct()
        while True:
            self.skip_ws()
            if self.pos < len(self.text) and self.text[self.pos] == '|':
                self.pos += 1
                expr = self.parse_filter(expr)
            else:
                break
        return expr

    def parse_filter(self, expr):
        """Parse a filter after seeing |."""
        self.skip_ws()

        # Parse filter name
        if self.pos >= len(self.text):
            self.error("syntax")

        if not (self.text[self.pos].isalpha() or self.text[self.pos] == '_'):
            self.error("syntax")

        name_start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.pos += 1

        if name_start == self.pos:
            self.error("syntax")

        filter_name = self.text[name_start:self.pos]

        self.skip_ws()

        args = []
        if self.pos < len(self.text) and self.text[self.pos] == ':':
            self.pos += 1
            self.skip_ws()

            # Parse arguments
            while True:
                arg = self.parse_filter_arg()
                args.append(arg)
                self.skip_ws()

                if self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_ws()
                else:
                    break

        self.skip_ws()

        # Check what comes next
        if self.pos < len(self.text):
            if self.text[self.pos] == '|':
                pass  # Another filter
            elif self.text[self.pos] not in ' \t\r\n\v\f':
                self.error("syntax")

        return ('filter', expr, filter_name, args)

    def parse_filter_arg(self):
        """Parse a single filter argument."""
        self.skip_ws()

        if self.pos >= len(self.text):
            return ''

        if self.text[self.pos] in ('"', "'"):
            quote = self.text[self.pos]
            self.pos += 1
            result = []
            while self.pos < len(self.text):
                if self.text[self.pos] == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text):
                        self.error("syntax")
                    if self.text[self.pos] == 'n':
                        result.append('\n')
                    elif self.text[self.pos] == 't':
                        result.append('\t')
                    else:
                        result.append(self.text[self.pos])
                    self.pos += 1
                elif self.text[self.pos] == quote:
                    self.pos += 1
                    return ''.join(result)
                else:
                    result.append(self.text[self.pos])
                    self.pos += 1
            self.error("syntax")
        else:
            # Bare argument - read until comma, pipe, or end
            start = self.pos
            while self.pos < len(self.text) and self.text[self.pos] not in (',', '|'):
                self.pos += 1

            arg_text = self.text[start:self.pos].strip()

            # Interpret the argument
            if arg_text.isdigit():
                return int(arg_text)
            elif arg_text == 'true':
                return True
            elif arg_text == 'false':
                return False
            elif arg_text == 'none':
                return None
            else:
                return arg_text

    def parse_disjunct(self):
        """disjunct := conjunct ( "or" conjunct )*"""
        left = self.parse_conjunct()
        while True:
            self.skip_ws()
            if self.pos + 2 <= len(self.text) and self.text[self.pos:self.pos+2] == 'or':
                # Check it's not part of a longer identifier
                if self.pos + 2 < len(self.text) and (self.text[self.pos + 2].isalnum() or self.text[self.pos + 2] == '_'):
                    break
                self.pos += 2
                right = self.parse_conjunct()
                left = ('binop', 'or', left, right)
            else:
                break
        return left

    def parse_conjunct(self):
        """conjunct := negation ( "and" negation )*"""
        left = self.parse_negation()
        while True:
            self.skip_ws()
            if self.pos + 3 <= len(self.text) and self.text[self.pos:self.pos+3] == 'and':
                if self.pos + 3 < len(self.text) and (self.text[self.pos + 3].isalnum() or self.text[self.pos + 3] == '_'):
                    break
                self.pos += 3
                right = self.parse_negation()
                left = ('binop', 'and', left, right)
            else:
                break
        return left

    def parse_negation(self):
        """negation := "not" negation | comparison"""
        self.skip_ws()
        if self.pos + 3 <= len(self.text) and self.text[self.pos:self.pos+3] == 'not':
            if self.pos + 3 < len(self.text) and (self.text[self.pos + 3].isalnum() or self.text[self.pos + 3] == '_'):
                return self.parse_comparison()
            self.pos += 3
            expr = self.parse_negation()
            return ('unop', 'not', expr)
        return self.parse_comparison()

    def parse_comparison(self):
        """comparison := primary [ cmpop primary ]"""
        left = self.parse_primary()
        self.skip_ws()

        cmpop = None
        if self.pos + 2 <= len(self.text):
            two = self.text[self.pos:self.pos+2]
            if two in ('==', '!=', '<=', '>='):
                cmpop = two
                self.pos += 2

        if not cmpop and self.pos < len(self.text):
            if self.text[self.pos] in ('<', '>'):
                cmpop = self.text[self.pos]
                self.pos += 1

        if not cmpop and self.pos + 2 <= len(self.text) and self.text[self.pos:self.pos+2] == 'in':
            if self.pos + 2 < len(self.text) and (self.text[self.pos + 2].isalnum() or self.text[self.pos + 2] == '_'):
                return left
            cmpop = 'in'
            self.pos += 2

        if cmpop:
            right = self.parse_primary()

            # Check for second comparison operator (error)
            self.skip_ws()
            if self.pos + 2 <= len(self.text) and self.text[self.pos:self.pos+2] in ('==', '!=', '<=', '>='):
                self.error("syntax")
            if self.pos < len(self.text) and self.text[self.pos] in ('<', '>'):
                if not (self.pos + 1 < len(self.text) and self.text[self.pos:self.pos+2] in ('<=', '>=')):
                    self.error("syntax")
            if self.pos + 2 <= len(self.text) and self.text[self.pos:self.pos+2] == 'in':
                if self.pos + 2 >= len(self.text) or not (self.text[self.pos + 2].isalnum() or self.text[self.pos + 2] == '_'):
                    self.error("syntax")

            return ('binop', cmpop, left, right)

        return left

    def parse_primary(self):
        """primary := atom ( "." key | "[" primary "]" )*"""
        base = self.parse_atom()

        while True:
            self.skip_ws()
            if self.pos < len(self.text) and self.text[self.pos] == '.':
                self.pos += 1
                self.skip_ws()

                if self.pos >= len(self.text):
                    self.error("syntax")

                if self.text[self.pos].isdigit():
                    key_start = self.pos
                    while self.pos < len(self.text) and self.text[self.pos].isdigit():
                        self.pos += 1
                    key = self.text[key_start:self.pos]
                elif self.text[self.pos].isalpha() or self.text[self.pos] == '_':
                    key_start = self.pos
                    while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                        self.pos += 1
                    key = self.text[key_start:self.pos]
                else:
                    self.error("syntax")

                base = ('getattr', base, key)

            elif self.pos < len(self.text) and self.text[self.pos] == '[':
                self.pos += 1
                subscript = self.parse_primary()
                self.skip_ws()
                if self.pos >= len(self.text) or self.text[self.pos] != ']':
                    self.error("syntax")
                self.pos += 1
                base = ('getitem', base, subscript)
            else:
                break

        return base

    def parse_atom(self):
        """atom := INT | STRING | "true" | "false" | "none" | IDENT | "(" pipeline ")" """
        self.skip_ws()

        if self.pos >= len(self.text):
            self.error("syntax")

        # INT
        if self.text[self.pos].isdigit():
            start = self.pos
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            return ('literal', int(self.text[start:self.pos]))

        # STRING
        if self.text[self.pos] in ('"', "'"):
            quote = self.text[self.pos]
            self.pos += 1
            result = []
            while self.pos < len(self.text):
                if self.text[self.pos] == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text):
                        self.error("syntax")
                    if self.text[self.pos] == 'n':
                        result.append('\n')
                    elif self.text[self.pos] == 't':
                        result.append('\t')
                    else:
                        result.append(self.text[self.pos])
                    self.pos += 1
                elif self.text[self.pos] == quote:
                    self.pos += 1
                    return ('literal', ''.join(result))
                else:
                    result.append(self.text[self.pos])
                    self.pos += 1
            self.error("syntax")

        # Identifier or keyword
        if self.text[self.pos].isalpha() or self.text[self.pos] == '_':
            start = self.pos
            while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                self.pos += 1
            word = self.text[start:self.pos]

            if word == 'true':
                return ('literal', True)
            elif word == 'false':
                return ('literal', False)
            elif word == 'none':
                return ('literal', None)
            else:
                return ('name', word)

        # Parenthesized expression
        if self.text[self.pos] == '(':
            self.pos += 1
            expr = self.parse_pipeline()
            self.skip_ws()
            if self.pos >= len(self.text) or self.text[self.pos] != ')':
                self.error("syntax")
            self.pos += 1
            return expr

        self.error("syntax")


# ============================================================================
# PHASE 2: PARSING
# ============================================================================

class Node:
    pass


class TextNode(Node):
    def __init__(self, text):
        self.text = text


class InterpNode(Node):
    def __init__(self, expr, pos):
        self.expr = expr
        self.pos = pos


class IfNode(Node):
    def __init__(self, branches, pos):
        self.branches = branches  # [(expr or None, nodes)]
        self.pos = pos


class ForNode(Node):
    def __init__(self, var, expr, body, empty, pos):
        self.var = var
        self.expr = expr
        self.body = body
        self.empty = empty
        self.pos = pos


class SetNode(Node):
    def __init__(self, var, expr, pos):
        self.var = var
        self.expr = expr
        self.pos = pos


def parse(tokens):
    """Parse tokens into an AST."""
    parser = Parser(tokens)
    return parser.parse()


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def error(self, kind, pos):
        raise TemplateError(kind, pos)

    def parse(self):
        """Parse tokens into AST nodes."""
        nodes = []
        while self.current():
            token = self.current()
            if token.kind == 'text':
                nodes.append(TextNode(token.body))
                self.advance()
            elif token.kind == 'interp':
                nodes.append(self.parse_interp())
            elif token.kind == 'block':
                nodes.append(self.parse_block())
            else:
                self.advance()

        return nodes

    def parse_interp(self):
        """Parse {{ expr }}"""
        token = self.current()
        self.advance()

        body = token.body.strip()
        if not body:
            self.error("syntax", token.pos)

        expr = ExprParser(body, token.pos).parse()
        return InterpNode(expr, token.pos)

    def parse_block(self):
        """Parse {% block %}"""
        token = self.current()
        self.advance()

        body = token.body.strip()
        if not body:
            self.error("unknown_tag", token.pos)

        parts = body.split(None, 1)
        tag_name = parts[0]
        tag_rest = parts[1] if len(parts) > 1 else ""

        if tag_name == 'if':
            return self.parse_if(token.pos)
        elif tag_name == 'for':
            return self.parse_for(token.pos)
        elif tag_name == 'set':
            return self.parse_set(token.pos, tag_rest)
        elif tag_name in ('else', 'elif', 'endif', 'empty', 'endfor'):
            self.error("unexpected_tag", token.pos)
        else:
            self.error("unknown_tag", token.pos)

    def parse_if(self, if_pos):
        """Parse if/elif/else/endif block."""
        # We already consumed the 'if' token, need to back up
        self.pos -= 1
        token = self.current()
        self.advance()

        body = token.body.strip()
        parts = body.split(None, 1)
        tag_rest = parts[1] if len(parts) > 1 else ""

        if not tag_rest:
            self.error("syntax", token.pos)

        expr = ExprParser(tag_rest, token.pos).parse()
        branches = [(expr, [])]

        # Parse if body and elif/else
        while self.current():
            current_token = self.current()
            if current_token.kind == 'block':
                block_body = current_token.body.strip()
                block_parts = block_body.split(None, 1)
                block_tag = block_parts[0]
                block_rest = block_parts[1] if len(block_parts) > 1 else ""

                if block_tag == 'elif':
                    if not block_rest:
                        self.error("syntax", current_token.pos)
                    if branches[-1][0] is None:  # After else
                        self.error("syntax", current_token.pos)
                    self.advance()
                    expr = ExprParser(block_rest, current_token.pos).parse()
                    branches.append((expr, []))

                elif block_tag == 'else':
                    if block_rest:
                        self.error("syntax", current_token.pos)
                    if branches[-1][0] is None:  # Already have else
                        self.error("unexpected_tag", current_token.pos)
                    self.advance()
                    branches.append((None, []))

                elif block_tag == 'endif':
                    if block_rest:
                        self.error("syntax", current_token.pos)
                    self.advance()
                    return IfNode(branches, if_pos)

                else:
                    # Regular block in if body
                    branches[-1][1].append(self.parse_block())
            elif current_token.kind == 'interp':
                branches[-1][1].append(self.parse_interp())
            else:
                # Text
                if current_token.kind == 'text':
                    branches[-1][1].append(TextNode(current_token.body))
                self.advance()

        # If we get here, the if block was never closed
        self.error("unclosed_block", if_pos)

    def parse_for(self, for_pos):
        """Parse for/empty/endfor block."""
        self.pos -= 1
        token = self.current()
        self.advance()

        body = token.body.strip()
        parts = body.split(None, 1)
        tag_rest = parts[1] if len(parts) > 1 else ""

        if not tag_rest:
            self.error("syntax", token.pos)

        # Parse "var in expr"
        words = tag_rest.split()
        if len(words) < 3 or words[1] != 'in':
            self.error("syntax", token.pos)

        var_name = words[0]
        if not var_name.isidentifier() or var_name in ('true', 'false', 'none', 'not', 'and', 'or', 'in'):
            self.error("syntax", token.pos)

        expr_text = ' '.join(words[2:])
        expr = ExprParser(expr_text, token.pos).parse()

        body_nodes = []
        empty_nodes = []

        while self.current():
            current_token = self.current()
            if current_token.kind == 'block':
                block_body = current_token.body.strip()
                block_parts = block_body.split(None, 1)
                block_tag = block_parts[0]
                block_rest = block_parts[1] if len(block_parts) > 1 else ""

                if block_tag == 'empty':
                    if block_rest:
                        self.error("syntax", current_token.pos)
                    if empty_nodes:
                        self.error("unexpected_tag", current_token.pos)
                    self.advance()

                    # Parse empty body
                    while self.current():
                        token2 = self.current()
                        if token2.kind == 'block':
                            body2 = token2.body.strip()
                            parts2 = body2.split(None, 1)
                            tag2 = parts2[0]
                            rest2 = parts2[1] if len(parts2) > 1 else ""

                            if tag2 == 'endfor':
                                if rest2:
                                    self.error("syntax", token2.pos)
                                self.advance()
                                return ForNode(var_name, expr, body_nodes, empty_nodes, for_pos)
                            else:
                                empty_nodes.append(self.parse_block())
                        elif token2.kind == 'interp':
                            empty_nodes.append(self.parse_interp())
                        else:
                            if token2.kind == 'text':
                                empty_nodes.append(TextNode(token2.body))
                            self.advance()

                elif block_tag == 'endfor':
                    if block_rest:
                        self.error("syntax", current_token.pos)
                    self.advance()
                    return ForNode(var_name, expr, body_nodes, empty_nodes, for_pos)

                else:
                    body_nodes.append(self.parse_block())

            elif current_token.kind == 'interp':
                body_nodes.append(self.parse_interp())
            else:
                if current_token.kind == 'text':
                    body_nodes.append(TextNode(current_token.body))
                self.advance()

        self.error("unclosed_block", for_pos)

    def parse_set(self, set_pos, tag_rest):
        """Parse {% set var = expr %}"""
        if not tag_rest:
            self.error("syntax", set_pos)

        # Find the = sign
        parts = tag_rest.split('=', 1)
        if len(parts) != 2:
            self.error("syntax", set_pos)

        var_part = parts[0].strip()
        expr_part = parts[1].strip()

        if not var_part or not expr_part:
            self.error("syntax", set_pos)

        if not var_part.isidentifier():
            self.error("syntax", set_pos)

        if var_part in ('true', 'false', 'none', 'not', 'and', 'or', 'in'):
            self.error("syntax", set_pos)

        # Check not ==
        eq_idx = tag_rest.index('=')
        if eq_idx > 0 and tag_rest[eq_idx - 1] == '=':
            self.error("syntax", set_pos)
        if eq_idx + 1 < len(tag_rest) and tag_rest[eq_idx + 1] == '=':
            self.error("syntax", set_pos)

        expr = ExprParser(expr_part, set_pos).parse()
        return SetNode(var_part, expr, set_pos)


# ============================================================================
# PHASE 3: RENDERING
# ============================================================================

def render(source, context):
    """Main render function."""
    # Phase 1: Lex
    tokens = lex(source)

    # Apply whitespace control
    tokens = apply_whitespace_control(tokens)

    # Remove comments
    tokens = remove_comments(tokens)

    # Phase 2: Parse
    ast = parse(tokens)

    # Phase 3: Render
    renderer = Renderer(context)
    return renderer.render_nodes(ast)


class Renderer:
    def __init__(self, context):
        self.context = context
        self.scopes = [dict(context)]

    def render_nodes(self, nodes):
        """Render a list of nodes."""
        result = []
        for node in nodes:
            result.append(self.render_node(node))
        return ''.join(result)

    def render_node(self, node):
        """Render a single node."""
        if isinstance(node, TextNode):
            return node.text

        elif isinstance(node, InterpNode):
            value, safe = self.eval_expr(node.expr)
            text = self.value_to_text(value)
            if not safe:
                text = self.escape(text)
            return text

        elif isinstance(node, IfNode):
            for cond_expr, body_nodes in node.branches:
                if cond_expr is None:
                    # else branch
                    return self.render_nodes(body_nodes)

                cond_val, _ = self.eval_expr(cond_expr)
                if self.is_truthy(cond_val):
                    return self.render_nodes(body_nodes)

            return ''

        elif isinstance(node, ForNode):
            return self.render_for(node)

        elif isinstance(node, SetNode):
            value, safe = self.eval_expr(node.expr)
            self.scopes[-1][node.var] = (value, safe)
            return ''

        return ''

    def render_for(self, node):
        """Render a for loop."""
        seq_val, _ = self.eval_expr(node.expr)
        sequence = self.get_sequence(seq_val, node.pos)

        if not sequence:
            return self.render_nodes(node.empty)

        # Push a new scope
        self.scopes.append({})
        result = []

        for i, item in enumerate(sequence):
            self.scopes[-1][node.var] = (item, False)
            loop_info = {
                'index': i + 1,
                'index0': i,
                'first': i == 0,
                'last': i == len(sequence) - 1,
                'length': len(sequence),
            }
            self.scopes[-1]['loop'] = (loop_info, False)
            result.append(self.render_nodes(node.body))

        self.scopes.pop()
        return ''.join(result)

    def get_sequence(self, value, tag_pos):
        """Convert a value to a sequence for iteration."""
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return list(value)
        elif isinstance(value, dict):
            return list(value.keys())
        elif value is None or value is ...:
            return []
        else:
            raise TemplateError("not_iterable", tag_pos)

    def eval_expr(self, expr):
        """Evaluate an expression. Returns (value, safe)."""
        if not isinstance(expr, tuple):
            return expr, False

        op = expr[0]

        if op == 'literal':
            return expr[1], False

        elif op == 'name':
            var_name = expr[1]
            for scope in reversed(self.scopes):
                if var_name in scope:
                    val = scope[var_name]
                    if isinstance(val, tuple) and len(val) == 2:
                        return val
                    return val, False
            return ..., False

        elif op == 'getattr':
            base_val, _ = self.eval_expr(expr[1])
            key = expr[2]
            return self.lookup(base_val, key), False

        elif op == 'getitem':
            base_val, _ = self.eval_expr(expr[1])
            subscript_val, _ = self.eval_expr(expr[2])
            return self.lookup(base_val, subscript_val), False

        elif op == 'binop':
            op_name = expr[1]

            if op_name == 'or':
                left, _ = self.eval_expr(expr[2])
                if self.is_truthy(left):
                    return left, False
                right, _ = self.eval_expr(expr[3])
                return right, False

            elif op_name == 'and':
                left, _ = self.eval_expr(expr[2])
                if not self.is_truthy(left):
                    return left, False
                right, _ = self.eval_expr(expr[3])
                return right, False

            left, _ = self.eval_expr(expr[2])
            right, _ = self.eval_expr(expr[3])

            if op_name == '==':
                return self.eq(left, right), False
            elif op_name == '!=':
                return not self.eq(left, right), False
            elif op_name == '<':
                return self.lt(left, right), False
            elif op_name == '<=':
                return self.le(left, right), False
            elif op_name == '>':
                return self.gt(left, right), False
            elif op_name == '>=':
                return self.ge(left, right), False
            elif op_name == 'in':
                return self.contains(left, right), False

        elif op == 'unop':
            op_name = expr[1]
            operand, _ = self.eval_expr(expr[2])
            if op_name == 'not':
                return not self.is_truthy(operand), False

        elif op == 'filter':
            base_val, safe = self.eval_expr(expr[1])
            filter_name = expr[2]
            filter_args = expr[3]
            return self.apply_filter(base_val, safe, filter_name, filter_args)

        return ..., False

    def apply_filter(self, value, safe, name, args):
        """Apply a filter."""
        # Filter arity map
        arity_map = {
            'upper': 0, 'lower': 0, 'trim': 0, 'length': 0, 'first': 0,
            'safe': 0, 'escape': 0, 'default': 1, 'join': 1, 'replace': 2,
            'slice': 2
        }

        if name not in arity_map:
            raise TemplateError("unknown_filter", 0)

        expected_arity = arity_map[name]
        if len(args) != expected_arity:
            raise TemplateError("filter_args", 0)

        if name == 'upper':
            text = self.value_to_text(value)
            return text.upper(), safe

        elif name == 'lower':
            text = self.value_to_text(value)
            return text.lower(), safe

        elif name == 'trim':
            text = self.value_to_text(value)
            return text.strip(' \t\r\n\v\f'), safe

        elif name == 'length':
            if value is ... or value is None or isinstance(value, bool):
                return 0, safe
            elif isinstance(value, int):
                return len(str(value)), safe
            elif isinstance(value, (str, list, dict)):
                return len(value), safe
            else:
                return 0, safe

        elif name == 'first':
            if value is ... or value is None:
                return ..., safe
            elif isinstance(value, str):
                return value[0] if value else ..., safe
            elif isinstance(value, list):
                return value[0] if value else ..., safe
            elif isinstance(value, dict):
                keys = list(value.keys())
                return keys[0] if keys else ..., safe
            else:
                return ..., safe

        elif name == 'safe':
            return value, True

        elif name == 'escape':
            text = self.value_to_text(value)
            return self.escape(text), True

        elif name == 'default':
            if len(args) != 1:
                raise TemplateError("filter_args", 0)
            if self.is_falsy(value):
                return args[0], False
            else:
                return value, safe

        elif name == 'join':
            if len(args) != 1:
                raise TemplateError("filter_args", 0)
            sep = self.value_to_text(args[0])

            if value is ... or value is None:
                return '', safe
            elif isinstance(value, list):
                return sep.join(self.value_to_text(v) for v in value), safe
            elif isinstance(value, str):
                return sep.join(value), safe
            elif isinstance(value, dict):
                return sep.join(str(k) for k in value.keys()), safe
            elif isinstance(value, (int, bool)):
                return self.value_to_text(value), safe
            else:
                return '', safe

        elif name == 'replace':
            if len(args) != 2:
                raise TemplateError("filter_args", 0)
            search = self.value_to_text(args[0])
            repl = self.value_to_text(args[1])
            text = self.value_to_text(value)
            if search == '':
                return text, safe
            return text.replace(search, repl), safe

        elif name == 'slice':
            start_arg = args[0]
            len_arg = args[1]

            if isinstance(start_arg, int):
                start = start_arg
            elif isinstance(start_arg, str) and start_arg.isdigit():
                start = int(start_arg)
            else:
                return value, safe

            if isinstance(len_arg, int):
                length = len_arg
            elif isinstance(len_arg, str) and len_arg.isdigit():
                length = int(len_arg)
            else:
                return value, safe

            if start < 0 or length < 0:
                return value, safe

            if isinstance(value, str):
                return value[start:start + length], safe
            elif isinstance(value, list):
                return value[start:start + length], safe
            else:
                text = self.value_to_text(value)
                return text[start:start + length], safe

    def lookup(self, base, key):
        """Look up a key in a value."""
        if base is ... or base is None:
            return ...

        if isinstance(base, dict):
            if key in base:
                val = base[key]
                if isinstance(val, tuple) and len(val) == 2:
                    return val[0]
                return val

        if isinstance(base, (list, str)):
            idx = None
            if isinstance(key, int):
                idx = key
            elif isinstance(key, str) and key.isdigit():
                idx = int(key)

            if idx is not None:
                if 0 <= idx < len(base):
                    return base[idx]
                return ...

        # Pseudo-keys
        if key == 'size':
            if isinstance(base, (str, list, dict)):
                return len(base)
        elif key == 'keys':
            if isinstance(base, dict):
                return list(base.keys())
        elif key == 'type':
            if base is ...:
                return ...
            elif base is None:
                return 'none'
            elif isinstance(base, bool):
                return 'bool'
            elif isinstance(base, int):
                return 'number'
            elif isinstance(base, str):
                return 'string'
            elif isinstance(base, list):
                return 'list'
            elif isinstance(base, dict):
                return 'map'

        return ...

    def eq(self, left, right):
        """Equality comparison."""
        if type(left) != type(right):
            return False
        if left is ... and right is ...:
            return True
        if left is None and right is None:
            return True
        if isinstance(left, (int, str, bool)):
            return left == right
        if isinstance(left, list):
            if len(left) != len(right):
                return False
            return all(self.eq(l, r) for l, r in zip(left, right))
        if isinstance(left, dict):
            if len(left) != len(right):
                return False
            for k in left:
                if k not in right or not self.eq(left[k], right[k]):
                    return False
            return True
        return False

    def lt(self, left, right):
        if isinstance(left, int) and isinstance(right, int):
            return left < right
        elif isinstance(left, str) and isinstance(right, str):
            return left < right
        else:
            raise TemplateError("bad_operand", 0)

    def le(self, left, right):
        if isinstance(left, int) and isinstance(right, int):
            return left <= right
        elif isinstance(left, str) and isinstance(right, str):
            return left <= right
        else:
            raise TemplateError("bad_operand", 0)

    def gt(self, left, right):
        if isinstance(left, int) and isinstance(right, int):
            return left > right
        elif isinstance(left, str) and isinstance(right, str):
            return left > right
        else:
            raise TemplateError("bad_operand", 0)

    def ge(self, left, right):
        if isinstance(left, int) and isinstance(right, int):
            return left >= right
        elif isinstance(left, str) and isinstance(right, str):
            return left >= right
        else:
            raise TemplateError("bad_operand", 0)

    def contains(self, left, right):
        """Check if left is in right."""
        if isinstance(right, str):
            return isinstance(left, str) and left in right
        elif isinstance(right, list):
            for item in right:
                if self.eq(left, item):
                    return True
            return False
        elif isinstance(right, dict):
            return isinstance(left, str) and left in right
        else:
            return False

    def value_to_text(self, value):
        """Convert a value to its text representation."""
        if value is ...:
            return ''
        elif value is None:
            return ''
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, list):
            items = [self.value_to_text(v) for v in value]
            return '[' + ', '.join(items) + ']'
        elif isinstance(value, dict):
            pairs = []
            for k, v in value.items():
                k_text = self.value_to_text(k)
                v_text = self.value_to_text(v)
                pairs.append(f'{k_text}: {v_text}')
            return '{' + ', '.join(pairs) + '}'
        else:
            return ''

    def escape(self, text):
        """HTML escape a string."""
        result = []
        for char in text:
            if char == '&':
                result.append('&amp;')
            elif char == '<':
                result.append('&lt;')
            elif char == '>':
                result.append('&gt;')
            elif char == '"':
                result.append('&#34;')
            elif char == "'":
                result.append('&#39;')
            else:
                result.append(char)
        return ''.join(result)

    def is_truthy(self, value):
        """Check if a value is truthy."""
        if value is ... or value is None or value is False:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value not in ('', '0', 'false')
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True

    def is_falsy(self, value):
        """Check if a value is falsy."""
        return not self.is_truthy(value)
