import re
from typing import Optional, List, Tuple, Union


class ScriptError(ValueError):
    """Exception for syntax errors in sed scripts."""
    def __init__(self, kind: str, message: str = ""):
        self.kind = kind
        super().__init__(f"{kind}: {message}" if message else kind)


def run(script: str, text: str, quiet: bool = False) -> str:
    """Execute a sed-like script on text and return the output."""

    # Parse the script
    commands = parse_script(script)

    # Split input text
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]

    # Execute commands
    output_chunks = []
    queue = []

    # Initialize range states for each command
    range_states = [{'active': False, 'start': None} for _ in commands]

    line_idx = 0
    while line_idx < len(lines):
        pattern_space = lines[line_idx]
        current_line = line_idx + 1  # 1-indexed line numbers
        queue = []
        deleted = False
        quit_flag = False

        for cmd_idx, cmd in enumerate(commands):
            if quit_flag or deleted:
                break

            # Check if command applies to this line
            applies = check_address_match(cmd, current_line, pattern_space, lines, range_states[cmd_idx])

            if not applies:
                continue

            # Execute command
            result = execute_command(cmd, pattern_space, output_chunks, queue, deleted, quit_flag)
            pattern_space = result.pattern_space
            if result.deleted:
                deleted = True
            if result.quit:
                quit_flag = True
            if result.output_chunks is not None:
                output_chunks = result.output_chunks

        # End of cycle
        if not deleted and not quiet:
            output_chunks.append(pattern_space)

        # Emit queued text
        output_chunks.extend(queue)

        if quit_flag:
            break

        line_idx += 1

    # Format output
    if not output_chunks:
        return ""
    return '\n'.join(output_chunks) + '\n'


class CommandResult:
    def __init__(self, pattern_space: str = "", deleted: bool = False, quit: bool = False,
                 output_chunks: Optional[List[str]] = None):
        self.pattern_space = pattern_space
        self.deleted = deleted
        self.quit = quit
        self.output_chunks = output_chunks


def parse_script(script: str) -> List[dict]:
    """Parse the sed script into a list of commands."""
    commands = []
    pos = 0

    while pos < len(script):
        # Skip whitespace, semicolons, and comments
        while pos < len(script) and script[pos] in ' \t\n;':
            pos += 1

        if pos >= len(script):
            break

        # Check for comment
        if script[pos] == '#':
            # Skip to end of line or end of script
            while pos < len(script) and script[pos] != '\n':
                pos += 1
            continue

        # Parse command
        cmd, pos = parse_command(script, pos)
        commands.append(cmd)

    return commands


def parse_command(script: str, pos: int) -> Tuple[dict, int]:
    """Parse a single command and return (command_dict, new_pos)."""
    cmd = {'addr1': None, 'addr2': None, 'negate': False}

    # Parse first address (optional)
    if pos < len(script) and is_address_start(script, pos):
        addr1, pos = parse_address(script, pos, False)
        cmd['addr1'] = addr1

        # Skip spaces/tabs
        while pos < len(script) and script[pos] in ' \t':
            pos += 1

        # Check for comma (range)
        if pos < len(script) and script[pos] == ',':
            pos += 1
            # Skip spaces/tabs
            while pos < len(script) and script[pos] in ' \t':
                pos += 1

            # Parse second address
            if pos >= len(script) or not is_address_start(script, pos):
                raise ScriptError("bad_address")
            addr2, pos = parse_address(script, pos, True)
            cmd['addr2'] = addr2

    # Skip spaces/tabs
    while pos < len(script) and script[pos] in ' \t':
        pos += 1

    # Parse negation (!)
    bang_count = 0
    while pos < len(script) and script[pos] == '!':
        bang_count += 1
        pos += 1
        # Skip spaces/tabs after !
        while pos < len(script) and script[pos] in ' \t':
            pos += 1

    if bang_count > 1:
        raise ScriptError("bad_bang")
    if bang_count == 1:
        if cmd['addr1'] is None:
            raise ScriptError("bad_bang")
        cmd['negate'] = True

    # Skip spaces/tabs
    while pos < len(script) and script[pos] in ' \t':
        pos += 1

    # Get command letter
    if pos >= len(script):
        raise ScriptError("unknown_command")

    cmd_letter = script[pos]
    pos += 1

    if cmd_letter not in 'sydpqai':
        raise ScriptError("unknown_command")

    cmd['type'] = cmd_letter

    # Check for extra addresses on q
    if cmd_letter == 'q' and cmd['addr2'] is not None:
        raise ScriptError("extra_address")

    # Parse command-specific arguments
    if cmd_letter == 's':
        cmd['subst'] = parse_s_command(script, pos)
        pos = cmd['subst']['end_pos']
        # Check for terminator
        while pos < len(script) and script[pos] in ' \t':
            pos += 1
        if pos < len(script) and script[pos] not in ';\n':
            raise ScriptError("trailing_garbage")
        if pos < len(script) and script[pos] in ';\n':
            pos += 1
    elif cmd_letter == 'y':
        cmd['trans'] = parse_y_command(script, pos)
        pos = cmd['trans']['end_pos']
        # Check for terminator
        while pos < len(script) and script[pos] in ' \t':
            pos += 1
        if pos < len(script) and script[pos] not in ';\n':
            raise ScriptError("trailing_garbage")
        if pos < len(script) and script[pos] in ';\n':
            pos += 1
    elif cmd_letter in 'dpq':
        # Skip spaces/tabs
        while pos < len(script) and script[pos] in ' \t':
            pos += 1

        # Must be followed by ; newline or end of script
        if pos < len(script) and script[pos] not in ';\n':
            raise ScriptError("trailing_garbage")

        # Consume delimiter
        if pos < len(script) and script[pos] in ';\n':
            pos += 1
    elif cmd_letter in 'ai':
        # Rest of line is the text
        text_start = pos
        while pos < len(script) and script[pos] != '\n':
            pos += 1

        text = script[text_start:pos]
        # Remove leading spaces and tabs
        text = text.lstrip(' \t')

        if not text:
            raise ScriptError("empty_text")

        # Unescape the text
        text = unescape_text(text)
        cmd['text'] = text

        # Consume newline if present
        if pos < len(script) and script[pos] == '\n':
            pos += 1

    return cmd, pos


def is_address_start(script: str, pos: int) -> bool:
    """Check if position starts an address."""
    if pos >= len(script):
        return False
    c = script[pos]
    return c in '/$' or c.isdigit() or c == '+' or c == '~'


def parse_address(script: str, pos: int, is_second: bool) -> Tuple[dict, int]:
    """Parse an address and return (address_dict, new_pos)."""
    if pos >= len(script):
        raise ScriptError("bad_address")

    c = script[pos]

    # Numeric address or step address
    if c.isdigit() or (c == '~' and not is_second):
        # Parse number
        num_start = pos
        while pos < len(script) and script[pos].isdigit():
            pos += 1

        num = int(script[num_start:pos])

        # Check for step address
        if pos < len(script) and script[pos] == '~':
            if is_second:
                raise ScriptError("bad_address")
            pos += 1

            if pos >= len(script) or not script[pos].isdigit():
                raise ScriptError("bad_address")

            step_start = pos
            while pos < len(script) and script[pos].isdigit():
                pos += 1

            step = int(script[step_start:pos])
            return {'type': 'step', 'first': num, 'step': step}, pos
        else:
            if num == 0:
                raise ScriptError("bad_address")
            return {'type': 'line', 'num': num}, pos

    # Plus offset (second address only)
    elif c == '+':
        if not is_second:
            raise ScriptError("bad_address")
        pos += 1

        if pos >= len(script) or not script[pos].isdigit():
            raise ScriptError("bad_address")

        num_start = pos
        while pos < len(script) and script[pos].isdigit():
            pos += 1

        num = int(script[num_start:pos])
        return {'type': 'offset', 'num': num}, pos

    # Dollar (last line)
    elif c == '$':
        if is_second:
            return {'type': 'dollar'}, pos + 1
        else:
            return {'type': 'dollar'}, pos + 1

    # Regex address
    elif c == '/':
        pos += 1
        regex_start = pos

        while pos < len(script):
            if script[pos] == '/':
                regex_content = script[regex_start:pos]
                pos += 1

                if not regex_content:
                    raise ScriptError("bad_regex")

                try:
                    compiled = re.compile(unescape_regex(regex_content))
                except:
                    raise ScriptError("bad_regex")

                return {'type': 'regex', 'pattern': regex_content, 'compiled': compiled}, pos
            elif script[pos] == '\\' and pos + 1 < len(script):
                pos += 2
            elif script[pos] == '\n':
                raise ScriptError("unterminated")
            else:
                pos += 1

        # End of script
        raise ScriptError("unterminated")

    else:
        raise ScriptError("bad_address")


def parse_s_command(script: str, pos: int) -> dict:
    """Parse the s command and return the substitution dict."""
    if pos >= len(script):
        raise ScriptError("bad_delimiter")

    delimiter = script[pos]
    if delimiter not in '/, :#_@%!':
        raise ScriptError("bad_delimiter")

    pos += 1

    # Parse regex
    regex_start = pos
    while pos < len(script):
        if script[pos] == delimiter:
            regex_content = script[regex_start:pos]
            pos += 1
            break
        elif script[pos] == '\\' and pos + 1 < len(script):
            pos += 2
        elif script[pos] == '\n':
            raise ScriptError("unterminated")
        else:
            pos += 1
    else:
        raise ScriptError("unterminated")

    if not regex_content:
        raise ScriptError("bad_regex")

    # Parse replacement
    repl_start = pos
    while pos < len(script):
        if script[pos] == delimiter:
            replacement = script[repl_start:pos]
            pos += 1
            break
        elif script[pos] == '\\' and pos + 1 < len(script):
            pos += 2
        elif script[pos] == '\n':
            raise ScriptError("unterminated")
        else:
            pos += 1
    else:
        raise ScriptError("unterminated")

    # Parse flags
    flags_start = pos
    while pos < len(script) and (script[pos].isalnum()):
        pos += 1

    flags_str = script[flags_start:pos]

    # Validate flags
    g_flag = False
    i_flag = False
    p_flag = False
    n_flag = None

    for flag_char in flags_str:
        if flag_char == 'g':
            if g_flag:
                raise ScriptError("bad_flag")
            g_flag = True
        elif flag_char == 'i':
            if i_flag:
                raise ScriptError("bad_flag")
            i_flag = True
        elif flag_char == 'p':
            if p_flag:
                raise ScriptError("bad_flag")
            p_flag = True
        elif flag_char.isdigit():
            if n_flag is not None:
                raise ScriptError("bad_flag")
            n_flag = int(flag_char)
            if n_flag == 0:
                raise ScriptError("bad_flag")
        else:
            raise ScriptError("bad_flag")

    # Compile regex
    try:
        regex_pattern = unescape_regex(regex_content)
        compiled = re.compile(regex_pattern, re.IGNORECASE if i_flag else 0)
    except:
        raise ScriptError("bad_regex")

    # Process replacement text for backreferences
    check_backreferences(replacement, compiled)

    return {
        'regex': regex_content,
        'replacement': replacement,
        'flags_g': g_flag,
        'flags_i': i_flag,
        'flags_p': p_flag,
        'flags_n': n_flag if n_flag else 1,
        'compiled': compiled,
        'end_pos': pos
    }


def parse_y_command(script: str, pos: int) -> dict:
    """Parse the y command and return the transliteration dict."""
    if pos >= len(script):
        raise ScriptError("bad_delimiter")

    delimiter = script[pos]
    if delimiter not in '/, :#_@%!':
        raise ScriptError("bad_delimiter")

    pos += 1

    # Parse src
    src_start = pos
    while pos < len(script):
        if script[pos] == delimiter:
            src = script[src_start:pos]
            pos += 1
            break
        elif script[pos] == '\\' and pos + 1 < len(script):
            pos += 2
        elif script[pos] == '\n':
            raise ScriptError("unterminated")
        else:
            pos += 1
    else:
        raise ScriptError("unterminated")

    # Parse dst
    dst_start = pos
    while pos < len(script):
        if script[pos] == delimiter:
            dst = script[dst_start:pos]
            pos += 1
            break
        elif script[pos] == '\\' and pos + 1 < len(script):
            pos += 2
        elif script[pos] == '\n':
            raise ScriptError("unterminated")
        else:
            pos += 1
    else:
        raise ScriptError("unterminated")

    # Unescape src and dst
    src_unescaped = unescape_y_text(src)
    dst_unescaped = unescape_y_text(dst)

    # Check lengths match
    if len(src_unescaped) != len(dst_unescaped):
        raise ScriptError("bad_y")

    return {
        'src': src_unescaped,
        'dst': dst_unescaped,
        'end_pos': pos
    }


def unescape_regex(s: str) -> str:
    """Unescape a regex pattern, handling only delimiter escapes."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            # Keep the backslash and next char as-is, they're part of the regex
            result.append(s[i])
            result.append(s[i + 1])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def unescape_text(s: str) -> str:
    """Unescape special sequences in a/i text."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_char = s[i + 1]
            if next_char == 'n':
                result.append('\n')
                i += 2
            elif next_char == 't':
                result.append('\t')
                i += 2
            else:
                result.append(next_char)
                i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def unescape_y_text(s: str) -> str:
    """Unescape special sequences in y command text."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_char = s[i + 1]
            if next_char == 'n':
                result.append('\n')
                i += 2
            elif next_char == 't':
                result.append('\t')
                i += 2
            else:
                result.append(next_char)
                i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def unescape_replacement(s: str) -> str:
    r"""Unescape special sequences in replacement text, handling &, \1-\9, \n, \t, etc."""
    # Return as-is; we'll handle escapes during replacement
    return s


def check_backreferences(replacement: str, compiled_regex) -> None:
    """Check that backreferences in replacement are valid."""
    group_count = compiled_regex.groups
    i = 0
    while i < len(replacement):
        if replacement[i] == '\\' and i + 1 < len(replacement):
            next_char = replacement[i + 1]
            if next_char.isdigit():
                ref_num = int(next_char)
                if ref_num > 0 and ref_num > group_count:
                    raise ScriptError("bad_backref")
            i += 2
        else:
            i += 1


def execute_replacement(match_obj, replacement: str) -> str:
    """Build the replacement string from a match object."""
    result = []
    i = 0
    while i < len(replacement):
        if replacement[i] == '\\' and i + 1 < len(replacement):
            next_char = replacement[i + 1]
            if next_char == 'n':
                result.append('\n')
                i += 2
            elif next_char == 't':
                result.append('\t')
                i += 2
            elif next_char.isdigit():
                ref_num = int(next_char)
                if ref_num > 0:
                    try:
                        group_val = match_obj.group(ref_num)
                        result.append(group_val if group_val is not None else '')
                    except IndexError:
                        result.append('')
                else:
                    # \0 is literal 0
                    result.append('0')
                i += 2
            else:
                # Any other character after backslash
                result.append(next_char)
                i += 2
        elif replacement[i] == '&':
            result.append(match_obj.group(0))
            i += 1
        else:
            result.append(replacement[i])
            i += 1
    return ''.join(result)


def execute_s_command(pattern_space: str, subst: dict) -> Tuple[str, bool]:
    """Execute a substitution command. Returns (new_pattern_space, was_replaced)."""
    compiled = subst['compiled']
    replacement = subst['replacement']
    g_flag = subst['flags_g']
    p_flag = subst['flags_p']
    n_flag = subst['flags_n']

    matches = list(compiled.finditer(pattern_space))

    if not matches:
        return pattern_space, False

    result = []
    last_end = 0
    was_replaced = False

    if g_flag:
        # Replace all matches starting from n_flag
        for idx, match_obj in enumerate(matches):
            if idx + 1 >= n_flag:
                result.append(pattern_space[last_end:match_obj.start()])
                result.append(execute_replacement(match_obj, replacement))
                last_end = match_obj.end()
                was_replaced = True
        result.append(pattern_space[last_end:])
    else:
        # Replace only the n_flag'th match
        if n_flag <= len(matches):
            target_match = matches[n_flag - 1]
            result.append(pattern_space[:target_match.start()])
            result.append(execute_replacement(target_match, replacement))
            result.append(pattern_space[target_match.end():])
            was_replaced = True
        else:
            result.append(pattern_space)

    return ''.join(result), was_replaced


def execute_y_command(pattern_space: str, trans: dict) -> str:
    """Execute a transliteration command."""
    src = trans['src']
    dst = trans['dst']

    # Build translation map (last occurrence wins)
    trans_map = {}
    for i, src_char in enumerate(src):
        trans_map[src_char] = dst[i]

    result = []
    for char in pattern_space:
        result.append(trans_map.get(char, char))

    return ''.join(result)


def execute_command(cmd: dict, pattern_space: str, output_chunks: List[str],
                   queue: List[str], deleted: bool, quit_flag: bool) -> CommandResult:
    """Execute a single command."""
    cmd_type = cmd['type']

    if cmd_type == 's':
        new_pattern_space, was_replaced = execute_s_command(pattern_space, cmd['subst'])
        if was_replaced and cmd['subst']['flags_p']:
            output_chunks.append(new_pattern_space)
        return CommandResult(pattern_space=new_pattern_space)

    elif cmd_type == 'y':
        new_pattern_space = execute_y_command(pattern_space, cmd['trans'])
        return CommandResult(pattern_space=new_pattern_space)

    elif cmd_type == 'd':
        return CommandResult(deleted=True)

    elif cmd_type == 'p':
        output_chunks.append(pattern_space)
        return CommandResult(pattern_space=pattern_space)

    elif cmd_type == 'q':
        return CommandResult(pattern_space=pattern_space, quit=True)

    elif cmd_type == 'a':
        queue.append(cmd['text'])
        return CommandResult(pattern_space=pattern_space)

    elif cmd_type == 'i':
        output_chunks.append(cmd['text'])
        return CommandResult(pattern_space=pattern_space)

    return CommandResult(pattern_space=pattern_space)


def check_address_match(cmd: dict, current_line: int, pattern_space: str, lines: List[str],
                       range_state: dict) -> bool:
    """Check if a command applies to the current line, and update range state."""
    addr1 = cmd['addr1']
    addr2 = cmd['addr2']
    negate = cmd['negate']

    # No address means always applies
    if addr1 is None:
        return not negate

    # Single address
    if addr2 is None:
        matches = match_address(addr1, current_line, pattern_space, lines)
        result = matches if not negate else not matches
        return result

    # Range
    result = False

    if not range_state['active']:
        # Range is inactive, check if addr1 matches
        if match_address(addr1, current_line, pattern_space, lines):
            range_state['start'] = current_line

            # Check if addr2 would close immediately
            # For plain numbers <= L, the range doesn't apply at all
            # For +0, the range applies as a one-line range
            if addr2['type'] == 'line' and addr2['num'] <= current_line:
                # Plain number <= L: range doesn't activate, command doesn't apply
                result = False
            elif addr2['type'] == 'offset' and addr2['num'] == 0:
                # +0: range applies as a one-line range, then closes
                result = True
            else:
                # Normal range: command applies and range activates
                result = True
                range_state['active'] = True
    else:
        # Range is active
        result = True

        # Check if addr2 closes
        if match_address_range_end(addr2, current_line, pattern_space, lines, range_state['start']):
            range_state['active'] = False

    if negate:
        result = not result

    return result


def match_address(addr: dict, current_line: int, pattern_space: str, lines: List[str]) -> bool:
    """Check if an address matches the current line."""
    addr_type = addr['type']

    if addr_type == 'line':
        return current_line == addr['num']

    elif addr_type == 'dollar':
        return current_line == len(lines)

    elif addr_type == 'regex':
        compiled = addr['compiled']
        return compiled.search(pattern_space) is not None

    elif addr_type == 'step':
        first = addr['first']
        step = addr['step']
        if step == 0:
            return current_line == first
        else:
            if current_line < first:
                return False
            return (current_line - first) % step == 0

    return False


def is_immediate_close(addr2: dict, current_line: int, pattern_space: str, lines: List[str]) -> bool:
    """Check if addr2 would close immediately on the start line."""
    addr_type = addr2['type']

    if addr_type == 'line':
        num = addr2['num']
        return num <= current_line

    elif addr_type == 'offset':
        num = addr2['num']
        return num == 0

    return False


def match_address_range_end(addr2: dict, current_line: int, pattern_space: str,
                           lines: List[str], start_line: int) -> bool:
    """Check if addr2 closes the range on the current line (when range is active)."""
    addr_type = addr2['type']

    if addr_type == 'line':
        num = addr2['num']
        return current_line >= num

    elif addr_type == 'dollar':
        return current_line == len(lines)

    elif addr_type == 'regex':
        compiled = addr2['compiled']
        return compiled.search(pattern_space) is not None

    elif addr_type == 'offset':
        num = addr2['num']
        return current_line >= start_line + num

    return False
