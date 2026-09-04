"""GitAttributes-style resolver."""


class AttrError(ValueError):
    """Error raised when parsing gitattributes lines."""
    def __init__(self, kind, message=""):
        self.kind = kind
        super().__init__(message)


# Character class definitions (ASCII only, no .isX() methods)
def _is_letter(c):
    return ('A' <= c <= 'Z') or ('a' <= c <= 'z')


def _is_digit(c):
    return '0' <= c <= '9'


def _is_alnum(c):
    return _is_letter(c) or _is_digit(c)


def _is_space(c):
    return c in ' \t\n\v\f\r'


def _is_upper(c):
    return 'A' <= c <= 'Z'


def _is_lower(c):
    return 'a' <= c <= 'z'


def _is_xdigit(c):
    return _is_digit(c) or ('a' <= c <= 'f') or ('A' <= c <= 'F')


def _is_printable(c):
    # ASCII printable: space (32) to ~ (126)
    return 32 <= ord(c) <= 126


def _is_punct(c):
    # ASCII punctuation: 33-47, 58-64, 91-96, 123-126
    code = ord(c)
    return (33 <= code <= 47) or (58 <= code <= 64) or (91 <= code <= 96) or (123 <= code <= 126)


def _count_backslashes_before(s, pos):
    """Count consecutive backslashes immediately before position pos."""
    count = 0
    i = pos - 1
    while i >= 0 and s[i] == '\\':
        count += 1
        i -= 1
    return count


def _is_escaped(s, pos):
    """Check if character at pos is escaped (preceded by odd number of backslashes)."""
    return _count_backslashes_before(s, pos) % 2 == 1


def _strip_trailing_unescaped_whitespace(line):
    """Strip trailing spaces and tabs that are not escaped."""
    while line and line[-1] in ' \t':
        if not _is_escaped(line, len(line) - 1):
            line = line[:-1]
        else:
            break
    return line


def _split_pattern_and_attrs(line):
    """Split line into pattern and attribute fields.

    Returns (pattern, attr_fields) where attr_fields is a list of strings.
    """
    # First field is the pattern (runs until first unescaped space/tab)
    i = 0
    while i < len(line):
        if line[i] in ' \t' and not _is_escaped(line, i):
            break
        i += 1

    pattern = line[:i]
    rest = line[i:]

    # Split rest on unescaped spaces/tabs
    attr_fields = []
    current = []
    j = 0
    while j < len(rest):
        if rest[j] in ' \t' and not _is_escaped(rest, j):
            if current:
                attr_fields.append(''.join(current))
                current = []
            j += 1
        else:
            current.append(rest[j])
            j += 1
    if current:
        attr_fields.append(''.join(current))

    return pattern, attr_fields


def _validate_name(name):
    """Check if name is valid per section 2.

    First char must be letter or _, rest must be letter, digit, -, _, or .
    """
    if not name:
        return False
    if not (_is_letter(name[0]) or name[0] == '_'):
        return False
    for c in name[1:]:
        if not (_is_alnum(c) or c in '-_.'):
            return False
    return True


def _parse_attr_field(field):
    """Parse one attribute field.

    Returns (name, value_form) where:
    - value_form is one of: 'set', 'unset', 'unspec', or a string value
    Raises AttrError if invalid.
    """
    if not field:
        raise AttrError('bad_attr_name', f"empty field")

    if field[0] == '-':
        # Unset form: -name
        name = field[1:]
        if not name:
            raise AttrError('bad_attr_name', f"invalid form: {field}")
        if '=' in name:
            raise AttrError('bad_attr_name', f"unset form cannot have value: {field}")
        if not _validate_name(name):
            raise AttrError('bad_attr_name', f"invalid name: {name}")
        return name, 'unset'
    elif field[0] == '!':
        # Unspec form: !name
        name = field[1:]
        if not name:
            raise AttrError('bad_attr_name', f"invalid form: {field}")
        if '=' in name:
            raise AttrError('bad_attr_name', f"unspec form cannot have value: {field}")
        if not _validate_name(name):
            raise AttrError('bad_attr_name', f"invalid name: {name}")
        return name, 'unspec'
    else:
        # Set or valued form
        if '=' in field:
            # name=value
            eq_pos = field.index('=')
            name = field[:eq_pos]
            value = field[eq_pos + 1:]
            if not _validate_name(name):
                raise AttrError('bad_attr_name', f"invalid name: {name}")
            return name, value
        else:
            # set form: name
            if not _validate_name(field):
                raise AttrError('bad_attr_name', f"invalid name: {field}")
            return field, 'set'


def _is_posix_class_valid(name):
    """Check if POSIX class name is valid."""
    return name in ('alpha', 'digit', 'alnum', 'space', 'upper', 'lower', 'punct', 'xdigit')


def _match_posix_class(c, name):
    """Check if character matches POSIX class."""
    if name == 'alpha':
        return _is_letter(c)
    elif name == 'digit':
        return _is_digit(c)
    elif name == 'alnum':
        return _is_alnum(c)
    elif name == 'space':
        return _is_space(c)
    elif name == 'upper':
        return _is_upper(c)
    elif name == 'lower':
        return _is_lower(c)
    elif name == 'punct':
        return _is_punct(c)
    elif name == 'xdigit':
        return _is_xdigit(c)
    return False


def _unescape_char(s, pos):
    """Get unescaped character at pos. If preceded by backslash, return the char after.

    Returns (char, next_pos).
    """
    if s[pos] == '\\' and pos + 1 < len(s):
        return s[pos + 1], pos + 2
    return s[pos], pos + 1


def _validate_and_parse_bracket_class(pattern, start_pos):
    """Parse and validate bracket class starting at start_pos (at '[').

    Returns (members_list, negated, next_pos) or raises AttrError.
    members_list is list of (type, value) tuples:
    - ('char', c)
    - ('range', (c1, c2))
    - ('posix', name)
    """
    pos = start_pos + 1  # skip '['

    if pos >= len(pattern):
        raise AttrError('unterminated_class', "bracket class never closed")

    negated = False
    if pattern[pos] in '!^':
        negated = True
        pos += 1

    members = []

    # First ] is literal if it's the first member character
    if pos < len(pattern) and pattern[pos] == ']':
        members.append(('char', ']'))
        pos += 1

    while pos < len(pattern):
        if pattern[pos] == ']':
            # Found closing ]
            return members, negated, pos + 1

        if pattern[pos] == '[' and pos + 1 < len(pattern) and pattern[pos + 1] == ':':
            # Try to parse POSIX class
            posix_start = pos + 2
            posix_end = pattern.find(':]', posix_start)
            if posix_end == -1:
                raise AttrError('bad_posix_class', "unterminated POSIX class")
            posix_name = pattern[posix_start:posix_end]
            if not _is_posix_class_valid(posix_name):
                raise AttrError('bad_posix_class', f"invalid POSIX class: {posix_name}")
            members.append(('posix', posix_name))
            pos = posix_end + 2
        else:
            # Regular member (possibly with range)
            if pattern[pos] == '\\':
                if pos + 1 >= len(pattern):
                    raise AttrError('trailing_backslash', "backslash at end of segment")
                c, pos = _unescape_char(pattern, pos)
            else:
                c = pattern[pos]
                pos += 1

            # Check for range
            if pos < len(pattern) and pattern[pos] == '-':
                if not _is_escaped(pattern, pos):
                    # Look ahead to see if this is a range
                    if pos + 1 < len(pattern) and pattern[pos + 1] != ']':
                        # This is a range
                        pos += 1  # skip '-'
                        if pattern[pos] == '\\':
                            if pos + 1 >= len(pattern):
                                raise AttrError('trailing_backslash', "backslash at end of segment")
                            c2, pos = _unescape_char(pattern, pos)
                        else:
                            c2 = pattern[pos]
                            pos += 1
                        members.append(('range', (c, c2)))
                    else:
                        # '-' is at end or before ']', it's a literal
                        members.append(('char', c))
                        # Don't consume the '-'
                else:
                    # Escaped '-', just a literal
                    members.append(('char', c))
            else:
                members.append(('char', c))

    raise AttrError('unterminated_class', "bracket class never closed")


def _validate_segment(segment):
    """Validate a pattern segment. Returns None or raises AttrError.

    This checks for:
    - trailing_backslash
    - unterminated_class
    - bad_posix_class
    """
    pos = 0
    while pos < len(segment):
        if segment[pos] == '\\':
            if pos + 1 >= len(segment):
                raise AttrError('trailing_backslash', "backslash at end of segment")
            pos += 2
        elif segment[pos] == '[':
            # Parse bracket class to validate it
            members, negated, new_pos = _validate_and_parse_bracket_class(segment, pos)
            pos = new_pos
        else:
            pos += 1


def _validate_pattern(pattern):
    """Validate pattern. Raises AttrError if invalid."""
    if not pattern:
        raise AttrError('empty_pattern', "pattern is empty")

    # Check for trailing unescaped /
    if pattern[-1] == '/' and not _is_escaped(pattern, len(pattern) - 1):
        raise AttrError('trailing_slash', "pattern ends with unescaped /")

    # Check if anchored
    anchored = False
    if pattern[0] == '/' and not _is_escaped(pattern, 0):
        anchored = True
        # Remove leading /s
        pattern = pattern.lstrip('/')
        if not pattern:
            raise AttrError('empty_pattern', "pattern is only /")
    else:
        # Check if contains unescaped /
        for i, c in enumerate(pattern):
            if c == '/' and not _is_escaped(pattern, i):
                anchored = True
                break

    # Validate all segments
    if anchored:
        segments = []
        current = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '/' and not _is_escaped(pattern, i):
                segments.append(''.join(current))
                current = []
                i += 1
            else:
                current.append(pattern[i])
                i += 1
        segments.append(''.join(current))

        for seg in segments:
            if seg:  # Empty segments are OK (they match nothing)
                _validate_segment(seg)
    else:
        _validate_segment(pattern)


def _segment_matches_component(segment, component):
    """Check if segment pattern matches a single component."""
    if segment == '**':
        # Special: ** matches everything when unanchored
        return True

    return _match_segment_chars(segment, component, 0, 0)


def _match_segment_chars(segment, component, seg_pos, comp_pos):
    """Recursively match segment pattern against component string."""
    # End of both?
    if seg_pos >= len(segment) and comp_pos >= len(component):
        return True

    # Segment exhausted but component remains?
    if seg_pos >= len(segment):
        return False

    # Look at segment char
    if segment[seg_pos] == '\\' and seg_pos + 1 < len(segment):
        # Escaped character - must match literally
        escape_char = segment[seg_pos + 1]
        if comp_pos < len(component) and component[comp_pos] == escape_char:
            return _match_segment_chars(segment, component, seg_pos + 2, comp_pos + 1)
        return False
    elif segment[seg_pos] == '*':
        # Match zero or more characters
        # Try matching zero chars
        if _match_segment_chars(segment, component, seg_pos + 1, comp_pos):
            return True
        # Try matching one or more chars
        if comp_pos < len(component):
            if _match_segment_chars(segment, component, seg_pos + 1, comp_pos + 1):
                return True
            # Greedy: keep consuming component
            if _match_segment_chars(segment, component, seg_pos, comp_pos + 1):
                return True
        return False
    elif segment[seg_pos] == '?':
        # Match exactly one character
        if comp_pos < len(component):
            return _match_segment_chars(segment, component, seg_pos + 1, comp_pos + 1)
        return False
    elif segment[seg_pos] == '[':
        # Bracket class
        members, negated, bracket_end = _validate_and_parse_bracket_class(segment, seg_pos)
        if comp_pos >= len(component):
            return False
        c = component[comp_pos]

        # Check if c matches class
        matched = False
        for member_type, member_value in members:
            if member_type == 'char':
                if c == member_value:
                    matched = True
                    break
            elif member_type == 'range':
                c1, c2 = member_value
                # Check if c is in range (c1 <= c <= c2)
                if ord(c1) <= ord(c) <= ord(c2):
                    matched = True
                    break
            elif member_type == 'posix':
                if _match_posix_class(c, member_value):
                    matched = True
                    break

        if negated:
            matched = not matched

        if matched:
            return _match_segment_chars(segment, component, bracket_end, comp_pos + 1)
        return False
    else:
        # Literal character
        if comp_pos < len(component) and component[comp_pos] == segment[seg_pos]:
            return _match_segment_chars(segment, component, seg_pos + 1, comp_pos + 1)
        return False


def _match_posix_class(c, name):
    """Check if character matches POSIX class (defined earlier too)."""
    if name == 'alpha':
        return _is_letter(c)
    elif name == 'digit':
        return _is_digit(c)
    elif name == 'alnum':
        return _is_alnum(c)
    elif name == 'space':
        return _is_space(c)
    elif name == 'upper':
        return _is_upper(c)
    elif name == 'lower':
        return _is_lower(c)
    elif name == 'punct':
        return _is_punct(c)
    elif name == 'xdigit':
        return _is_xdigit(c)
    return False


def _pattern_matches_path(pattern_str, path):
    """Check if pattern matches path."""
    # Determine if anchored
    if pattern_str[0] == '/' and not _is_escaped(pattern_str, 0):
        anchored = True
        pattern = pattern_str.lstrip('/')
    else:
        # Check for unescaped /
        anchored = False
        for i, c in enumerate(pattern_str):
            if c == '/' and not _is_escaped(pattern_str, i):
                anchored = True
                break
        pattern = pattern_str

    path_components = path.split('/')

    if anchored:
        # Split pattern on unescaped /
        segments = []
        current = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '/' and not _is_escaped(pattern, i):
                segments.append(''.join(current))
                current = []
                i += 1
            else:
                current.append(pattern[i])
                i += 1
        segments.append(''.join(current))

        return _match_anchored(segments, path_components, 0, 0)
    else:
        # Unanchored: match against last component only
        if not path_components:
            return False
        last_component = path_components[-1]
        return _segment_matches_component(pattern, last_component)


def _match_anchored(segments, components, seg_idx, comp_idx):
    """Match anchored pattern segments against path components."""
    # If we've consumed all segments, we must have consumed all components
    if seg_idx >= len(segments):
        return comp_idx >= len(components)

    seg = segments[seg_idx]

    if seg == '**':
        # ** matches zero or more components
        # Try matching zero components
        if _match_anchored(segments, components, seg_idx + 1, comp_idx):
            return True
        # Try matching one or more components
        if comp_idx < len(components):
            if _match_anchored(segments, components, seg_idx, comp_idx + 1):
                return True
        return False
    else:
        # Regular segment: must match exactly one component
        if comp_idx >= len(components):
            return False
        if _segment_matches_component(seg, components[comp_idx]):
            return _match_anchored(segments, components, seg_idx + 1, comp_idx + 1)
        return False


class _CompiledAttrs:
    """Internal representation of compiled attributes."""
    def __init__(self):
        self.rules = []  # List of (pattern_str, attr_fields)
        self.macros = {}  # name -> attr_fields


def compile_attrs(lines):
    """Compile gitattributes lines.

    Args:
        lines: iterable of strings (lines without trailing newline)

    Returns:
        compiled object for use with check_attrs

    Raises:
        AttrError if any line is invalid
    """
    compiled = _CompiledAttrs()
    line_list = []

    # First pass: read all lines
    for line in lines:
        line_list.append(line)

    # Process each line
    for line_idx, line in enumerate(line_list):
        # Step 1: strip trailing unescaped whitespace
        line = _strip_trailing_unescaped_whitespace(line)

        # Step 2: skip empty lines
        if not line:
            continue

        # Step 3: skip comments
        if line[0] == '#':
            continue

        # Step 4: check if macro definition
        is_macro = line.startswith('[attr]')

        if is_macro:
            # Macro definition line
            # Extract macro name and attributes
            if len(line) == 6:  # Just "[attr]"
                raise AttrError('bad_macro_name', "missing macro name")

            macro_header = '[attr]'
            rest = line[6:]  # Skip "[attr]"

            # Macro name is the first field
            pattern, attr_fields = _split_pattern_and_attrs(rest)
            macro_name = pattern

            if not macro_name:
                raise AttrError('bad_macro_name', "empty macro name")

            if not _validate_name(macro_name):
                raise AttrError('bad_macro_name', f"invalid macro name: {macro_name}")

            if not attr_fields:
                raise AttrError('no_attrs', "macro has no attributes")

            if macro_name in compiled.macros:
                raise AttrError('duplicate_macro', f"macro {macro_name} defined twice")

            # Parse attribute fields
            parsed_attrs = []
            for field in attr_fields:
                name, value_form = _parse_attr_field(field)
                parsed_attrs.append((name, value_form))

            compiled.macros[macro_name] = parsed_attrs
        else:
            # Rule line
            pattern_str, attr_fields = _split_pattern_and_attrs(line)

            # Validate pattern (step 4a-c in order)
            _validate_pattern(pattern_str)

            # Check for attribute fields (step 4d)
            if not attr_fields:
                raise AttrError('no_attrs', "rule has no attributes")

            # Parse attribute fields (step 4e)
            parsed_attrs = []
            for field in attr_fields:
                name, value_form = _parse_attr_field(field)
                parsed_attrs.append((name, value_form))

            compiled.rules.append((pattern_str, parsed_attrs))

    # After parsing all lines, check for macro cycles
    _check_macro_cycles(compiled.macros)

    return compiled


def _check_macro_cycles(macros):
    """Check for macro reference cycles.

    Raises AttrError if a cycle is found.
    """
    # Build dependency graph
    def get_referenced_macros(attrs):
        """Get all macro names referenced in attribute fields."""
        refs = set()
        for name, value_form in attrs:
            refs.add(name)
        return refs

    # Check each macro for cycles
    for start_name in macros:
        visited = set()
        rec_stack = set()

        def has_cycle(name):
            if name not in macros:
                return False
            if name in rec_stack:
                return True
            if name in visited:
                return False

            visited.add(name)
            rec_stack.add(name)

            refs = get_referenced_macros(macros[name])
            for ref in refs:
                if ref in macros and has_cycle(ref):
                    return True

            rec_stack.remove(name)
            return False

        if has_cycle(start_name):
            raise AttrError('macro_cycle', f"macro {start_name} has a cycle")


def check_attrs(path, compiled):
    """Check attributes for a path.

    Args:
        path: string path to check
        compiled: compiled object from compile_attrs

    Returns:
        dict mapping attribute names to their resolved values
    """
    result = {}

    # Walk rules in order
    for pattern_str, attr_fields in compiled.rules:
        if _pattern_matches_path(pattern_str, path):
            # Apply attribute fields
            for name, value_form in attr_fields:
                result = _apply_attr_field(name, value_form, result, compiled.macros)

    return result


def _apply_attr_field(name, value_form, result, macros):
    """Apply one attribute field to result dict.

    Returns updated result dict.
    """
    if value_form == 'set':
        result[name] = True
        # Expand macro if applicable
        if name in macros:
            for macro_name, macro_value_form in macros[name]:
                result = _apply_attr_field(macro_name, macro_value_form, result, macros)
    elif value_form == 'unset':
        result[name] = False
    elif value_form == 'unspec':
        result[name] = None
    else:
        # It's a valued form
        result[name] = value_form

    return result
