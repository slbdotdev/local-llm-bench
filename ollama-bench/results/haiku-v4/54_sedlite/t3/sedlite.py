import re

class ScriptError(ValueError):
    """Exception for sed script syntax errors."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


def run(script, text, quiet=False):
    """Execute a sed-like script on the given text."""

    # Parse input lines
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()

    # Parse script to get commands
    commands = parse_script(script)

    # Execute commands
    output_chunks = []
    append_queue = []

    for cmd_idx, cmd in enumerate(commands):
        cmd['range_state'] = 'inactive'
        cmd['range_start'] = None

    for line_num, line in enumerate(lines, 1):
        pattern_space = line
        append_queue = []

        # Process each command for this line
        for cmd_idx, cmd in enumerate(commands):
            # Determine if command applies
            applies = should_apply(cmd, line_num, pattern_space, len(lines), commands[cmd_idx])

            if applies:
                if cmd['cmd'] == 's':
                    pattern_space, was_replaced = cmd_substitute(cmd, pattern_space)
                    if was_replaced and cmd['flags']['print']:
                        output_chunks.append(pattern_space)
                elif cmd['cmd'] == 'y':
                    pattern_space = cmd_transliterate(cmd, pattern_space)
                elif cmd['cmd'] == 'd':
                    # Delete: end cycle, skip auto-print
                    pattern_space = None
                    break
                elif cmd['cmd'] == 'p':
                    output_chunks.append(pattern_space)
                elif cmd['cmd'] == 'q':
                    # Emit pattern space if not quiet
                    if not quiet and pattern_space is not None:
                        output_chunks.append(pattern_space)
                    # Emit queued a text
                    output_chunks.extend(append_queue)
                    # Build and return result
                    if output_chunks:
                        return '\n'.join(output_chunks) + '\n'
                    return ''
                elif cmd['cmd'] == 'a':
                    append_queue.append(cmd['text'])
                elif cmd['cmd'] == 'i':
                    output_chunks.append(cmd['text'])

        # Auto-print if not quiet and not deleted
        if pattern_space is not None and not quiet:
            output_chunks.append(pattern_space)

        # Emit queued append text
        output_chunks.extend(append_queue)

    # Build output
    if output_chunks:
        return '\n'.join(output_chunks) + '\n'
    return ''


def parse_script(script):
    """Parse sed script and return list of commands."""
    commands = []
    pos = 0

    while pos < len(script):
        # Skip whitespace, tabs, newlines, semicolons
        while pos < len(script) and script[pos] in ' \t\n;':
            pos += 1

        if pos >= len(script):
            break

        # Handle comments
        if script[pos] == '#':
            # Skip until newline or end
            while pos < len(script) and script[pos] != '\n':
                pos += 1
            continue

        # Parse addresses
        addr1 = None
        addr2 = None

        # Try to parse first address
        addr1, pos = parse_address(script, pos, is_second=False)

        # Skip spaces/tabs
        while pos < len(script) and script[pos] in ' \t':
            pos += 1

        # Check for comma (second address)
        if pos < len(script) and script[pos] == ',':
            pos += 1
            # Skip spaces/tabs
            while pos < len(script) and script[pos] in ' \t':
                pos += 1
            addr2_start_pos = pos
            addr2, pos = parse_address(script, pos, is_second=True)
            # If comma was present but no valid second address was parsed
            if addr2 is None:
                raise ScriptError('bad_address')

        # Skip spaces/tabs
        while pos < len(script) and script[pos] in ' \t':
            pos += 1

        # Parse bang
        negated = False
        while pos < len(script) and script[pos] == '!':
            if negated:
                raise ScriptError('bad_bang')
            negated = True
            pos += 1
            # Skip spaces/tabs after bang
            while pos < len(script) and script[pos] in ' \t':
                pos += 1

        # Check for bang with no address
        if negated and addr1 is None:
            raise ScriptError('bad_bang')

        # Parse command
        if pos >= len(script):
            raise ScriptError('unknown_command')

        cmd_char = script[pos]

        if cmd_char not in 'sydpqai':
            raise ScriptError('unknown_command')

        pos += 1

        # Check for extra address on q
        if cmd_char == 'q' and addr2 is not None:
            raise ScriptError('extra_address')

        # Parse command argument
        if cmd_char == 'd':
            # No argument, just check terminator
            check_terminator(script, pos)
            commands.append({
                'cmd': 'd',
                'addr1': addr1,
                'addr2': addr2,
                'negated': negated
            })
        elif cmd_char == 'p':
            # No argument, just check terminator
            check_terminator(script, pos)
            commands.append({
                'cmd': 'p',
                'addr1': addr1,
                'addr2': addr2,
                'negated': negated
            })
        elif cmd_char == 'q':
            # No argument, just check terminator
            check_terminator(script, pos)
            commands.append({
                'cmd': 'q',
                'addr1': addr1,
                'addr2': addr2,
                'negated': negated
            })
        elif cmd_char == 's':
            cmd_s, pos = parse_s_command(script, pos)
            cmd_s['addr1'] = addr1
            cmd_s['addr2'] = addr2
            cmd_s['negated'] = negated
            commands.append(cmd_s)
        elif cmd_char == 'y':
            cmd_y, pos = parse_y_command(script, pos)
            cmd_y['addr1'] = addr1
            cmd_y['addr2'] = addr2
            cmd_y['negated'] = negated
            commands.append(cmd_y)
        elif cmd_char == 'a':
            # Rest of line is text (after stripping leading spaces/tabs)
            start = pos
            # Find end of line
            end = pos
            while end < len(script) and script[end] != '\n':
                end += 1
            text = script[start:end].lstrip(' \t')
            if not text:
                raise ScriptError('empty_text')
            text = unescape_text(text)
            pos = end
            commands.append({
                'cmd': 'a',
                'addr1': addr1,
                'addr2': addr2,
                'negated': negated,
                'text': text
            })
        elif cmd_char == 'i':
            # Rest of line is text (after stripping leading spaces/tabs)
            start = pos
            # Find end of line
            end = pos
            while end < len(script) and script[end] != '\n':
                end += 1
            text = script[start:end].lstrip(' \t')
            if not text:
                raise ScriptError('empty_text')
            text = unescape_text(text)
            pos = end
            commands.append({
                'cmd': 'i',
                'addr1': addr1,
                'addr2': addr2,
                'negated': negated,
                'text': text
            })

    return commands


def parse_address(script, pos, is_second=False):
    """Parse an address and return (address_dict, new_pos)."""
    if pos >= len(script):
        return None, pos

    char = script[pos]

    # +N (second address only)
    if char == '+':
        if not is_second:
            return None, pos
        pos += 1
        num_str = ''
        while pos < len(script) and script[pos].isdigit():
            num_str += script[pos]
            pos += 1
        if not num_str:
            raise ScriptError('bad_address')
        return {'type': 'offset', 'value': int(num_str)}, pos

    # $ (end of file)
    if char == '$':
        return {'type': 'dollar'}, pos + 1

    # /regex/
    if char == '/':
        return parse_regex_address(script, pos)

    # Line number or first~step
    if char.isdigit():
        num_str = ''
        pos_start = pos
        while pos < len(script) and script[pos].isdigit():
            num_str += script[pos]
            pos += 1

        num = int(num_str)

        # Check for zero as plain address
        if num == 0 and (pos >= len(script) or script[pos] not in '~+,'):
            raise ScriptError('bad_address')

        # Check for first~step
        if pos < len(script) and script[pos] == '~':
            if is_second:
                raise ScriptError('bad_address')
            pos += 1
            step_str = ''
            while pos < len(script) and script[pos].isdigit():
                step_str += script[pos]
                pos += 1
            if not step_str:
                raise ScriptError('bad_address')
            return {'type': 'step', 'first': num, 'step': int(step_str)}, pos

        # Check if it's being used as second address when it shouldn't
        if is_second and num == 0:
            raise ScriptError('bad_address')

        return {'type': 'num', 'value': num}, pos

    # No address
    return None, pos


def parse_regex_address(script, pos):
    """Parse /regex/ address."""
    if script[pos] != '/':
        raise ScriptError('bad_address')

    pos += 1
    regex_str = ''

    while pos < len(script):
        if script[pos] == '\n':
            raise ScriptError('unterminated')
        if script[pos] == '\\':
            if pos + 1 >= len(script):
                raise ScriptError('unterminated')
            if script[pos + 1] == '/':
                regex_str += '/'
                pos += 2
            else:
                regex_str += script[pos + 1]
                pos += 2
        elif script[pos] == '/':
            pos += 1
            break
        else:
            regex_str += script[pos]
            pos += 1
    else:
        raise ScriptError('unterminated')

    if not regex_str:
        raise ScriptError('bad_regex')

    try:
        compiled = re.compile(regex_str)
    except re.error:
        raise ScriptError('bad_regex')

    return {'type': 'regex', 'pattern': regex_str, 'compiled': compiled}, pos


def parse_s_command(script, pos):
    """Parse s command: s<delim>regex<delim>replacement<delim>flags."""
    if pos >= len(script):
        raise ScriptError('bad_delimiter')

    delim = script[pos]
    if delim not in '/,:#_@%!':
        raise ScriptError('bad_delimiter')

    pos += 1

    # Parse regex
    regex_str = ''
    while pos < len(script):
        if script[pos] == '\n':
            raise ScriptError('unterminated')
        if script[pos] == '\\':
            if pos + 1 >= len(script):
                raise ScriptError('unterminated')
            if script[pos + 1] == delim:
                regex_str += delim
                pos += 2
            else:
                regex_str += script[pos:pos+2]
                pos += 2
        elif script[pos] == delim:
            pos += 1
            break
        else:
            regex_str += script[pos]
            pos += 1
    else:
        raise ScriptError('unterminated')

    if not regex_str:
        raise ScriptError('bad_regex')

    # Parse replacement
    repl_str = ''
    while pos < len(script):
        if script[pos] == '\n':
            raise ScriptError('unterminated')
        if script[pos] == '\\':
            if pos + 1 >= len(script):
                raise ScriptError('unterminated')
            if script[pos + 1] == delim:
                repl_str += delim
                pos += 2
            else:
                repl_str += script[pos:pos+2]
                pos += 2
        elif script[pos] == delim:
            pos += 1
            break
        else:
            repl_str += script[pos]
            pos += 1
    else:
        raise ScriptError('unterminated')

    # Parse flags
    flags = ''
    flag_start = pos
    while pos < len(script) and script[pos] not in ';\n' and script[pos] not in ' \t':
        flags += script[pos]
        pos += 1

    # Parse flags
    parsed_flags = parse_s_flags(flags, regex_str)

    # Validate backrefs (before checking terminator)
    group_count = parsed_flags['compiled'].groups
    validate_backrefs(repl_str, group_count)

    # Check terminator
    check_terminator(script, pos)

    return {
        'cmd': 's',
        'regex': regex_str,
        'replacement': repl_str,
        'flags': parsed_flags
    }, pos


def parse_s_flags(flags, regex_str):
    """Parse s command flags."""
    result = {
        'global': False,
        'case_insensitive': False,
        'print': False,
        'nth_match': None
    }

    seen_number = False
    seen_p = False
    seen_g = False
    seen_i = False

    for char in flags:
        if char == 'g':
            if seen_g:
                raise ScriptError('bad_flag')
            seen_g = True
            result['global'] = True
        elif char == 'p':
            if seen_p:
                raise ScriptError('bad_flag')
            seen_p = True
            result['print'] = True
        elif char == 'i':
            if seen_i:
                raise ScriptError('bad_flag')
            seen_i = True
            result['case_insensitive'] = True
        elif char.isdigit():
            if seen_number:
                raise ScriptError('bad_flag')
            seen_number = True
            num = int(char)
            if num == 0:
                raise ScriptError('bad_flag')
            result['nth_match'] = num
        else:
            raise ScriptError('bad_flag')

    # Validate regex now that we have all flags
    flags_arg = 0
    if result['case_insensitive']:
        flags_arg |= re.IGNORECASE

    try:
        compiled = re.compile(regex_str, flags_arg)
    except re.error:
        raise ScriptError('bad_regex')

    result['compiled'] = compiled

    return result


def validate_backrefs(replacement, group_count):
    """Validate that all backrefs in replacement are valid."""
    i = 0
    while i < len(replacement):
        if replacement[i] == '\\' and i + 1 < len(replacement):
            next_char = replacement[i + 1]
            if next_char in '123456789':
                group_num = int(next_char)
                if group_num > group_count:
                    raise ScriptError('bad_backref')
            i += 2
        else:
            i += 1


def parse_y_command(script, pos):
    """Parse y command: y<delim>src<delim>dst<delim>."""
    if pos >= len(script):
        raise ScriptError('bad_delimiter')

    delim = script[pos]
    if delim not in '/,:#_@%!':
        raise ScriptError('bad_delimiter')

    pos += 1

    # Parse src
    src_str = ''
    while pos < len(script):
        if script[pos] == '\n':
            raise ScriptError('unterminated')
        if script[pos] == '\\':
            if pos + 1 >= len(script):
                raise ScriptError('unterminated')
            if script[pos + 1] == delim:
                src_str += delim
                pos += 2
            else:
                src_str += script[pos:pos+2]
                pos += 2
        elif script[pos] == delim:
            pos += 1
            break
        else:
            src_str += script[pos]
            pos += 1
    else:
        raise ScriptError('unterminated')

    # Parse dst
    dst_str = ''
    while pos < len(script):
        if script[pos] == '\n':
            raise ScriptError('unterminated')
        if script[pos] == '\\':
            if pos + 1 >= len(script):
                raise ScriptError('unterminated')
            if script[pos + 1] == delim:
                dst_str += delim
                pos += 2
            else:
                dst_str += script[pos:pos+2]
                pos += 2
        elif script[pos] == delim:
            pos += 1
            break
        else:
            dst_str += script[pos]
            pos += 1
    else:
        raise ScriptError('unterminated')

    # Unescape src and dst
    src_unescaped = unescape_text(src_str)
    dst_unescaped = unescape_text(dst_str)

    # Check equal length (before checking terminator)
    if len(src_unescaped) != len(dst_unescaped):
        raise ScriptError('bad_y')

    # Check terminator
    check_terminator(script, pos)

    return {
        'cmd': 'y',
        'src': src_unescaped,
        'dst': dst_unescaped
    }, pos


def unescape_text(s):
    """Unescape \\n, \\t, and \\x sequences."""
    result = ''
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_char = s[i + 1]
            if next_char == 'n':
                result += '\n'
                i += 2
            elif next_char == 't':
                result += '\t'
                i += 2
            else:
                result += next_char
                i += 2
        else:
            result += s[i]
            i += 1
    return result


def skip_spaces_tabs(script, pos):
    """Skip spaces and tabs (not newlines)."""
    while pos < len(script) and script[pos] in ' \t':
        pos += 1
    return pos


def check_terminator(script, pos):
    """Check that we have a valid terminator (;, newline, or end)."""
    pos = skip_spaces_tabs(script, pos)
    if pos < len(script) and script[pos] not in ';\n':
        raise ScriptError('trailing_garbage')


def should_apply(cmd, line_num, pattern_space, total_lines, cmd_state):
    """Determine if a command should apply to this line."""
    addr1 = cmd.get('addr1')
    addr2 = cmd.get('addr2')
    negated = cmd.get('negated', False)

    # Initialize range state if not present
    if 'range_state' not in cmd_state:
        cmd_state['range_state'] = 'inactive'
        cmd_state['range_start'] = None

    if addr1 is None and addr2 is None:
        # No address, applies to all lines
        applies = True
    elif addr2 is None:
        # Single address
        applies = match_address(addr1, line_num, pattern_space, total_lines)
    else:
        # Range
        if cmd_state['range_state'] == 'inactive':
            if match_address(addr1, line_num, pattern_space, total_lines):
                cmd_state['range_start'] = line_num
                applies = True
                # Check if range closes on start line
                if is_range_close(addr2, line_num, pattern_space, total_lines, line_num):
                    cmd_state['range_state'] = 'inactive'
                else:
                    cmd_state['range_state'] = 'active'
            else:
                applies = False
        else:
            # Range is active
            applies = True
            # Check if range closes
            if is_range_close(addr2, line_num, pattern_space, total_lines, cmd_state['range_start']):
                cmd_state['range_state'] = 'inactive'

    if negated:
        applies = not applies

    return applies


def match_address(addr, line_num, pattern_space, total_lines):
    """Check if an address matches the current line."""
    if addr is None:
        return True

    addr_type = addr['type']

    if addr_type == 'num':
        return line_num == addr['value']
    elif addr_type == 'dollar':
        return line_num == total_lines
    elif addr_type == 'regex':
        return bool(addr['compiled'].search(pattern_space))
    elif addr_type == 'step':
        first = addr['first']
        step = addr['step']
        if step == 0:
            return line_num == first
        else:
            return line_num >= first and (line_num - first) % step == 0

    return False


def is_range_close(addr2, line_num, pattern_space, total_lines, start_line):
    """Check if range address closes."""
    addr_type = addr2['type']

    if addr_type == 'num':
        return line_num >= addr2['value']
    elif addr_type == 'dollar':
        return line_num == total_lines
    elif addr_type == 'regex':
        return bool(addr2['compiled'].search(pattern_space))
    elif addr_type == 'offset':
        return line_num >= start_line + addr2['value']

    return False


def cmd_substitute(cmd, pattern_space):
    """Execute s command. Returns (new_pattern_space, was_replacement_made)."""
    regex = cmd['flags']['compiled']
    replacement = cmd['replacement']
    flags = cmd['flags']

    # Find all matches
    matches = list(regex.finditer(pattern_space))

    if not matches:
        return pattern_space, False

    # Determine which matches to replace
    if flags['global']:
        nth_start = flags['nth_match'] if flags['nth_match'] is not None else 1
        matches_to_replace = [(i + 1, m) for i, m in enumerate(matches) if i + 1 >= nth_start]
    else:
        nth = flags['nth_match'] if flags['nth_match'] is not None else 1
        matches_to_replace = [(i + 1, m) for i, m in enumerate(matches) if i + 1 == nth]

    if not matches_to_replace:
        return pattern_space, False

    # Build result by replacing matches
    result = ''
    last_end = 0

    for match_num, match in matches_to_replace:
        result += pattern_space[last_end:match.start()]
        result += build_replacement(replacement, match, cmd['regex'])
        last_end = match.end()

    result += pattern_space[last_end:]

    return result, True


def build_replacement(repl_template, match, regex_pattern):
    """Build replacement string from template."""
    result = ''
    i = 0

    # Count groups in the original pattern
    try:
        compiled = re.compile(regex_pattern)
        group_count = compiled.groups
    except:
        group_count = 0

    while i < len(repl_template):
        if repl_template[i] == '\\' and i + 1 < len(repl_template):
            next_char = repl_template[i + 1]
            if next_char == 'n':
                result += '\n'
                i += 2
            elif next_char == 't':
                result += '\t'
                i += 2
            elif next_char in '123456789':
                group_num = int(next_char)
                if group_num > group_count:
                    raise ScriptError('bad_backref')
                try:
                    group_val = match.group(group_num)
                    if group_val is None:
                        result += ''
                    else:
                        result += group_val
                except:
                    raise ScriptError('bad_backref')
                i += 2
            else:
                # Literal character
                result += next_char
                i += 2
        elif repl_template[i] == '&':
            result += match.group(0)
            i += 1
        else:
            result += repl_template[i]
            i += 1

    return result


def cmd_transliterate(cmd, pattern_space):
    """Execute y command."""
    src = cmd['src']
    dst = cmd['dst']

    # Build mapping (last occurrence of each char in src wins)
    mapping = {}
    for i, char in enumerate(src):
        mapping[char] = dst[i]

    result = ''
    for char in pattern_space:
        if char in mapping:
            result += mapping[char]
        else:
            result += char

    return result
