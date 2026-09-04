"""Text template engine implementation."""


class TemplateError(Exception):
    """Template rendering error with kind and position."""
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"{kind} at position {pos}")


WHITESPACE = set(' \t\r\n\x0b\x0c')
ESCAPE_MAP = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&#34;', "'": '&#39;'}


class Lexer:
    """Tokenizes template source into literal text and tags."""

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.tokens = []

    def lex(self):
        """Scan source and produce token stream."""
        while self.pos < len(self.source):
            if self.pos < len(self.source) - 1 and self.source[self.pos] == '{':
                next_char = self.source[self.pos + 1]
                if next_char in ('{', '%', '#'):
                    self._scan_tag(next_char)
                    continue
            self._scan_literal()

        self._apply_trimming()
        self.tokens = [t for t in self.tokens if t[0] != 'comment']
        return self.tokens

    def _scan_tag(self, tag_type):
        """Scan a single tag starting at current position."""
        tag_pos = self.pos
        self.pos += 2

        if tag_type == '{':
            closer = '}}'
            kind = 'interp'
        elif tag_type == '%':
            closer = '%}'
            kind = 'block'
        else:
            closer = '#}'
            kind = 'comment'

        left_marker = False
        if self.pos < len(self.source) and self.source[self.pos] == '-':
            left_marker = True
            self.pos += 1

        closer_pos = self.source.find(closer, self.pos)
        if closer_pos == -1:
            raise TemplateError('unclosed_tag', tag_pos)

        right_marker = False
        content_end = closer_pos
        if closer_pos > 0 and self.source[closer_pos - 1] == '-':
            right_marker = True
            content_end = closer_pos - 1

        content = self.source[self.pos:content_end]
        self.pos = closer_pos + 2

        self.tokens.append((kind, content, tag_pos, left_marker, right_marker))

    def _scan_literal(self):
        """Scan a run of literal text until the next tag."""
        start = self.pos
        while self.pos < len(self.source):
            if self.pos < len(self.source) - 1 and self.source[self.pos] == '{':
                if self.source[self.pos + 1] in ('{', '%', '#'):
                    break
            self.pos += 1

        if self.pos > start:
            self.tokens.append(('literal', self.source[start:self.pos], start, False, False))

    def _apply_trimming(self):
        """Apply whitespace trimming based on markers."""
        for i in range(len(self.tokens)):
            kind, content, pos, left_marker, right_marker = self.tokens[i]

            if kind == 'literal':
                if i > 0 and self.tokens[i-1][4]:
                    content = content.lstrip(' \t\r\n\x0b\x0c')

                if i < len(self.tokens) - 1 and self.tokens[i+1][3]:
                    content = content.rstrip(' \t\r\n\x0b\x0c')

                self.tokens[i] = (kind, content, pos, left_marker, right_marker)


class ExprParser:
    """Parses template expressions."""

    def __init__(self, source, tag_pos):
        self.source = source
        self.tag_pos = tag_pos
        self.pos = 0

    def parse(self):
        """Parse expression and return AST."""
        self.skip_ws()
        result = self.parse_pipeline()
        self.skip_ws()
        if self.pos < len(self.source):
            raise TemplateError('syntax', self.tag_pos)
        return result

    def parse_pipeline(self):
        """pipeline := disjunct ( '|' filter )*"""
        result = self.parse_disjunct()
        while True:
            saved_pos = self.pos
            self.skip_ws()
            if self.pos >= len(self.source) or self.source[self.pos] != '|':
                self.pos = saved_pos
                break
            self.pos += 1
            self.skip_ws()
            filter_name = self.read_identifier()
            if not filter_name:
                raise TemplateError('syntax', self.tag_pos)

            # Validate filter exists
            filter_arity = {
                'upper': 0, 'lower': 0, 'trim': 0, 'length': 0, 'first': 0,
                'safe': 0, 'escape': 0, 'default': 1, 'join': 1, 'replace': 2, 'slice': 2
            }
            if filter_name not in filter_arity:
                raise TemplateError('unknown_filter', self.tag_pos)

            args = []
            if self.pos < len(self.source) and self.peek_char() == ':':
                self.pos += 1
                self.skip_ws()
                args = self.parse_filter_args()

            # Validate arity
            if len(args) != filter_arity[filter_name]:
                raise TemplateError('filter_args', self.tag_pos)

            result = ('filter', filter_name, args, result)
        return result

    def parse_disjunct(self):
        """disjunct := conjunct ( 'or' conjunct )*"""
        result = self.parse_conjunct()
        while self.peek_word() == 'or':
            self.skip_ws()
            self.pos += 2
            self.skip_ws()
            result = ('or', result, self.parse_conjunct())
        return result

    def parse_conjunct(self):
        """conjunct := negation ( 'and' negation )*"""
        result = self.parse_negation()
        while self.peek_word() == 'and':
            self.skip_ws()
            self.pos += 3
            self.skip_ws()
            result = ('and', result, self.parse_negation())
        return result

    def parse_negation(self):
        """negation := 'not' negation | comparison"""
        if self.peek_word() == 'not':
            self.pos += 3
            self.skip_ws()
            return ('not', self.parse_negation())
        return self.parse_comparison()

    def parse_comparison(self):
        """comparison := primary [ cmpop primary ]"""
        result = self.parse_primary()
        cmpop = self.peek_cmpop()
        if cmpop:
            self.skip_ws()
            if cmpop == 'in':
                self.pos += 2
            else:
                self.pos += len(cmpop)
            self.skip_ws()
            right = self.parse_primary()
            return (cmpop, result, right)
        return result

    def parse_primary(self):
        """primary := atom ( '.' key | '[' primary ']' )*"""
        result = self.parse_atom()
        while True:
            if self.pos < len(self.source) and self.peek_char() == '.':
                self.pos += 1
                self.skip_ws()
                key = self.read_key()
                result = ('getattr', result, key)
            elif self.pos < len(self.source) and self.peek_char() == '[':
                self.pos += 1
                self.skip_ws()
                idx = self.parse_primary()
                self.skip_ws()
                if self.pos >= len(self.source) or self.peek_char() != ']':
                    raise TemplateError('syntax', self.tag_pos)
                self.pos += 1
                result = ('getitem', result, idx)
            else:
                break
        return result

    def parse_atom(self):
        """atom := INT | STRING | 'true' | 'false' | 'none' | IDENT"""
        self.skip_ws()
        if self.pos >= len(self.source):
            raise TemplateError('syntax', self.tag_pos)

        ch = self.source[self.pos]

        if ch.isdigit():
            num_str = ''
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                num_str += self.source[self.pos]
                self.pos += 1
            return ('int', int(num_str))

        if ch in ('"', "'"):
            return ('str', self.read_string())

        if ch.isalpha() or ch == '_':
            word = self.read_identifier()
            if word == 'true':
                return ('bool', True)
            elif word == 'false':
                return ('bool', False)
            elif word == 'none':
                return ('none',)
            else:
                return ('var', word)

        raise TemplateError('syntax', self.tag_pos)

    def parse_filter_args(self):
        """Parse filter arguments."""
        args = []
        while self.pos < len(self.source) and self.peek_char() not in ('|', None):
            self.skip_ws()
            if self.pos >= len(self.source) or self.peek_char() in ('|', None):
                break
            if self.peek_char() in ('"', "'"):
                args.append(self.read_string())
            else:
                arg_start = self.pos
                arg_text = ''
                while self.pos < len(self.source) and self.source[self.pos] not in (',', '|'):
                    arg_text += self.source[self.pos]
                    self.pos += 1
                arg_text = arg_text.strip()
                if arg_text == 'true':
                    args.append(True)
                elif arg_text == 'false':
                    args.append(False)
                elif arg_text == 'none':
                    args.append(None)
                elif arg_text.isdigit():
                    args.append(int(arg_text))
                else:
                    args.append(arg_text)

            self.skip_ws()
            if self.pos < len(self.source) and self.peek_char() == ',':
                self.pos += 1
            elif self.pos >= len(self.source) or self.peek_char() in ('|', None):
                break

        return args

    def read_identifier(self):
        """Read an identifier."""
        result = ''
        if self.pos >= len(self.source):
            return result
        ch = self.source[self.pos]
        if not (ch.isalpha() or ch == '_'):
            return result
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            result += self.source[self.pos]
            self.pos += 1
        return result

    def read_string(self):
        """Read a string literal."""
        quote = self.source[self.pos]
        self.pos += 1
        result = ''
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == quote:
                self.pos += 1
                return result
            elif ch == '\\' and self.pos + 1 < len(self.source):
                self.pos += 1
                next_ch = self.source[self.pos]
                if next_ch == 'n':
                    result += '\n'
                elif next_ch == 't':
                    result += '\t'
                else:
                    result += next_ch
                self.pos += 1
            else:
                result += ch
                self.pos += 1
        raise TemplateError('syntax', self.tag_pos)

    def read_key(self):
        """Read a key after dot."""
        self.skip_ws()
        if self.pos >= len(self.source):
            raise TemplateError('syntax', self.tag_pos)
        if self.source[self.pos].isdigit():
            result = ''
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                result += self.source[self.pos]
                self.pos += 1
            return result
        return self.read_identifier()

    def skip_ws(self):
        """Skip whitespace."""
        while self.pos < len(self.source) and self.source[self.pos] in WHITESPACE:
            self.pos += 1

    def peek_char(self):
        """Peek at current character without skipping whitespace."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek_word(self):
        """Peek at next word."""
        saved_pos = self.pos
        self.skip_ws()
        word = ''
        while self.pos < len(self.source) and (self.source[self.pos].isalpha() or self.source[self.pos] == '_'):
            word += self.source[self.pos]
            self.pos += 1
        self.pos = saved_pos
        if word in ('or', 'and', 'not', 'in'):
            return word
        return None

    def peek_cmpop(self):
        """Peek at comparison operator."""
        saved_pos = self.pos
        self.skip_ws()
        if self.pos >= len(self.source):
            self.pos = saved_pos
            return None
        remaining = self.source[self.pos:]
        for op in ('==', '!=', '<=', '>=', '<', '>', 'in'):
            if remaining.startswith(op):
                if op == 'in':
                    if self.pos + 2 < len(self.source) and (self.source[self.pos + 2].isalnum() or self.source[self.pos + 2] == '_'):
                        self.pos = saved_pos
                        return None
                self.pos = saved_pos
                return op
        self.pos = saved_pos
        return None


def _get_block_name(token):
    """Extract block name from token content."""
    content = token[1].strip()
    if not content:
        return None
    parts = content.split(None, 1)
    return parts[0]


class Parser:
    """Parses tag stream into an AST."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        """Parse token stream into AST."""
        nodes = []
        while self.pos < len(self.tokens):
            nodes.append(self.parse_node())
        return nodes

    def parse_node(self):
        """Parse a single node."""
        token = self.tokens[self.pos]
        kind = token[0]

        if kind == 'literal':
            self.pos += 1
            return ('literal', token[1])
        elif kind == 'interp':
            self.pos += 1
            return self._parse_interp(token)
        elif kind == 'block':
            return self._parse_block_tag(token)

    def _parse_interp(self, token):
        """Parse interpolation tag."""
        kind, content, tag_pos, left_marker, right_marker = token
        content = content.strip()

        if not content:
            raise TemplateError('syntax', tag_pos)

        parser = ExprParser(content, tag_pos)
        expr = parser.parse()
        return ('interp', expr, tag_pos)

    def _parse_block_tag(self, token):
        """Parse block tag or return None if it's a closing tag."""
        kind, content, tag_pos, left_marker, right_marker = token
        content = content.strip()

        if not content:
            raise TemplateError('unknown_tag', tag_pos)

        parts = content.split(None, 1)
        tag_name = parts[0]
        rest = parts[1] if len(parts) > 1 else ''

        if tag_name == 'if':
            if not rest:
                raise TemplateError('syntax', tag_pos)
            if '|' in rest:
                raise TemplateError('syntax', tag_pos)
            parser = ExprParser(rest, tag_pos)
            expr = parser.parse()
            self.pos += 1

            body = []
            branches = [expr, body]

            while self.pos < len(self.tokens):
                if self.tokens[self.pos][0] != 'block':
                    body.append(self.parse_node())
                else:
                    block_name = _get_block_name(self.tokens[self.pos])
                    if block_name == 'elif':
                        block_content = self.tokens[self.pos][1].strip().split(None, 1)
                        block_rest = block_content[1] if len(block_content) > 1 else ''
                        block_tag_pos = self.tokens[self.pos][2]
                        if not block_rest:
                            raise TemplateError('syntax', block_tag_pos)
                        if '|' in block_rest:
                            raise TemplateError('syntax', block_tag_pos)
                        expr_parser = ExprParser(block_rest, block_tag_pos)
                        elif_expr = expr_parser.parse()
                        self.pos += 1
                        elif_body = []
                        branches.extend([elif_expr, elif_body])
                        body = elif_body
                    elif block_name == 'else':
                        block_content = self.tokens[self.pos][1].strip().split(None, 1)
                        block_rest = block_content[1] if len(block_content) > 1 else ''
                        block_tag_pos = self.tokens[self.pos][2]
                        if block_rest:
                            raise TemplateError('syntax', block_tag_pos)
                        self.pos += 1
                        else_body = []
                        branches.append(else_body)
                        body = else_body
                    elif block_name == 'endif':
                        self.pos += 1
                        return ('if_block', branches, tag_pos)
                    else:
                        body.append(self.parse_node())

            raise TemplateError('unclosed_block', tag_pos)

        elif tag_name == 'for':
            if not rest:
                raise TemplateError('syntax', tag_pos)
            parts = rest.split(None, 2)
            if len(parts) < 3 or parts[1] != 'in':
                raise TemplateError('syntax', tag_pos)
            var_name = parts[0]
            expr_str = ' '.join(parts[2:])
            parser = ExprParser(expr_str, tag_pos)
            expr = parser.parse()
            self.pos += 1

            body = []
            while self.pos < len(self.tokens):
                if self.tokens[self.pos][0] != 'block':
                    body.append(self.parse_node())
                else:
                    block_name = _get_block_name(self.tokens[self.pos])
                    if block_name == 'empty':
                        self.pos += 1
                        empty_body = []
                        while self.pos < len(self.tokens):
                            if self.tokens[self.pos][0] != 'block':
                                empty_body.append(self.parse_node())
                            else:
                                if _get_block_name(self.tokens[self.pos]) == 'endfor':
                                    self.pos += 1
                                    return ('for_block', var_name, expr, body, empty_body, tag_pos)
                                else:
                                    empty_body.append(self.parse_node())
                        raise TemplateError('unclosed_block', tag_pos)
                    elif block_name == 'endfor':
                        self.pos += 1
                        return ('for_block', var_name, expr, body, [], tag_pos)
                    else:
                        body.append(self.parse_node())

            raise TemplateError('unclosed_block', tag_pos)

        elif tag_name == 'set':
            if not rest:
                raise TemplateError('syntax', tag_pos)
            if '=' not in rest:
                raise TemplateError('syntax', tag_pos)
            parts = rest.split('=', 1)
            var_name = parts[0].strip()
            expr_str = parts[1].strip()
            if not var_name or not expr_str:
                raise TemplateError('syntax', tag_pos)
            if not (var_name[0].isalpha() or var_name[0] == '_'):
                raise TemplateError('syntax', tag_pos)
            for ch in var_name:
                if not (ch.isalnum() or ch == '_'):
                    raise TemplateError('syntax', tag_pos)
            if '==' in rest:
                idx = rest.find('=')
                if idx > 0 and rest[idx-1] == '=':
                    raise TemplateError('syntax', tag_pos)
                if idx + 1 < len(rest) and rest[idx+1] == '=':
                    raise TemplateError('syntax', tag_pos)
            parser = ExprParser(expr_str, tag_pos)
            expr = parser.parse()
            self.pos += 1
            return ('set', var_name, expr, tag_pos)

        else:
            raise TemplateError('unknown_tag', tag_pos)


def render(source, context):
    """Render a template."""
    lexer = Lexer(source)
    tokens = lexer.lex()

    parser = Parser(tokens)
    ast = parser.parse()

    renderer = Renderer(context)
    return renderer.render(ast)


class Renderer:
    """Renders AST."""

    def __init__(self, context):
        self.scopes = [dict(context)]

    def render(self, nodes):
        """Render nodes."""
        result = []
        for node in nodes:
            result.append(self.render_node(node))
        return ''.join(result)

    def render_node(self, node):
        """Render a single node."""
        if node[0] == 'literal':
            return node[1]
        elif node[0] == 'interp':
            value, is_safe = self.eval_expr(node[1])
            text = self.value_to_text(value)
            if not is_safe:
                text = self.escape_html(text)
            return text
        elif node[0] == 'if_block':
            return self.render_if_block(node[1])
        elif node[0] == 'for_block':
            return self.render_for_block(node[1], node[2], node[3], node[4])
        elif node[0] == 'set':
            return self.render_set(node[1], node[2])
        return ''

    def render_if_block(self, branches):
        """Render an if block."""
        # branches alternates expr, body, expr, body, ..., [body for else]
        # If len is odd, last element is the else body
        for i in range(0, len(branches) - 1, 2):
            expr = branches[i]
            body = branches[i+1]
            if self.is_truthy(self.eval_expr(expr)[0]):
                return self.render(body)
        # Handle else clause if present (len is odd)
        if len(branches) % 2 == 1:
            return self.render(branches[-1])
        return ''

    def render_for_block(self, var_name, expr, body, empty_body):
        """Render a for loop."""
        value, _ = self.eval_expr(expr)
        sequence = self.get_sequence(value)

        if not sequence:
            if empty_body:
                return self.render(empty_body)
            return ''

        result = []
        self.scopes.append({})
        scope = self.scopes[-1]

        for idx, item in enumerate(sequence):
            scope[var_name] = item
            scope['loop'] = {
                'index': idx + 1,
                'index0': idx,
                'first': idx == 0,
                'last': idx == len(sequence) - 1,
                'length': len(sequence)
            }
            result.append(self.render(body))

        self.scopes.pop()
        return ''.join(result)

    def render_set(self, var_name, expr):
        """Render a set statement."""
        value, is_safe = self.eval_expr(expr)
        if is_safe:
            value = (value, True)
        self.scopes[-1][var_name] = value
        return ''

    def eval_expr(self, expr):
        """Evaluate expression, return (value, is_safe)."""
        if expr[0] == 'int':
            return (expr[1], False)
        elif expr[0] == 'str':
            return (expr[1], False)
        elif expr[0] == 'bool':
            return (expr[1], False)
        elif expr[0] == 'none':
            return (None, False)
        elif expr[0] == 'var':
            return self.lookup_var(expr[1])
        elif expr[0] == 'filter':
            return self.apply_filter(expr[1], expr[2], expr[3])
        elif expr[0] == 'getattr':
            return self.eval_getattr(expr[1], expr[2])
        elif expr[0] == 'getitem':
            return self.eval_getitem(expr[1], expr[2])
        elif expr[0] in ('and', 'or', 'not', '==', '!=', '<', '<=', '>', '>=', 'in'):
            return self.eval_comparison(expr)
        return (None, False)

    def lookup_var(self, name):
        """Look up a variable in scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                value = scope[name]
                if isinstance(value, tuple) and len(value) == 2:
                    return value
                return (value, False)
        return (None, False)

    def apply_filter(self, name, args, value_expr):
        """Apply a filter."""
        value, is_safe = self.eval_expr(value_expr)

        if name == 'upper':
            text = self.value_to_text(value)
            return (text.upper(), is_safe)
        elif name == 'lower':
            text = self.value_to_text(value)
            return (text.lower(), is_safe)
        elif name == 'trim':
            text = self.value_to_text(value)
            return (text.strip(), is_safe)
        elif name == 'length':
            if value is None:
                return (0, is_safe)
            elif isinstance(value, bool):
                return (0, is_safe)
            elif isinstance(value, int):
                return (len(str(value)), is_safe)
            elif isinstance(value, str):
                return (len(value), is_safe)
            elif isinstance(value, list):
                return (len(value), is_safe)
            elif isinstance(value, dict):
                return (len(value), is_safe)
            return (0, is_safe)
        elif name == 'first':
            if isinstance(value, str) and value:
                return (value[0], is_safe)
            elif isinstance(value, list) and value:
                return (value[0], is_safe)
            elif isinstance(value, dict) and value:
                return (list(value.keys())[0], is_safe)
            return (None, is_safe)
        elif name == 'safe':
            return (value, True)
        elif name == 'escape':
            text = self.value_to_text(value)
            return (self.escape_html(text), True)
        elif name == 'default':
            if self.is_falsy(value):
                if args:
                    return (args[0], False)
                return ('', False)
            return (value, is_safe)
        elif name == 'join':
            if args:
                sep = self.value_to_text(args[0])
                if isinstance(value, str):
                    return (sep.join(value), is_safe)
                elif isinstance(value, list):
                    return (sep.join(self.value_to_text(v) for v in value), is_safe)
                elif isinstance(value, dict):
                    return (sep.join(value.keys()), is_safe)
                else:
                    return (self.value_to_text(value), is_safe)
            return (self.value_to_text(value), is_safe)
        elif name == 'replace':
            if len(args) >= 2:
                search = self.value_to_text(args[0])
                replace = self.value_to_text(args[1])
                text = self.value_to_text(value)
                if search:
                    text = text.replace(search, replace)
                return (text, is_safe)
            return (self.value_to_text(value), is_safe)
        elif name == 'slice':
            start_arg = args[0]
            len_arg = args[1]
            if isinstance(start_arg, int) and start_arg >= 0 and isinstance(len_arg, int) and len_arg >= 0:
                if isinstance(value, str):
                    return (value[start_arg:start_arg+len_arg], is_safe)
                elif isinstance(value, list):
                    return (value[start_arg:start_arg+len_arg], is_safe)
                else:
                    text = self.value_to_text(value)
                    return (text[start_arg:start_arg+len_arg], is_safe)
            return (value, is_safe)

        return (value, is_safe)

    def eval_getattr(self, base_expr, key):
        """Evaluate attribute access."""
        base, is_safe = self.eval_expr(base_expr)
        return self.lookup(base, key, is_safe)

    def eval_getitem(self, base_expr, idx_expr):
        """Evaluate subscript access."""
        base, is_safe = self.eval_expr(base_expr)
        idx, _ = self.eval_expr(idx_expr)
        return self.lookup(base, idx, is_safe)

    def lookup(self, base, key, is_safe):
        """Lookup in base object with key."""
        if base is None:
            return (None, False)
        if isinstance(base, dict):
            if key in base:
                return (base[key], False)
        if isinstance(base, (list, str)):
            if isinstance(key, int) and 0 <= key < len(base):
                return (base[key], False)
            elif isinstance(key, str) and key.isdigit():
                idx = int(key)
                if 0 <= idx < len(base):
                    return (base[idx], False)
        if isinstance(key, str):
            if key == 'size':
                if isinstance(base, (str, list, dict)):
                    return (len(base), False)
            elif key == 'keys':
                if isinstance(base, dict):
                    return (list(base.keys()), False)
            elif key == 'type':
                if isinstance(base, bool):
                    return ('bool', False)
                elif isinstance(base, int):
                    return ('number', False)
                elif isinstance(base, str):
                    return ('string', False)
                elif isinstance(base, list):
                    return ('list', False)
                elif isinstance(base, dict):
                    return ('map', False)
                elif base is None:
                    return ('none', False)
        return (None, False)

    def eval_comparison(self, expr):
        """Evaluate comparison and logical operators."""
        if expr[0] == 'not':
            val, _ = self.eval_expr(expr[1])
            return (not self.is_truthy(val), False)
        elif expr[0] == 'and':
            left, _ = self.eval_expr(expr[1])
            if not self.is_truthy(left):
                return (False, False)
            right, _ = self.eval_expr(expr[2])
            return (self.is_truthy(right), False)
        elif expr[0] == 'or':
            left, _ = self.eval_expr(expr[1])
            if self.is_truthy(left):
                return (True, False)
            right, _ = self.eval_expr(expr[2])
            return (self.is_truthy(right), False)
        elif expr[0] == '==':
            left, _ = self.eval_expr(expr[1])
            right, _ = self.eval_expr(expr[2])
            if type(left) != type(right):
                return (False, False)
            return (left == right, False)
        elif expr[0] == '!=':
            left, _ = self.eval_expr(expr[1])
            right, _ = self.eval_expr(expr[2])
            if type(left) != type(right):
                return (True, False)
            return (left != right, False)
        elif expr[0] in ('<', '<=', '>', '>='):
            left, _ = self.eval_expr(expr[1])
            right, _ = self.eval_expr(expr[2])
            if (isinstance(left, (int, bool)) or isinstance(left, str)) and \
               (isinstance(right, (int, bool)) or isinstance(right, str)):
                if type(left) != type(right):
                    raise TemplateError('bad_operand', 0)
                if isinstance(left, bool) or isinstance(right, bool):
                    raise TemplateError('bad_operand', 0)
                if expr[0] == '<':
                    return (left < right, False)
                elif expr[0] == '<=':
                    return (left <= right, False)
                elif expr[0] == '>':
                    return (left > right, False)
                elif expr[0] == '>=':
                    return (left >= right, False)
            raise TemplateError('bad_operand', 0)
        elif expr[0] == 'in':
            left, _ = self.eval_expr(expr[1])
            right, _ = self.eval_expr(expr[2])
            if isinstance(right, str):
                return (isinstance(left, str) and left in right, False)
            elif isinstance(right, list):
                return (left in right, False)
            elif isinstance(right, dict):
                return (isinstance(left, str) and left in right, False)
            return (False, False)
        return (None, False)

    def get_sequence(self, value):
        """Get sequence from value for iteration."""
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

    def is_truthy(self, value):
        """Check if value is truthy."""
        if value is None or value is False:
            return False
        if value == 0 or value == '' or value == '0' or value == 'false':
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True

    def is_falsy(self, value):
        """Check if value is falsy."""
        return not self.is_truthy(value)

    def value_to_text(self, value):
        """Convert value to text."""
        if value is None:
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
            items = []
            for k, v in value.items():
                items.append(k + ': ' + self.value_to_text(v))
            return '{' + ', '.join(items) + '}'
        return ''

    def escape_html(self, text):
        """Escape HTML characters."""
        for char, escape in ESCAPE_MAP.items():
            text = text.replace(char, escape)
        return text
