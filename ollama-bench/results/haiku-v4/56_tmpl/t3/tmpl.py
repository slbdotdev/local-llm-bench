"""Text template engine."""


class TemplateError(Exception):
    """Template processing error."""
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"{kind} at {pos}")


def render(source, context):
    """Render a template string with the given context."""
    # Phase 1: Lexing
    tokens = _lex(source)
    # Phase 2: Parsing
    ast = _parse(tokens)
    # Phase 3: Rendering
    return _render(ast, context)


# ============================================================================
# PHASE 1: LEXING
# ============================================================================

WHITESPACE = ' \t\r\n\v\f'


class Token:
    def __init__(self, type, body=None, pos=0, left_trim=False, right_trim=False):
        self.type = type  # 'text', 'interp', 'block'
        self.body = body
        self.pos = pos
        self.left_trim = left_trim
        self.right_trim = right_trim


def _lex(source):
    """Tokenize template source into tags and text."""
    tokens = []
    i = 0

    while i < len(source):
        if i < len(source) - 1 and source[i] == '{':
            next_ch = source[i + 1]
            if next_ch in '{%#':
                tag_start = i
                if next_ch == '{':
                    opener, closer, tag_type = '{{', '}}', 'interp'
                elif next_ch == '%':
                    opener, closer, tag_type = '{%', '%}', 'block'
                else:
                    opener, closer, tag_type = '{#', '#}', 'comment'

                i += 2

                # Check left trim
                left_trim = False
                if i < len(source) and source[i] == '-':
                    left_trim = True
                    i += 1

                # Find closer
                closer_idx = source.find(closer, i)
                if closer_idx == -1:
                    raise TemplateError('unclosed_tag', tag_start)

                body = source[i:closer_idx]

                # Check right trim
                right_trim = False
                if body and body[-1] == '-':
                    right_trim = True
                    body = body[:-1]

                if tag_type != 'comment':
                    tokens.append(Token(tag_type, body, tag_start, left_trim, right_trim))

                i = closer_idx + len(closer)
            else:
                # Just a {
                text_start = i
                i += 1
                while i < len(source) and not (i < len(source) - 1 and source[i] == '{' and source[i+1] in '{%#'):
                    i += 1
                tokens.append(Token('text', source[text_start:i]))
        else:
            # Literal text
            text_start = i
            i += 1
            while i < len(source) and not (i < len(source) - 1 and source[i] == '{' and source[i+1] in '{%#'):
                i += 1
            tokens.append(Token('text', source[text_start:i]))

    # Apply whitespace trimming
    trimmed = []
    for idx, token in enumerate(tokens):
        if token.type == 'text':
            text = token.body

            # Trim leading whitespace if previous tag has right marker
            if idx > 0 and trimmed and trimmed[-1].type in ('interp', 'block'):
                if trimmed[-1].right_trim:
                    text = text.lstrip(WHITESPACE)

            # Trim trailing whitespace if next tag has left marker
            if idx < len(tokens) - 1:
                next_token = tokens[idx + 1]
                if next_token.type in ('interp', 'block') and next_token.left_trim:
                    text = text.rstrip(WHITESPACE)

            trimmed.append(Token('text', text))
        elif token.type in ('interp', 'block'):
            trimmed.append(token)

    return trimmed


# ============================================================================
# PHASE 2: PARSING
# ============================================================================

def _parse(tokens):
    """Parse tokens into AST."""
    parser = Parser(tokens)
    ast = []
    while parser.pos < len(parser.tokens):
        ast.append(parser.parse_top_level())
    if parser.block_stack:
        raise TemplateError('unclosed_block', parser.block_stack[-1]['pos'])
    return ast


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.block_stack = []

    def parse_top_level(self):
        """Parse a top-level element."""
        if self.pos >= len(self.tokens):
            return None

        token = self.tokens[self.pos]

        if token.type == 'text':
            self.pos += 1
            return ('text', token.body)
        elif token.type == 'interp':
            self.pos += 1
            return self.parse_interp(token)
        elif token.type == 'block':
            self.pos += 1
            return self.parse_block(token)

        self.pos += 1
        return None

    def parse_interp(self, token):
        """Parse {{ ... }}"""
        body = token.body.strip()
        if not body:
            raise TemplateError('syntax', token.pos)

        # Parse pipeline (expression with filters)
        expr, remaining = parse_pipeline(body, token.pos)
        if remaining.strip():
            raise TemplateError('syntax', token.pos)

        return ('interp', expr)

    def parse_block(self, token):
        """Parse {% ... %}"""
        body = token.body.strip()
        if not body:
            raise TemplateError('unknown_tag', token.pos)

        parts = body.split(None, 1)
        tag_name = parts[0]
        tag_rest = parts[1] if len(parts) > 1 else ''

        if tag_name == 'if':
            return self.parse_if(tag_rest, token.pos)
        elif tag_name == 'for':
            return self.parse_for(tag_rest, token.pos)
        elif tag_name == 'set':
            return self.parse_set(tag_rest, token.pos)
        elif tag_name in ('else', 'elif', 'endif', 'empty', 'endfor'):
            raise TemplateError('unexpected_tag', token.pos)
        else:
            raise TemplateError('unknown_tag', token.pos)

    def parse_if(self, condition_str, pos):
        """Parse if/elif/else/endif block."""
        if not condition_str.strip():
            raise TemplateError('syntax', pos)

        self.block_stack.append({'type': 'if', 'pos': pos})

        # Parse condition (no filters allowed in conditions)
        cond, remaining = parse_condition(condition_str, pos)
        if remaining.strip():
            raise TemplateError('syntax', pos)

        # Parse body
        body = self.parse_body()

        self.block_stack.pop()

        # Check for elif/else
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'block':
            peek = self.tokens[self.pos]
            peek_body = peek.body.strip()
            if peek_body:
                peek_parts = peek_body.split(None, 1)
                next_name = peek_parts[0]
                next_rest = peek_parts[1] if len(peek_parts) > 1 else ''

                if next_name == 'elif':
                    if not next_rest.strip():
                        raise TemplateError('syntax', peek.pos)
                    self.pos += 1
                    elif_node = self.parse_if(next_rest, peek.pos)
                    return ('if', cond, body, elif_node)
                elif next_name == 'else':
                    if next_rest.strip():
                        raise TemplateError('syntax', peek.pos)
                    self.pos += 1
                    else_body = self.parse_body()

                    # After else body, we must see endif
                    if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'block':
                        peek2 = self.tokens[self.pos]
                        peek2_body = peek2.body.strip()
                        if peek2_body:
                            peek2_parts = peek2_body.split(None, 1)
                            if peek2_parts[0] == 'endif':
                                if len(peek2_parts) > 1 and peek2_parts[1].strip():
                                    raise TemplateError('syntax', peek2.pos)
                                self.pos += 1
                                return ('if', cond, body, else_body)

                    raise TemplateError('unclosed_block', pos)
                elif next_name == 'endif':
                    if next_rest.strip():
                        raise TemplateError('syntax', peek.pos)
                    self.pos += 1
                    return ('if', cond, body)

        raise TemplateError('unclosed_block', pos)

    def parse_for(self, expr_str, pos):
        """Parse for/empty/endfor block."""
        if not expr_str.strip():
            raise TemplateError('syntax', pos)

        self.block_stack.append({'type': 'for', 'pos': pos})

        # Parse: NAME in EXPR
        parts = expr_str.split()
        if len(parts) < 3 or parts[1] != 'in':
            raise TemplateError('syntax', pos)

        var_name = parts[0]
        if not is_identifier(var_name):
            raise TemplateError('syntax', pos)

        expr_text = ' '.join(parts[2:])
        expr, remaining = parse_pipeline(expr_text, pos)
        if remaining.strip():
            raise TemplateError('syntax', pos)

        # Parse body
        body = self.parse_body()

        # Check for empty/endfor
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'block':
            peek = self.tokens[self.pos]
            peek_body = peek.body.strip()
            if peek_body:
                peek_parts = peek_body.split(None, 1)
                next_name = peek_parts[0]
                next_rest = peek_parts[1] if len(peek_parts) > 1 else ''

                if next_name == 'empty':
                    if next_rest.strip():
                        raise TemplateError('syntax', peek.pos)
                    self.pos += 1
                    empty_body = self.parse_body()

                    # Expect endfor
                    if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'block':
                        peek2 = self.tokens[self.pos]
                        peek2_body = peek2.body.strip()
                        if peek2_body:
                            peek2_parts = peek2_body.split(None, 1)
                            if peek2_parts[0] == 'endfor':
                                if len(peek2_parts) > 1 and peek2_parts[1].strip():
                                    raise TemplateError('syntax', peek2.pos)
                                self.pos += 1
                                self.block_stack.pop()
                                return ('for', var_name, expr, body, empty_body)

                    raise TemplateError('unclosed_block', pos)

                elif next_name == 'endfor':
                    if next_rest.strip():
                        raise TemplateError('syntax', peek.pos)
                    self.pos += 1
                    self.block_stack.pop()
                    return ('for', var_name, expr, body, [])

        raise TemplateError('unclosed_block', pos)

    def parse_set(self, rest_str, pos):
        """Parse {% set NAME = EXPR %}"""
        if not rest_str.strip():
            raise TemplateError('syntax', pos)

        # Find = (not ==)
        eq_idx = rest_str.find('=')
        if eq_idx == -1:
            raise TemplateError('syntax', pos)

        # Make sure it's not == or part of ==
        if eq_idx > 0 and rest_str[eq_idx - 1] == '=':
            raise TemplateError('syntax', pos)
        if eq_idx < len(rest_str) - 1 and rest_str[eq_idx + 1] == '=':
            raise TemplateError('syntax', pos)

        var_name = rest_str[:eq_idx].strip()
        expr_text = rest_str[eq_idx + 1:].strip()

        if not var_name or not expr_text:
            raise TemplateError('syntax', pos)
        if not is_identifier(var_name):
            raise TemplateError('syntax', pos)

        expr, remaining = parse_pipeline(expr_text, pos)
        if remaining.strip():
            raise TemplateError('syntax', pos)

        return ('set', var_name, expr)

    def parse_body(self):
        """Parse body until we hit a block-closing tag."""
        body = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.type == 'text':
                body.append(('text', token.body))
                self.pos += 1
            elif token.type == 'interp':
                body.append(self.parse_top_level())
            elif token.type == 'block':
                block_body = token.body.strip()
                if block_body:
                    parts = block_body.split(None, 1)
                    tag_name = parts[0]
                    tag_rest = parts[1] if len(parts) > 1 else ''

                    if tag_name in ('elif', 'else', 'endif', 'empty', 'endfor'):
                        # This closes the current block
                        return body
                    elif tag_name in ('if', 'for', 'set'):
                        # Nested block
                        self.pos += 1
                        if tag_name == 'if':
                            body.append(self.parse_if(tag_rest, token.pos))
                        elif tag_name == 'for':
                            body.append(self.parse_for(tag_rest, token.pos))
                        elif tag_name == 'set':
                            body.append(self.parse_set(tag_rest, token.pos))
                    else:
                        raise TemplateError('unknown_tag', token.pos)
                else:
                    raise TemplateError('unknown_tag', token.pos)
            else:
                self.pos += 1

        return body


def is_identifier(s):
    """Check if string is a valid identifier."""
    if not s:
        return False
    if not (s[0].isalpha() or s[0] == '_'):
        return False
    for c in s[1:]:
        if not (c.isalnum() or c == '_'):
            return False
    return True


# Expression parsing
def parse_pipeline(s, pos):
    """Parse: disjunction ( "|" filter )*"""
    expr, rest = parse_disjunction(s, pos)

    filters = []
    while rest.strip():
        if rest.strip().startswith('|'):
            rest = rest.strip()[1:].strip()
            filter_obj, rest = parse_single_filter(rest, pos)
            filters.append(filter_obj)
        else:
            break

    if filters:
        return ('pipeline', expr, filters), rest
    return expr, rest


def parse_condition(s, pos):
    """Parse condition (no pipes allowed)."""
    expr, rest = parse_disjunction(s, pos)
    # Check that no pipes follow
    if rest.strip().startswith('|'):
        raise TemplateError('syntax', pos)
    return expr, rest


def parse_disjunction(s, pos):
    """Parse: conjunct ( "or" conjunct )*"""
    left, rest = parse_conjunct(s, pos)
    while rest.strip():
        rest = rest.strip()
        if word_starts(rest, 'or'):
            rest = rest[2:].strip()
            right, rest = parse_conjunct(rest, pos)
            left = ('or', left, right)
        else:
            break
    return left, rest


def parse_conjunct(s, pos):
    """Parse: negation ( "and" negation )*"""
    left, rest = parse_negation(s, pos)
    while rest.strip():
        rest = rest.strip()
        if word_starts(rest, 'and'):
            rest = rest[3:].strip()
            right, rest = parse_negation(rest, pos)
            left = ('and', left, right)
        else:
            break
    return left, rest


def parse_negation(s, pos):
    """Parse: "not" negation | comparison"""
    s = s.strip()
    if word_starts(s, 'not'):
        rest = s[3:].strip()
        expr, rest = parse_negation(rest, pos)
        return ('not', expr), rest
    return parse_comparison(s, pos)


def parse_comparison(s, pos):
    """Parse: primary [ cmpop primary ]"""
    left, rest = parse_postfix(s, pos)
    rest_stripped = rest.strip()

    if not rest_stripped:
        return left, rest

    # Try each comparison operator
    for op in ['==', '!=', '<=', '>=', '<', '>', 'in']:
        if op in ('in',):
            if not word_starts(rest_stripped, op):
                continue
            op_len = 2
        else:
            if not rest_stripped.startswith(op):
                continue
            op_len = len(op)

        rest = rest_stripped[op_len:].strip()
        right, rest = parse_postfix(rest, pos)

        # Check no second operator
        rest_stripped2 = rest.strip()
        for op2 in ['==', '!=', '<=', '>=', '<', '>', 'in']:
            if op2 in ('in',):
                if word_starts(rest_stripped2, op2):
                    raise TemplateError('syntax', pos)
            else:
                if rest_stripped2.startswith(op2):
                    raise TemplateError('syntax', pos)

        return (op, left, right), rest

    return left, rest


def parse_postfix(s, pos):
    """Parse: atom ( "." key | "[" primary "]" )*"""
    expr, rest = parse_atom(s, pos)

    while rest.strip():
        rest_stripped = rest.strip()
        if rest_stripped.startswith('.'):
            rest = rest_stripped[1:].strip()
            key, rest = parse_key(rest, pos)
            expr = ('.', expr, key)
        elif rest_stripped.startswith('['):
            rest = rest_stripped[1:].strip()
            idx, rest = parse_postfix(rest, pos)
            rest = rest.strip()
            if not rest.startswith(']'):
                raise TemplateError('syntax', pos)
            rest = rest[1:]
            expr = ('[]', expr, idx)
        else:
            break

    return expr, rest


def parse_key(s, pos):
    """Parse key (identifier or digits)."""
    s = s.strip()
    if not s:
        raise TemplateError('syntax', pos)

    if s[0].isdigit():
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        return ('int', int(s[:i])), s[i:]
    else:
        i = 0
        while i < len(s) and (s[i].isalnum() or s[i] == '_'):
            i += 1
        return ('var', s[:i]), s[i:]


def parse_atom(s, pos):
    """Parse: INT | STRING | true | false | none | IDENT"""
    s = s.strip()
    if not s:
        raise TemplateError('syntax', pos)

    # INT
    if s[0].isdigit():
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        return ('int', int(s[:i])), s[i:]

    # STRING
    if s[0] in ('"', "'"):
        return parse_string(s, pos)

    # Keywords
    if word_starts(s, 'true'):
        return ('bool', True), s[4:]
    if word_starts(s, 'false'):
        return ('bool', False), s[5:]
    if word_starts(s, 'none'):
        return ('none',), s[4:]

    # IDENT
    if s[0].isalpha() or s[0] == '_':
        i = 0
        while i < len(s) and (s[i].isalnum() or s[i] == '_'):
            i += 1
        ident = s[:i]

        # Reject keywords as identifiers
        if ident in ('and', 'or', 'not', 'in', 'true', 'false', 'none'):
            raise TemplateError('syntax', pos)

        return ('var', ident), s[i:]

    raise TemplateError('syntax', pos)


def parse_string(s, pos):
    """Parse a string literal."""
    quote = s[0]
    i = 1
    chars = []

    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_ch = s[i + 1]
            if next_ch == 'n':
                chars.append('\n')
            elif next_ch == 't':
                chars.append('\t')
            else:
                chars.append(next_ch)
            i += 2
        elif s[i] == quote:
            return ('str', ''.join(chars)), s[i + 1:]
        else:
            chars.append(s[i])
            i += 1

    raise TemplateError('syntax', pos)


def parse_single_filter(s, pos):
    """Parse a single filter: name [ ":args" ]"""
    s = s.strip()

    # Parse filter name
    if not s or s[0].isdigit():
        raise TemplateError('syntax', pos)

    i = 0
    while i < len(s) and (s[i].isalnum() or s[i] == '_'):
        i += 1

    if i == 0:
        raise TemplateError('syntax', pos)

    filter_name = s[:i]
    rest = s[i:].strip()

    # Check filter exists
    filter_table = {
        'upper': 0, 'lower': 0, 'trim': 0, 'length': 0, 'first': 0,
        'safe': 0, 'escape': 0, 'default': 1, 'join': 1, 'replace': 2, 'slice': 2
    }

    if filter_name not in filter_table:
        raise TemplateError('unknown_filter', pos)

    args = []
    if rest and rest[0] == ':':
        rest = rest[1:]
        args, rest = parse_filter_args(rest, pos)

    if len(args) != filter_table[filter_name]:
        raise TemplateError('filter_args', pos)

    return ('filter', filter_name, args), rest


def parse_filter_args(s, pos):
    """Parse filter arguments."""
    args = []

    while s:
        s = s.strip()
        if not s:
            break

        if s[0] in ('"', "'"):
            # String argument
            arg, s = parse_string(s, pos)
            args.append(arg)
            s = s.strip()
        else:
            # Non-string argument: maximal run to , | or end
            i = 0
            while i < len(s) and s[i] not in (',', '|'):
                i += 1

            arg_text = s[:i].strip()
            s = s[i:]

            if not arg_text:
                args.append(('str', ''))
            elif arg_text == 'true':
                args.append(('bool', True))
            elif arg_text == 'false':
                args.append(('bool', False))
            elif arg_text == 'none':
                args.append(('none',))
            elif arg_text.isdigit():
                args.append(('int', int(arg_text)))
            else:
                args.append(('str', arg_text))

        # Expect , or | or end
        s = s.strip()
        if s and s[0] == ',':
            s = s[1:]
        elif s and s[0] != '|':
            raise TemplateError('syntax', pos)

    return args, s


def word_starts(s, word):
    """Check if string starts with word as a complete word."""
    if not s.startswith(word):
        return False
    if len(s) == len(word):
        return True
    next_ch = s[len(word)]
    return not (next_ch.isalnum() or next_ch == '_')


# ============================================================================
# PHASE 3: RENDERING
# ============================================================================

def _render(ast, context):
    """Render AST with context."""
    renderer = Renderer(context)
    return renderer.render_body(ast)


class Renderer:
    def __init__(self, context):
        self.context = context if isinstance(context, dict) else {}
        self.scopes = [self.context.copy()]

    def render_body(self, body):
        """Render a list of nodes."""
        parts = []
        for node in body:
            if node:
                parts.append(self.render_node(node))
        return ''.join(parts)

    def render_node(self, node):
        """Render a single AST node."""
        if node[0] == 'text':
            return node[1]
        elif node[0] == 'interp':
            value = self.eval_expr(node[1])
            text = self.value_to_text(value)
            if not self.is_safe(value):
                text = self.html_escape(text)
            return text
        elif node[0] == 'if':
            return self.render_if(node)
        elif node[0] == 'for':
            return self.render_for(node)
        elif node[0] == 'set':
            return self.render_set(node)
        return ''

    def render_if(self, node):
        """Render if/elif/else."""
        cond = self.eval_expr(node[1])
        body = node[2]

        if self.is_truthy(cond):
            return self.render_body(body)

        # Check elif/else
        if len(node) > 3:
            next_node = node[3]
            if isinstance(next_node, tuple) and next_node[0] == 'if':
                # elif
                return self.render_if(next_node)
            elif isinstance(next_node, list):
                # else
                return self.render_body(next_node)

        return ''

    def render_for(self, node):
        """Render for loop."""
        var_name = node[1]
        expr = node[2]
        body = node[3]
        empty_body = node[4] if len(node) > 4 else []

        value = self.eval_expr(expr)
        sequence = self.to_sequence(value)

        if not sequence:
            return self.render_body(empty_body)

        # New scope
        self.scopes.append({})

        parts = []
        for idx, item in enumerate(sequence):
            self.scopes[-1][var_name] = item
            self.scopes[-1]['loop'] = {
                'index': idx + 1,
                'index0': idx,
                'first': idx == 0,
                'last': idx == len(sequence) - 1,
                'length': len(sequence),
            }
            parts.append(self.render_body(body))

        self.scopes.pop()
        return ''.join(parts)

    def render_set(self, node):
        """Render set statement."""
        var_name = node[1]
        expr = node[2]
        value = self.eval_expr(expr)
        self.scopes[-1][var_name] = value
        return ''

    def eval_expr(self, expr):
        """Evaluate an expression."""
        if isinstance(expr, tuple):
            if expr[0] == 'int':
                return expr[1]
            elif expr[0] == 'str':
                return expr[1]
            elif expr[0] == 'bool':
                return expr[1]
            elif expr[0] == 'none':
                return None
            elif expr[0] == 'var':
                return self.lookup(expr[1])
            elif expr[0] == '.':
                base = self.eval_expr(expr[1])
                # expr[2] is always a key tuple like ('var', 'name') or ('int', 0)
                if isinstance(expr[2], tuple):
                    if expr[2][0] == 'var':
                        key = expr[2][1]
                    elif expr[2][0] == 'int':
                        key = expr[2][1]
                    else:
                        key = expr[2][1]
                else:
                    key = expr[2]
                return self.lookup_key(base, key)
            elif expr[0] == '[]':
                base = self.eval_expr(expr[1])
                key = self.eval_expr(expr[2])
                return self.lookup_key(base, key)
            elif expr[0] == 'not':
                return not self.is_truthy(self.eval_expr(expr[1]))
            elif expr[0] == 'and':
                left = self.eval_expr(expr[1])
                if not self.is_truthy(left):
                    return False
                return self.is_truthy(self.eval_expr(expr[2]))
            elif expr[0] == 'or':
                left = self.eval_expr(expr[1])
                if self.is_truthy(left):
                    return True
                return self.is_truthy(self.eval_expr(expr[2]))
            elif expr[0] == '==':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                return self.equals(left, right)
            elif expr[0] == '!=':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                return not self.equals(left, right)
            elif expr[0] == '<':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                if isinstance(left, int) and isinstance(right, int):
                    return left < right
                elif isinstance(left, str) and isinstance(right, str):
                    return left < right
                else:
                    raise TemplateError('bad_operand', 0)
            elif expr[0] == '<=':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                if isinstance(left, int) and isinstance(right, int):
                    return left <= right
                elif isinstance(left, str) and isinstance(right, str):
                    return left <= right
                else:
                    raise TemplateError('bad_operand', 0)
            elif expr[0] == '>':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                if isinstance(left, int) and isinstance(right, int):
                    return left > right
                elif isinstance(left, str) and isinstance(right, str):
                    return left > right
                else:
                    raise TemplateError('bad_operand', 0)
            elif expr[0] == '>=':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                if isinstance(left, int) and isinstance(right, int):
                    return left >= right
                elif isinstance(left, str) and isinstance(right, str):
                    return left >= right
                else:
                    raise TemplateError('bad_operand', 0)
            elif expr[0] == 'in':
                left = self.eval_expr(expr[1])
                right = self.eval_expr(expr[2])
                if isinstance(right, str):
                    return isinstance(left, str) and left in right
                elif isinstance(right, list):
                    return any(self.equals(left, item) for item in right)
                elif isinstance(right, dict):
                    return isinstance(left, str) and left in right
                else:
                    return False
            elif expr[0] == 'pipeline':
                base_val = self.eval_expr(expr[1])
                for filt in expr[2]:
                    base_val = self.apply_filter(base_val, filt)
                return base_val
            elif expr[0] == 'filter':
                # Shouldn't happen as filters are in pipelines
                return expr
        return None

    def apply_filter(self, value, filter_expr):
        """Apply a filter to a value."""
        filter_name = filter_expr[1]
        args = filter_expr[2]

        # Evaluate arguments
        eval_args = [self.eval_expr(arg) for arg in args]

        if filter_name == 'upper':
            text = self.value_to_text(value)
            return {'__text__': text.upper(), '__safe__': self.is_safe(value)}
        elif filter_name == 'lower':
            text = self.value_to_text(value)
            return {'__text__': text.lower(), '__safe__': self.is_safe(value)}
        elif filter_name == 'trim':
            text = self.value_to_text(value)
            return {'__text__': text.strip(), '__safe__': self.is_safe(value)}
        elif filter_name == 'length':
            if value is None or value is False or value is True:
                return 0
            elif isinstance(value, (int, bool)):
                return 0
            elif isinstance(value, str):
                return len(value)
            elif isinstance(value, list):
                return len(value)
            elif isinstance(value, dict):
                return len(value)
            else:
                return 0
        elif filter_name == 'first':
            if isinstance(value, str):
                return value[0] if value else None
            elif isinstance(value, list):
                return value[0] if value else None
            elif isinstance(value, dict):
                keys = list(value.keys())
                return keys[0] if keys else None
            else:
                return None
        elif filter_name == 'safe':
            # Mark as safe
            if isinstance(value, dict) and '__text__' in value:
                value['__safe__'] = True
                return value
            else:
                return {'__text__': self.value_to_text(value), '__safe__': True}
        elif filter_name == 'escape':
            # If already safe, don't re-escape
            if self.is_safe(value):
                return value if isinstance(value, dict) and '__text__' in value else {'__text__': self.value_to_text(value), '__safe__': True}
            text = self.value_to_text(value)
            escaped = self.html_escape(text)
            return {'__text__': escaped, '__safe__': True}
        elif filter_name == 'default':
            if self.is_truthy(value):
                return value
            else:
                return eval_args[0]
        elif filter_name == 'join':
            sep = self.value_to_text(eval_args[0])
            if isinstance(value, str):
                joined = sep.join(value)
            elif isinstance(value, list):
                items = [self.value_to_text(v) for v in value]
                joined = sep.join(items)
            elif isinstance(value, dict):
                keys = [self.value_to_text(k) for k in value.keys()]
                joined = sep.join(keys)
            elif value is None:
                joined = ''
            else:
                joined = self.value_to_text(value)
            return {'__text__': joined, '__safe__': self.is_safe(value)}
        elif filter_name == 'replace':
            text = self.value_to_text(value)
            from_str = self.value_to_text(eval_args[0])
            to_str = self.value_to_text(eval_args[1])
            if from_str:
                replaced = text.replace(from_str, to_str)
            else:
                replaced = text
            return {'__text__': replaced, '__safe__': self.is_safe(value)}
        elif filter_name == 'slice':
            start_val = eval_args[0]
            length_val = eval_args[1]

            # Check if valid integers >= 0
            if not (isinstance(start_val, int) and start_val >= 0):
                if isinstance(start_val, str) and start_val.isdigit():
                    start_val = int(start_val)
                else:
                    return value

            if not (isinstance(length_val, int) and length_val >= 0):
                if isinstance(length_val, str) and length_val.isdigit():
                    length_val = int(length_val)
                else:
                    return value

            if isinstance(value, list):
                result = value[start_val:start_val + length_val]
                return result
            elif isinstance(value, str):
                result = value[start_val:start_val + length_val]
                return result
            else:
                text = self.value_to_text(value)
                result = text[start_val:start_val + length_val]
                return result

        return value

    def lookup(self, name):
        """Look up variable in scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                val = scope[name]
                # Extract text if it's a filter result
                if isinstance(val, dict) and '__text__' in val:
                    # Return as special dict to preserve safety
                    return val
                return val
        return None

    def lookup_key(self, base, key):
        """Lookup base[key]."""
        if base is None:
            return None

        # Convert key to appropriate type
        if isinstance(key, tuple):
            if key[0] == 'int':
                key = key[1]
            elif key[0] == 'var':
                key = key[1]
            elif key[0] == 'str':
                key = key[1]

        if isinstance(base, dict):
            if key in base:
                return base[key]
            # Pseudo-keys
            if key == 'size':
                return len(base)
            elif key == 'keys':
                return list(base.keys())
            elif key == 'type':
                return 'map'
            return None

        if isinstance(base, list):
            if isinstance(key, int) and 0 <= key < len(base):
                return base[key]
            elif isinstance(key, str) and key.isdigit():
                idx = int(key)
                if 0 <= idx < len(base):
                    return base[idx]
            if key == 'size':
                return len(base)
            elif key == 'type':
                return 'list'
            return None

        if isinstance(base, str):
            if isinstance(key, int) and 0 <= key < len(base):
                return base[key]
            elif isinstance(key, str) and key.isdigit():
                idx = int(key)
                if 0 <= idx < len(base):
                    return base[idx]
            if key == 'size':
                return len(base)
            elif key == 'type':
                return 'string'
            return None

        # Other types
        if key == 'type':
            if isinstance(base, bool):
                return 'bool'
            elif isinstance(base, int):
                return 'number'
        return None

    def is_truthy(self, value):
        """Check truthiness (spec-defined)."""
        if value is None or value is False:
            return False
        if value == 0 or value == '' or value == '0' or value == 'false':
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True

    def equals(self, left, right):
        """Check equality (spec-defined)."""
        # Different types
        if type(left) != type(right):
            if left is None and right is None:
                return True
            return False

        # Same types
        if isinstance(left, list):
            if len(left) != len(right):
                return False
            return all(self.equals(l, r) for l, r in zip(left, right))

        if isinstance(left, dict):
            if len(left) != len(right):
                return False
            for k in left:
                if k not in right or not self.equals(left[k], right[k]):
                    return False
            return True

        return left == right

    def to_sequence(self, value):
        """Convert value to sequence for loops."""
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return list(value)
        elif isinstance(value, dict):
            return list(value.keys())
        elif value is None:
            return []
        else:
            raise TemplateError('not_iterable', 0)

    def value_to_text(self, value):
        """Convert value to text."""
        if value is None:
            return ''
        if isinstance(value, dict):
            if '__text__' in value:
                return value['__text__']
            # Map representation
            items = []
            for k, v in value.items():
                if k.startswith('__'):
                    continue
                k_text = self.value_to_text(k)
                v_text = self.value_to_text(v)
                items.append(f"{k_text}: {v_text}")
            return '{' + ', '.join(items) + '}'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            items = [self.value_to_text(v) for v in value]
            return '[' + ', '.join(items) + ']'
        return ''

    def is_safe(self, value):
        """Check if value is marked safe."""
        if isinstance(value, dict) and value.get('__safe__'):
            return True
        return False

    def html_escape(self, text):
        """HTML escape text."""
        if not isinstance(text, str):
            return text
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&#34;')
        text = text.replace("'", '&#39;')
        return text
