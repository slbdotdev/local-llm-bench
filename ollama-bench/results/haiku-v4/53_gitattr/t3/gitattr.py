"""Gitattributes-style resolver: maps paths to attribute sets."""


class AttrError(ValueError):
    """Exception raised for invalid gitattributes lines."""

    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


def compile_attrs(lines):
    """
    Compile lines from a gitattributes file.

    Args:
        lines: An iterable of strings (no trailing newlines)

    Returns:
        An opaque compiled object for use with check_attrs

    Raises:
        AttrError: If any line is invalid
    """
    rules = []
    macros = {}

    # Convert to list to allow multiple passes if needed
    lines_list = list(lines)

    for line in lines_list:
        # Step 1: Strip trailing whitespace (unescaped only)
        while line and line[-1] in (' ', '\t'):
            # Count preceding backslashes
            backslash_count = 0
            i = len(line) - 2
            while i >= 0 and line[i] == '\\':
                backslash_count += 1
                i -= 1
            # If even number of backslashes, this whitespace is unescaped
            if backslash_count % 2 == 0:
                line = line[:-1]
            else:
                break

        # Step 2: Skip empty lines
        if not line:
            continue

        # Step 3: Skip comments (line starting with #)
        if line[0] == '#':
            continue

        # Step 4: Check if it's a macro definition
        if line.startswith('[attr]'):
            # Parse as macro definition
            _parse_macro_line(line, macros)
        else:
            # Parse as rule line
            _parse_rule_line(line, rules)

    # Check for macro cycles
    _check_macro_cycles(macros)

    return {'rules': rules, 'macros': macros}


def _parse_macro_line(line, macros):
    """Parse a macro definition line."""
    # Line starts with [attr]
    rest = line[6:]  # After "[attr]"

    # Find the macro name (first word of rest)
    macro_name, attrs_str = _split_first_field(rest)

    # Step a: Check macro name validity
    if not macro_name or not _is_valid_name(macro_name):
        raise AttrError('bad_macro_name')

    # Parse attribute fields
    attr_fields = _parse_attr_fields(attrs_str)

    # Step b: Check for zero attribute fields
    if not attr_fields:
        raise AttrError('no_attrs')

    # Step c: Check for duplicate macro name
    if macro_name in macros:
        raise AttrError('duplicate_macro')

    # Step d: Validate attribute fields
    for field in attr_fields:
        _validate_attr_field(field)

    # Store the macro
    macros[macro_name] = attr_fields


def _parse_rule_line(line, rules):
    """Parse a rule line."""
    # Split into pattern and attributes
    pattern, attrs_str = _split_first_field(line)

    # Step a: Check for empty pattern
    if not pattern:
        raise AttrError('empty_pattern')

    # Step b: Check for trailing slash
    if pattern and pattern[-1] == '/' and not _is_escaped(pattern, len(pattern) - 1):
        raise AttrError('trailing_slash')

    # Step c: Validate pattern syntax (scan from left to right)
    _validate_pattern(pattern)

    # Parse attribute fields
    attr_fields = _parse_attr_fields(attrs_str)

    # Step d: Check for zero attribute fields
    if not attr_fields:
        raise AttrError('no_attrs')

    # Step e: Validate attribute fields
    for field in attr_fields:
        _validate_attr_field(field)

    # Store the rule
    rules.append({'pattern': pattern, 'fields': attr_fields})


def _split_first_field(line):
    """Split a line into first field and rest (attribute fields)."""
    i = 0
    while i < len(line):
        if line[i] in (' ', '\t'):
            # Check if escaped
            if not _is_escaped(line, i):
                break
        i += 1

    first_field = line[:i]
    rest = line[i:].lstrip(' \t')
    return first_field, rest


def _is_escaped(s, pos):
    """Check if character at pos is escaped (preceded by odd number of backslashes)."""
    if pos == 0:
        return False
    backslash_count = 0
    i = pos - 1
    while i >= 0 and s[i] == '\\':
        backslash_count += 1
        i -= 1
    return backslash_count % 2 == 1


def _is_valid_name(name):
    """Check if a name is valid (ASCII letter or _, followed by letter/digit/-/_/.)."""
    if not name:
        return False
    # First character: ASCII letter or _
    c = name[0]
    if not ((ord('A') <= ord(c) <= ord('Z')) or (ord('a') <= ord(c) <= ord('z')) or c == '_'):
        return False
    # Rest: ASCII letter, digit, -, _, or .
    for c in name[1:]:
        is_letter = (ord('A') <= ord(c) <= ord('Z')) or (ord('a') <= ord(c) <= ord('z'))
        is_digit = ord('0') <= ord(c) <= ord('9')
        is_special = c in ('-', '_', '.')
        if not (is_letter or is_digit or is_special):
            return False
    return True


def _parse_attr_fields(attrs_str):
    """Parse attribute fields from a string."""
    fields = []
    current = []
    i = 0
    while i < len(attrs_str):
        c = attrs_str[i]
        if c in (' ', '\t'):
            if current:
                fields.append(''.join(current))
                current = []
        else:
            current.append(c)
        i += 1
    if current:
        fields.append(''.join(current))
    return fields


def _validate_attr_field(field):
    """Validate an attribute field and raise AttrError if invalid."""
    if not field:
        raise AttrError('bad_attr_name')

    # Check the four valid forms
    if field[0] == '-':
        # Form: -name
        name = field[1:]
        if not name or not _is_valid_name(name):
            raise AttrError('bad_attr_name')
        # Check for -name=value (invalid)
        if '=' in field:
            raise AttrError('bad_attr_name')
    elif field[0] == '!':
        # Form: !name
        name = field[1:]
        if not name or not _is_valid_name(name):
            raise AttrError('bad_attr_name')
        # Check for !name=value (invalid)
        if '=' in field:
            raise AttrError('bad_attr_name')
    elif '=' in field:
        # Form: name=value
        eq_idx = field.index('=')
        name = field[:eq_idx]
        if not name or not _is_valid_name(name):
            raise AttrError('bad_attr_name')
    else:
        # Form: name
        if not _is_valid_name(field):
            raise AttrError('bad_attr_name')


def _validate_pattern(pattern):
    """Validate pattern syntax. Raises AttrError for syntax errors."""
    # This validates: trailing_backslash, unterminated_class, bad_posix_class
    # Check for trailing backslash first (at the very end of pattern)
    if pattern and pattern[-1] == '\\':
        # Check if this backslash is escaped
        if not _is_escaped(pattern, len(pattern) - 1):
            # The very last character is an unescaped backslash
            raise AttrError('trailing_backslash')

    i = 0

    while i < len(pattern):
        # Handle escaped characters in segment
        if pattern[i] == '\\':
            if i + 1 >= len(pattern):
                # Trailing backslash (shouldn't reach here due to check above)
                raise AttrError('trailing_backslash')
            # Skip the escaped character
            i += 2
            continue

        # Handle unescaped /
        if pattern[i] == '/':
            i += 1
            continue

        # Handle bracket class
        if pattern[i] == '[':
            _validate_bracket_class(pattern, i)
            # Find the end of the class
            i = _find_bracket_class_end(pattern, i)
            if i == -1:
                raise AttrError('unterminated_class')
            i += 1  # Move past the ]
            continue

        i += 1


def _validate_bracket_class(pattern, start_pos):
    """Validate a bracket class starting at start_pos."""
    i = start_pos + 1  # Skip [

    if i >= len(pattern):
        raise AttrError('unterminated_class')

    # Check for negation
    if pattern[i] in ('!', '^'):
        i += 1

    if i >= len(pattern):
        raise AttrError('unterminated_class')

    # Special case: ] as first member character
    if pattern[i] == ']':
        i += 1

    # Scan through class members
    while i < len(pattern):
        if pattern[i] == '\\':
            # Escaped character
            if i + 1 >= len(pattern):
                raise AttrError('trailing_backslash')
            i += 2
            continue

        if pattern[i] == ']':
            # End of class found
            return

        # Check for POSIX class
        if pattern[i] == ':':
            # Could be end of POSIX class - handled elsewhere
            i += 1
            continue

        if pattern[i] == '[' and i + 1 < len(pattern) and pattern[i + 1] == ':':
            # Start of POSIX class
            _validate_posix_class(pattern, i)
            i += 2  # Skip [: and move forward
            # Find the closing :]
            end = pattern.find(':]', i)
            if end == -1:
                raise AttrError('bad_posix_class')
            posix_name = pattern[i:end]
            if posix_name not in ('alpha', 'digit', 'alnum', 'space', 'upper', 'lower', 'punct', 'xdigit'):
                raise AttrError('bad_posix_class')
            i = end + 2  # Move past :]
            continue

        # Regular character
        i += 1


def _validate_posix_class(pattern, pos):
    """Check if there's a valid POSIX class starting at pos."""
    # Pattern at pos should be '[:'
    i = pos + 2
    # Find the closing :]
    while i < len(pattern):
        if pattern[i] == ':' and i + 1 < len(pattern) and pattern[i + 1] == ']':
            # Found closing :]
            posix_name = pattern[pos + 2:i]
            if posix_name not in ('alpha', 'digit', 'alnum', 'space', 'upper', 'lower', 'punct', 'xdigit'):
                raise AttrError('bad_posix_class')
            return
        i += 1
    # No closing :] found
    raise AttrError('bad_posix_class')


def _find_bracket_class_end(pattern, start_pos):
    """Find the end of a bracket class, returning the index of ] or -1 if unterminated."""
    i = start_pos + 1

    if i >= len(pattern):
        return -1

    # Check for negation
    if pattern[i] in ('!', '^'):
        i += 1

    if i >= len(pattern):
        return -1

    # Special case: ] as first member
    if pattern[i] == ']':
        i += 1

    # Scan through members
    while i < len(pattern):
        if pattern[i] == '\\':
            if i + 1 >= len(pattern):
                return -1
            i += 2
            continue

        if pattern[i] == ']':
            return i

        if pattern[i] == '[' and i + 1 < len(pattern) and pattern[i + 1] == ':':
            # POSIX class - find closing :]
            j = i + 2
            while j < len(pattern):
                if pattern[j] == ':' and j + 1 < len(pattern) and pattern[j + 1] == ']':
                    i = j + 2
                    break
                j += 1
            else:
                return -1
            continue

        i += 1

    return -1


def _check_macro_cycles(macros):
    """Check for macro reference cycles."""
    visited = set()
    rec_stack = set()

    def has_cycle(name):
        if name in rec_stack:
            return True
        if name in visited:
            return False

        if name not in macros:
            return False

        visited.add(name)
        rec_stack.add(name)

        fields = macros[name]
        for field in fields:
            ref_name = _extract_field_name(field)
            if ref_name and has_cycle(ref_name):
                return True

        rec_stack.remove(name)
        return False

    for macro_name in macros:
        if macro_name not in visited:
            if has_cycle(macro_name):
                raise AttrError('macro_cycle')


def _extract_field_name(field):
    """Extract the macro/attribute name from a field."""
    if field[0] == '-':
        return field[1:]
    elif field[0] == '!':
        return field[1:]
    elif '=' in field:
        return field[:field.index('=')]
    else:
        return field


def check_attrs(path, compiled):
    """
    Check attributes for a path.

    Args:
        path: A valid path string
        compiled: A compiled attributes object from compile_attrs

    Returns:
        A dict mapping attribute names to their resolved values
    """
    rules = compiled['rules']
    macros = compiled['macros']
    result = {}

    for rule in rules:
        if _pattern_matches(rule['pattern'], path):
            # Apply attributes left to right
            for field in rule['fields']:
                _apply_field(field, result, macros)

    return result


def _pattern_matches(pattern, path):
    """Check if pattern matches path."""
    # Determine if pattern is anchored
    # It's anchored if it starts with / or contains an unescaped /
    is_anchored = pattern[0] == '/' or _has_unescaped_slash(pattern)

    # Handle leading /
    if pattern[0] == '/':
        # Remove all leading /
        i = 0
        while i < len(pattern) and pattern[i] == '/':
            i += 1
        pattern = pattern[i:]
        if not pattern:
            return False

    # Split path and pattern into components
    path_components = path.split('/')

    if is_anchored:
        # Anchored: split pattern on / and match full component list
        pattern_segments = _split_pattern_on_slash(pattern)
        return _match_segments(pattern_segments, path_components)
    else:
        # Unanchored: match against last component only
        basename = path_components[-1]
        return _match_segment(pattern, basename)


def _has_unescaped_slash(pattern):
    """Check if pattern contains an unescaped /."""
    for i, char in enumerate(pattern):
        if char == '/' and not _is_escaped(pattern, i):
            return True
    return False


def _split_pattern_on_slash(pattern):
    """Split pattern on unescaped / characters."""
    segments = []
    current = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '/' and not _is_escaped(pattern, i):
            segments.append(''.join(current))
            current = []
        else:
            current.append(pattern[i])
        i += 1
    segments.append(''.join(current))
    return segments


def _match_segment(segment, component):
    """Match a single segment against a component."""
    if segment == '**':
        # Special case for unanchored **: matches anything
        return _match_glob(segment, component)
    return _match_glob(segment, component)


def _match_segments(segments, components):
    """Match segments against components."""
    return _match_segments_recursive(segments, components, 0, 0)


def _match_segments_recursive(segments, components, seg_idx, comp_idx):
    """Recursively match segments to components."""
    # Base case: both exhausted
    if seg_idx >= len(segments) and comp_idx >= len(components):
        return True

    # Mismatch: one exhausted but not the other
    if seg_idx >= len(segments) or comp_idx >= len(components):
        return False

    segment = segments[seg_idx]

    # Handle ** segment
    if segment == '**':
        # ** matches zero or more components
        # Try matching zero components
        if _match_segments_recursive(segments, components, seg_idx + 1, comp_idx):
            return True
        # Try matching one component
        if comp_idx < len(components):
            if _match_segments_recursive(segments, components, seg_idx, comp_idx + 1):
                return True
        return False

    # Handle empty segment (from //) - matches nothing
    if not segment:
        return False

    # Regular segment - match exactly one component
    if comp_idx < len(components):
        if _match_glob(segment, components[comp_idx]):
            return _match_segments_recursive(segments, components, seg_idx + 1, comp_idx + 1)

    return False


def _match_glob(pattern, text):
    """Match a glob pattern against text."""
    return _match_glob_recursive(pattern, text, 0, 0)


def _match_glob_recursive(pattern, text, p_idx, t_idx):
    """Recursively match glob pattern."""
    # Base case: pattern exhausted
    if p_idx >= len(pattern):
        # Must have consumed all text
        return t_idx >= len(text)

    p_char = pattern[p_idx]

    # Handle backslash escape
    if p_char == '\\':
        if p_idx + 1 >= len(pattern):
            # This shouldn't happen if validated properly
            return False
        # Escaped character must match literally
        next_char = pattern[p_idx + 1]
        if t_idx < len(text) and text[t_idx] == next_char:
            return _match_glob_recursive(pattern, text, p_idx + 2, t_idx + 1)
        return False

    # Handle bracket class
    if p_char == '[':
        class_end = _find_bracket_class_end_in_pattern(pattern, p_idx)
        if class_end == -1:
            # Invalid pattern (shouldn't happen if validated)
            return False

        class_content = pattern[p_idx + 1:class_end]
        if t_idx < len(text):
            if _char_in_class(text[t_idx], class_content):
                return _match_glob_recursive(pattern, text, class_end + 1, t_idx + 1)
        return False

    # Handle ?
    if p_char == '?':
        if t_idx < len(text):
            return _match_glob_recursive(pattern, text, p_idx + 1, t_idx + 1)
        return False

    # Handle *
    if p_char == '*':
        # Check if it's ** in an unanchored pattern (won't happen in segments, but check anyway)
        # Multiple * behave like single *
        # Match zero characters
        if _match_glob_recursive(pattern, text, p_idx + 1, t_idx):
            return True
        # Match one or more characters
        if t_idx < len(text):
            return _match_glob_recursive(pattern, text, p_idx, t_idx + 1)
        return False

    # Regular character - must match literally
    if t_idx < len(text) and text[t_idx] == p_char:
        return _match_glob_recursive(pattern, text, p_idx + 1, t_idx + 1)

    return False


def _find_bracket_class_end_in_pattern(pattern, start):
    """Find end of bracket class starting at start for pattern matching."""
    i = start + 1
    if i >= len(pattern):
        return -1

    if pattern[i] in ('!', '^'):
        i += 1

    if i >= len(pattern):
        return -1

    if pattern[i] == ']':
        i += 1

    while i < len(pattern):
        if pattern[i] == '\\':
            i += 2
            continue
        # Check for POSIX class start
        if pattern[i] == '[' and i + 1 < len(pattern) and pattern[i + 1] == ':':
            # Skip to closing :]
            j = i + 2
            while j < len(pattern):
                if pattern[j] == ':' and j + 1 < len(pattern) and pattern[j + 1] == ']':
                    i = j + 2
                    break
                j += 1
            else:
                # No closing :] found, continue with normal scanning
                i += 1
            continue
        if pattern[i] == ']':
            return i
        i += 1

    return -1


def _char_in_class(char, class_content):
    """Check if char matches the bracket class."""
    negated = class_content and class_content[0] in ('!', '^')
    if negated:
        class_content = class_content[1:]

    # Parse class content and check membership
    matched = _check_class_membership(char, class_content)

    if negated:
        return not matched
    return matched


def _check_class_membership(char, class_content):
    """Check if char is in the class content."""
    i = 0

    # Special case: ] as first character
    if class_content and class_content[0] == ']':
        if char == ']':
            return True
        i = 1

    while i < len(class_content):
        c = class_content[i]

        # Check for POSIX class
        if c == '[' and i + 1 < len(class_content) and class_content[i + 1] == ':':
            # Find closing :]
            j = i + 2
            while j < len(class_content):
                if class_content[j] == ':' and j + 1 < len(class_content) and class_content[j + 1] == ']':
                    posix_name = class_content[i + 2:j]
                    if _char_in_posix_class(char, posix_name):
                        return True
                    i = j + 2
                    break
                j += 1
            else:
                i += 1
            continue

        # Check for escaped character
        if c == '\\' and i + 1 < len(class_content):
            literal = class_content[i + 1]
            # Check if next is range
            if i + 2 < len(class_content) and class_content[i + 2] == '-':
                if i + 3 < len(class_content) and class_content[i + 3] != ']':
                    # It's a range
                    if i + 4 < len(class_content) and class_content[i + 3] == '\\':
                        range_end = class_content[i + 4]
                        if _in_range(char, literal, range_end):
                            return True
                        i += 5
                    else:
                        range_end = class_content[i + 3]
                        if _in_range(char, literal, range_end):
                            return True
                        i += 4
                    continue
            if char == literal:
                return True
            i += 2
            continue

        # Regular character
        # Check for range
        if i + 1 < len(class_content) and class_content[i + 1] == '-':
            if i + 2 < len(class_content) and class_content[i + 2] != ']':
                # It's a range
                if i + 3 < len(class_content) and class_content[i + 2] == '\\':
                    range_end = class_content[i + 3]
                    if _in_range(char, c, range_end):
                        return True
                    i += 4
                else:
                    range_end = class_content[i + 2]
                    if _in_range(char, c, range_end):
                        return True
                    i += 3
                continue

        if char == c:
            return True
        i += 1

    return False


def _in_range(char, start, end):
    """Check if char is in range [start, end]."""
    char_ord = ord(char)
    start_ord = ord(start)
    end_ord = ord(end)
    return start_ord <= char_ord <= end_ord


def _char_in_posix_class(char, class_name):
    """Check if char is in POSIX character class."""
    char_ord = ord(char)

    if class_name == 'alpha':
        return (ord('A') <= char_ord <= ord('Z')) or (ord('a') <= char_ord <= ord('z'))
    elif class_name == 'digit':
        return ord('0') <= char_ord <= ord('9')
    elif class_name == 'alnum':
        is_alpha = (ord('A') <= char_ord <= ord('Z')) or (ord('a') <= char_ord <= ord('z'))
        is_digit = ord('0') <= char_ord <= ord('9')
        return is_alpha or is_digit
    elif class_name == 'space':
        return char in (' ', '\t', '\n', '\v', '\f', '\r')
    elif class_name == 'upper':
        return ord('A') <= char_ord <= ord('Z')
    elif class_name == 'lower':
        return ord('a') <= char_ord <= ord('z')
    elif class_name == 'punct':
        # ASCII printable that are neither alphanumeric nor space
        # Code points 33-47, 58-64, 91-96, 123-126
        return (33 <= char_ord <= 47) or (58 <= char_ord <= 64) or (91 <= char_ord <= 96) or (123 <= char_ord <= 126)
    elif class_name == 'xdigit':
        return (ord('0') <= char_ord <= ord('9')) or (ord('a') <= char_ord <= ord('f')) or (ord('A') <= char_ord <= ord('F'))

    return False


def _apply_field(field, result, macros):
    """Apply a field to the result dict, handling macro expansion."""
    name = _extract_field_name(field)

    # Determine value
    if field[0] == '-':
        value = False
    elif field[0] == '!':
        value = None
    elif '=' in field:
        value = field[field.index('=') + 1:]
    else:
        value = True

    # Store in result
    result[name] = value

    # If value is True and name is a macro, expand
    if value is True and name in macros:
        for macro_field in macros[name]:
            _apply_field(macro_field, result, macros)
