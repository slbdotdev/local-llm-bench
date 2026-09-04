class AttrError(ValueError):
    """Exception raised for invalid gitattributes lines."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(f"Invalid gitattributes: {kind}")


def compile_attrs(lines):
    """Compile gitattributes lines into a usable object."""
    compiled = {
        'rules': [],
        'macros': {}
    }

    lines_list = list(lines)

    # First pass: collect all macro definitions and validate syntax
    for line_idx, line in enumerate(lines_list):
        original_line = line

        # Step 1: Strip trailing whitespace (respecting escapes)
        while line and _is_trailing_whitespace(line):
            line = line[:-1]

        # Step 2: Skip empty lines
        if not line:
            continue

        # Step 3: Skip comments
        if line[0] == '#':
            continue

        # Step 4: Check if it's a macro definition
        if line.startswith('[attr]'):
            # This is a macro definition
            rest = line[6:]  # Skip '[attr]'

            # Find the first space/tab to separate macro name from attributes
            split_idx = _find_first_unescaped_space_or_tab(rest)
            if split_idx == -1:
                macro_name = rest
                attr_fields = []
            else:
                macro_name = rest[:split_idx]
                attr_fields_str = rest[split_idx:]
                attr_fields = _split_attr_fields(attr_fields_str)

            # Validate macro name (section 2)
            if not _is_valid_name(macro_name):
                raise AttrError('bad_macro_name')

            # Check for at least one attribute field
            if not attr_fields:
                raise AttrError('no_attrs')

            # Check for duplicate macro
            if macro_name in compiled['macros']:
                raise AttrError('duplicate_macro')

            # Validate attribute fields
            parsed_attrs = []
            for attr_field in attr_fields:
                parsed_attr = _parse_attr_field(attr_field)
                if parsed_attr is None:
                    raise AttrError('bad_attr_name')
                parsed_attrs.append(parsed_attr)

            # Store macro
            compiled['macros'][macro_name] = parsed_attrs

    # Second pass: collect rule lines
    for line_idx, line in enumerate(lines_list):
        original_line = line

        # Step 1: Strip trailing whitespace
        while line and _is_trailing_whitespace(line):
            line = line[:-1]

        # Step 2: Skip empty lines
        if not line:
            continue

        # Step 3: Skip comments
        if line[0] == '#':
            continue

        # Step 4: Check if it's a macro definition (skip it in second pass)
        if line.startswith('[attr]'):
            continue

        # This is a rule line
        # Find first unescaped space/tab
        split_idx = _find_first_unescaped_space_or_tab(line)
        if split_idx == -1:
            pattern = line
            attr_fields_str = ''
        else:
            pattern = line[:split_idx]
            attr_fields_str = line[split_idx:]

        # Validate pattern (section 4)
        # Step 1: Check if pattern is empty
        if not pattern:
            raise AttrError('empty_pattern')

        # Step 2: Check if pattern ends with unescaped /
        if _ends_with_unescaped_slash(pattern):
            raise AttrError('trailing_slash')

        # Step 3-4: Process leading / and determine if anchored
        if pattern.startswith('/'):
            # Remove all leading /
            pattern = pattern.lstrip('/')
            if not pattern:
                raise AttrError('empty_pattern')
            anchored = True
        else:
            # Check if contains unescaped /
            anchored = _contains_unescaped_slash(pattern)

        # Validate pattern segments for errors
        # (trailing_backslash, unterminated_class, bad_posix_class)
        _validate_pattern_segments(pattern)

        # Parse attribute fields
        attr_fields = _split_attr_fields(attr_fields_str)

        # Check for at least one attribute field
        if not attr_fields:
            raise AttrError('no_attrs')

        # Validate attribute fields
        parsed_attrs = []
        for attr_field in attr_fields:
            parsed_attr = _parse_attr_field(attr_field)
            if parsed_attr is None:
                raise AttrError('bad_attr_name')
            parsed_attrs.append(parsed_attr)

        # Store rule
        compiled['rules'].append({
            'pattern': pattern,
            'anchored': anchored,
            'attrs': parsed_attrs
        })

    # Check for macro cycles
    _check_macro_cycles(compiled['macros'])

    return compiled


def check_attrs(path, compiled):
    """Check attributes for a given path."""
    result = {}

    for rule in compiled['rules']:
        if _pattern_matches(path, rule['pattern'], rule['anchored']):
            for attr_name, attr_value in rule['attrs']:
                # Store the value
                if attr_name in result:
                    old_value = result[attr_name]
                else:
                    old_value = None

                result[attr_name] = attr_value

                # If this is a macro reference with value True, expand it
                if attr_name in compiled['macros'] and attr_value is True:
                    _expand_macro(attr_name, compiled['macros'], result, set())

    return result


# Helper functions

def _is_trailing_whitespace(line):
    """Check if the last character is unescaped space or tab."""
    if not line:
        return False
    last_char = line[-1]
    if last_char not in (' ', '\t'):
        return False
    # Count preceding backslashes
    num_backslashes = 0
    i = len(line) - 2
    while i >= 0 and line[i] == '\\':
        num_backslashes += 1
        i -= 1
    # If odd number of backslashes, it's escaped
    return num_backslashes % 2 == 0


def _find_first_unescaped_space_or_tab(line):
    """Find index of first unescaped space or tab, or -1."""
    i = 0
    while i < len(line):
        if line[i] == '\\':
            i += 2
        elif line[i] in (' ', '\t'):
            return i
        else:
            i += 1
    return -1


def _ends_with_unescaped_slash(pattern):
    """Check if pattern ends with unescaped /."""
    if not pattern or pattern[-1] != '/':
        return False
    # Count preceding backslashes
    num_backslashes = 0
    i = len(pattern) - 2
    while i >= 0 and pattern[i] == '\\':
        num_backslashes += 1
        i -= 1
    return num_backslashes % 2 == 0


def _contains_unescaped_slash(pattern):
    """Check if pattern contains any unescaped /."""
    i = 0
    while i < len(pattern):
        if pattern[i] == '\\':
            i += 2
        elif pattern[i] == '/':
            return True
        else:
            i += 1
    return False


def _split_attr_fields(attr_fields_str):
    """Split attribute fields on unescaped spaces/tabs."""
    fields = []
    current = []
    i = 0
    while i < len(attr_fields_str):
        ch = attr_fields_str[i]
        if ch in (' ', '\t'):
            if current:
                fields.append(''.join(current))
                current = []
            i += 1
        else:
            current.append(ch)
            i += 1
    if current:
        fields.append(''.join(current))
    return fields


def _is_valid_name(name):
    """Check if name is valid (starts with letter or _, rest alphanumeric/dash/underscore/dot)."""
    if not name:
        return False
    first = name[0]
    if not _is_ascii_letter(first) and first != '_':
        return False
    for ch in name[1:]:
        if not (_is_ascii_letter(ch) or _is_ascii_digit(ch) or ch in ('-', '_', '.')):
            return False
    return True


def _is_ascii_letter(ch):
    """Check if character is ASCII letter."""
    return ('A' <= ch <= 'Z') or ('a' <= ch <= 'z')


def _is_ascii_digit(ch):
    """Check if character is ASCII digit."""
    return '0' <= ch <= '9'


def _is_ascii_space(ch):
    """Check if character is ASCII space (space, tab, newline, etc)."""
    return ch in (' ', '\t', '\n', '\v', '\f', '\r')


def _is_ascii_upper(ch):
    """Check if character is ASCII uppercase."""
    return 'A' <= ch <= 'Z'


def _is_ascii_lower(ch):
    """Check if character is ASCII lowercase."""
    return 'a' <= ch <= 'z'


def _is_ascii_alnum(ch):
    """Check if character is ASCII alphanumeric."""
    return _is_ascii_letter(ch) or _is_ascii_digit(ch)


def _is_ascii_punct(ch):
    """Check if character is ASCII punctuation."""
    code = ord(ch)
    return code in range(33, 48) or code in range(58, 65) or code in range(91, 97) or code in range(123, 127)


def _is_ascii_xdigit(ch):
    """Check if character is ASCII hex digit."""
    return _is_ascii_digit(ch) or ('a' <= ch <= 'f') or ('A' <= ch <= 'F')


def _parse_attr_field(field):
    """Parse an attribute field. Returns (name, value) or None."""
    if not field:
        return None

    first = field[0]
    if first == '-':
        # Unset form: -name
        if '=' in field:
            return None  # Invalid: -name=v
        name = field[1:]
        if not _is_valid_name(name):
            return None
        return (name, False)
    elif first == '!':
        # Unspecified form: !name
        if '=' in field:
            return None  # Invalid: !name=v
        name = field[1:]
        if not _is_valid_name(name):
            return None
        return (name, None)
    else:
        # Set or value form: name or name=value
        if '=' in field:
            eq_idx = field.index('=')
            name = field[:eq_idx]
            value = field[eq_idx + 1:]
            if not _is_valid_name(name):
                return None
            return (name, value)
        else:
            name = field
            if not _is_valid_name(name):
                return None
            return (name, True)


def _validate_pattern_segments(pattern):
    """Validate pattern for trailing_backslash, unterminated_class, bad_posix_class."""
    i = 0
    while i < len(pattern):
        if pattern[i] == '\\':
            # Check if it's the last character
            if i == len(pattern) - 1:
                raise AttrError('trailing_backslash')
            i += 2
        elif pattern[i] == '[':
            # Parse bracket class
            _validate_bracket_class(pattern, i)
            # Find the end of the bracket class
            j = i + 1
            if j < len(pattern) and pattern[j] in ('!', '^'):
                j += 1
            # Check for first ] being a literal member
            if j < len(pattern) and pattern[j] == ']':
                j += 1
            # Now find the closing ]
            while j < len(pattern):
                if pattern[j] == '\\':
                    if j == len(pattern) - 1:
                        raise AttrError('trailing_backslash')
                    j += 2
                elif pattern[j] == ']':
                    j += 1
                    break
                else:
                    j += 1
            if j > len(pattern):
                # Didn't find closing ]
                raise AttrError('unterminated_class')
            i = j
        elif pattern[i] == '/':
            i += 1
        else:
            i += 1


def _validate_bracket_class(pattern, start_idx):
    """Validate a bracket class starting at start_idx."""
    i = start_idx + 1

    # Skip negation marker
    if i < len(pattern) and pattern[i] in ('!', '^'):
        i += 1

    # Must have at least one member
    if i >= len(pattern):
        raise AttrError('unterminated_class')

    # Check for first ] being a literal member
    if pattern[i] == ']':
        i += 1

    # Now parse members
    while i < len(pattern):
        if pattern[i] == '\\':
            if i == len(pattern) - 1:
                raise AttrError('trailing_backslash')
            i += 2
        elif pattern[i] == ']':
            # End of class
            return
        elif pattern[i] == '[' and i + 1 < len(pattern) and pattern[i + 1] == ':':
            # POSIX class
            i += 2
            # Find the closing :]
            posix_start = i
            while i < len(pattern):
                if pattern[i] == ']' and i > posix_start and pattern[i - 1] == ':':
                    break
                i += 1
            if i >= len(pattern) or pattern[i] != ']':
                raise AttrError('bad_posix_class')
            # Extract the POSIX class name
            posix_name = pattern[posix_start:i-1]
            if posix_name not in ('alpha', 'digit', 'alnum', 'space', 'upper', 'lower', 'punct', 'xdigit'):
                raise AttrError('bad_posix_class')
            i += 1
        else:
            i += 1

    # If we get here, class was unterminated
    raise AttrError('unterminated_class')


def _split_pattern_segments(pattern):
    """Split pattern by unescaped / into segments."""
    segments = []
    current = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '\\':
            current.append(pattern[i])
            if i + 1 < len(pattern):
                current.append(pattern[i + 1])
            i += 2
        elif pattern[i] == '/':
            segments.append(''.join(current))
            current = []
            i += 1
        else:
            current.append(pattern[i])
            i += 1
    if current or not pattern or pattern[-1] == '/':
        segments.append(''.join(current))
    return segments


def _pattern_matches(path, pattern, anchored):
    """Check if a path matches a pattern."""
    path_components = path.split('/')

    if anchored:
        # Split pattern by unescaped /
        segments = _split_pattern_segments(pattern)
        return _match_anchored(path_components, segments)
    else:
        # Single segment, match against basename
        return _match_unanchored(path_components[-1], pattern)


def _match_anchored(components, segments):
    """Match path components against pattern segments (anchored)."""
    return _match_segments(components, segments, 0, 0)


def _match_segments(components, segments, comp_idx, seg_idx):
    """Recursively match components against segments."""
    if seg_idx >= len(segments):
        # All segments matched
        return comp_idx >= len(components)

    segment = segments[seg_idx]

    if segment == '**':
        # Match zero or more components
        # Try matching zero components first, then one, two, etc.
        if _match_segments(components, segments, comp_idx, seg_idx + 1):
            return True
        if comp_idx < len(components):
            return _match_segments(components, segments, comp_idx + 1, seg_idx)
        return False
    elif segment == '':
        # Empty segment matches nothing
        return False
    else:
        # Match single component
        if comp_idx >= len(components):
            return False
        if _segment_matches_component(segment, components[comp_idx]):
            return _match_segments(components, segments, comp_idx + 1, seg_idx + 1)
        return False


def _match_unanchored(basename, pattern):
    """Match basename against unanchored pattern (single segment)."""
    return _segment_matches_component(pattern, basename)


def _segment_matches_component(segment, component):
    """Check if a segment pattern matches a component."""
    return _match_glob(segment, component, 0, 0)


def _match_glob(pattern, text, pat_idx, text_idx):
    """Recursive glob matching."""
    if pat_idx >= len(pattern):
        return text_idx >= len(text)

    if pattern[pat_idx] == '\\':
        # Escaped character
        if pat_idx + 1 >= len(pattern):
            return False
        escaped_char = pattern[pat_idx + 1]
        if text_idx >= len(text) or text[text_idx] != escaped_char:
            return False
        return _match_glob(pattern, text, pat_idx + 2, text_idx + 1)
    elif pattern[pat_idx] == '*':
        # Check if it's ** (but in unanchored, ** is just *)
        # Match zero or more characters
        # Try matching zero first
        if _match_glob(pattern, text, pat_idx + 1, text_idx):
            return True
        if text_idx >= len(text):
            return False
        return _match_glob(pattern, text, pat_idx, text_idx + 1)
    elif pattern[pat_idx] == '?':
        # Match exactly one character
        if text_idx >= len(text):
            return False
        return _match_glob(pattern, text, pat_idx + 1, text_idx + 1)
    elif pattern[pat_idx] == '[':
        # Bracket class
        if text_idx >= len(text):
            return False
        # Parse the bracket class
        negated, end_idx, matches = _parse_bracket_class_for_matching(pattern, pat_idx)
        if end_idx == -1:
            # Invalid bracket class
            return False
        if _char_in_bracket_class(text[text_idx], negated, matches):
            return _match_glob(pattern, text, end_idx, text_idx + 1)
        return False
    else:
        # Literal character
        if text_idx >= len(text) or text[text_idx] != pattern[pat_idx]:
            return False
        return _match_glob(pattern, text, pat_idx + 1, text_idx + 1)


def _parse_bracket_class_for_matching(pattern, start_idx):
    """Parse a bracket class for matching. Returns (negated, end_idx, members)."""
    i = start_idx + 1

    negated = False
    if i < len(pattern) and pattern[i] in ('!', '^'):
        negated = True
        i += 1

    # Check for ] as first member
    members = []
    posix_classes = []
    if i < len(pattern) and pattern[i] == ']':
        members.append(']')
        i += 1

    # Parse members
    while i < len(pattern):
        if pattern[i] == '\\':
            if i + 1 < len(pattern):
                members.append(pattern[i + 1])
                i += 2
            else:
                return (negated, -1, members)
        elif pattern[i] == ']':
            return (negated, i + 1, (members, posix_classes))
        elif pattern[i] == '[' and i + 1 < len(pattern) and pattern[i + 1] == ':':
            # POSIX class
            i += 2
            posix_start = i
            while i < len(pattern):
                if pattern[i] == ':' and i + 1 < len(pattern) and pattern[i + 1] == ']':
                    posix_name = pattern[posix_start:i]
                    posix_classes.append(posix_name)
                    i += 2
                    break
                i += 1
        else:
            # Regular member or range
            member_char = pattern[i]
            i += 1
            # Check for range
            if i < len(pattern) and pattern[i] == '-' and i + 1 < len(pattern) and pattern[i + 1] != ']':
                # This is a range
                i += 1
                if pattern[i] == '\\' and i + 1 < len(pattern):
                    end_char = pattern[i + 1]
                    i += 2
                else:
                    end_char = pattern[i]
                    i += 1
                # Store range as tuple
                members.append((member_char, end_char))
            else:
                members.append(member_char)

    return (negated, -1, (members, posix_classes))


def _char_in_bracket_class(ch, negated, members_tuple):
    """Check if character is in bracket class."""
    members, posix_classes = members_tuple

    # Check POSIX classes
    for posix_name in posix_classes:
        if _char_in_posix_class(ch, posix_name):
            return not negated

    # Check literal members and ranges
    for member in members:
        if isinstance(member, tuple):
            # Range
            start, end = member
            if ord(start) <= ord(ch) <= ord(end):
                return not negated
        else:
            if ch == member:
                return not negated

    return negated


def _char_in_posix_class(ch, class_name):
    """Check if character is in POSIX class."""
    if class_name == 'alpha':
        return _is_ascii_letter(ch)
    elif class_name == 'digit':
        return _is_ascii_digit(ch)
    elif class_name == 'alnum':
        return _is_ascii_alnum(ch)
    elif class_name == 'space':
        return _is_ascii_space(ch)
    elif class_name == 'upper':
        return _is_ascii_upper(ch)
    elif class_name == 'lower':
        return _is_ascii_lower(ch)
    elif class_name == 'punct':
        return _is_ascii_punct(ch)
    elif class_name == 'xdigit':
        return _is_ascii_xdigit(ch)
    return False


def _expand_macro(macro_name, macros, result, seen):
    """Recursively expand a macro."""
    if macro_name in seen:
        # Cycle detected (shouldn't happen if _check_macro_cycles works)
        return
    seen.add(macro_name)

    if macro_name not in macros:
        return

    for attr_name, attr_value in macros[macro_name]:
        result[attr_name] = attr_value
        # Recursively expand if it's a macro reference with True value
        if attr_name in macros and attr_value is True:
            _expand_macro(attr_name, macros, result, seen.copy())


def _check_macro_cycles(macros):
    """Check for macro definition cycles."""
    for macro_name in macros:
        visited = set()
        if _has_cycle(macro_name, macros, visited):
            raise AttrError('macro_cycle')


def _has_cycle(macro_name, macros, visited):
    """Check if a macro has a cycle."""
    if macro_name in visited:
        return True
    if macro_name not in macros:
        return False

    visited.add(macro_name)
    for attr_name, attr_value in macros[macro_name]:
        # Only check if this is a macro reference (appears in macros dict)
        if attr_name in macros:
            if _has_cycle(attr_name, macros, visited.copy()):
                return True
    return False
