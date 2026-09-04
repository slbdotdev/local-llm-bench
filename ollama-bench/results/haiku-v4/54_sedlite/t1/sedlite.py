import re

class ScriptError(ValueError):
    """Exception for sed script syntax errors."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


class ScriptParser:
    """Parse a sed script into a list of commands."""

    def __init__(self, script):
        self.script = script
        self.pos = 0

    def peek(self):
        """Return current character without consuming it."""
        if self.pos < len(self.script):
            return self.script[self.pos]
        return None

    def consume(self):
        """Return current character and advance position."""
        if self.pos < len(self.script):
            ch = self.script[self.pos]
            self.pos += 1
            return ch
        return None

    def skip_whitespace_and_sep(self):
        """Skip spaces, tabs, newlines, and semicolons."""
        while self.pos < len(self.script):
            ch = self.script[self.pos]
            if ch in ' \t\n;':
                self.pos += 1
            else:
                break

    def skip_whitespace(self):
        """Skip spaces and tabs (not newlines or semicolons)."""
        while self.pos < len(self.script):
            ch = self.script[self.pos]
            if ch in ' \t':
                self.pos += 1
            else:
                break

    def parse(self):
        """Parse the entire script and return a list of commands."""
        commands = []

        while self.pos < len(self.script):
            self.skip_whitespace_and_sep()

            if self.pos >= len(self.script):
                break

            # Check for comment
            if self.peek() == '#':
                # Skip until newline or end
                while self.pos < len(self.script) and self.script[self.pos] != '\n':
                    self.pos += 1
                continue

            # Parse address and command
            cmd = self.parse_command()
            if cmd:
                commands.append(cmd)

        return commands

    def parse_command(self):
        """Parse a single command with optional addresses."""
        # Parse first address (optional)
        addr1 = None
        try:
            addr1 = self.parse_address(first_addr=True)
        except ScriptError:
            raise

        if addr1 is not None:
            self.skip_whitespace()

            # Check for second address
            addr2 = None
            if self.peek() == ',':
                self.consume()  # consume comma
                self.skip_whitespace()
                try:
                    addr2 = self.parse_address(first_addr=False)
                except ScriptError:
                    raise
                if addr2 is None:
                    raise ScriptError("bad_address")
        else:
            addr2 = None

        self.skip_whitespace()

        # Parse optional negation
        negate = False
        bang_count = 0
        while self.peek() == '!':
            bang_count += 1
            self.consume()
            self.skip_whitespace()

        if bang_count > 1:
            raise ScriptError("bad_bang")
        if bang_count == 1:
            if addr1 is None and addr2 is None:
                raise ScriptError("bad_bang")
            negate = True

        # Parse command letter
        cmd_char = self.peek()
        if cmd_char not in 'sydpqai':
            raise ScriptError("unknown_command")
        self.consume()

        # Check extra_address for q
        if cmd_char == 'q':
            if addr2 is not None:
                raise ScriptError("extra_address")

        # Parse command arguments
        if cmd_char == 's':
            cmd = self.parse_s_command(addr1, addr2, negate)
        elif cmd_char == 'y':
            cmd = self.parse_y_command(addr1, addr2, negate)
        elif cmd_char == 'd':
            self.parse_terminator()
            cmd = ('d', addr1, addr2, negate)
        elif cmd_char == 'p':
            self.parse_terminator()
            cmd = ('p', addr1, addr2, negate)
        elif cmd_char == 'q':
            self.parse_terminator()
            cmd = ('q', addr1, addr2, negate)
        elif cmd_char == 'a':
            text = self.parse_text_command()
            cmd = ('a', addr1, addr2, negate, text)
        elif cmd_char == 'i':
            text = self.parse_text_command()
            cmd = ('i', addr1, addr2, negate, text)

        return cmd

    def parse_address(self, first_addr=True):
        """Parse an address. Returns None if no address present."""
        if self.pos >= len(self.script):
            return None

        ch = self.peek()

        # Check for +N (only allowed as second address)
        if ch == '+':
            if first_addr:
                return None
            self.consume()
            num_str = ''
            while self.pos < len(self.script) and self.script[self.pos].isdigit():
                num_str += self.consume()
            if not num_str:
                raise ScriptError("bad_address")
            return ('+', int(num_str))

        # Check for number or first~step
        if ch and ch.isdigit():
            num_str = ''
            while self.pos < len(self.script) and self.script[self.pos].isdigit():
                num_str += self.consume()
            num = int(num_str)

            # Check for ~step (only allowed as first address)
            if self.peek() == '~':
                if not first_addr:
                    return ('num', num)  # Return just the number, ~ won't be consumed
                self.consume()
                step_str = ''
                while self.pos < len(self.script) and self.script[self.pos].isdigit():
                    step_str += self.consume()
                if not step_str:
                    raise ScriptError("bad_address")
                step = int(step_str)
                return ('~', num, step)

            # Check for line number 0 (only allowed in step address, which we handled above)
            if num == 0:
                raise ScriptError("bad_address")

            return ('num', num)

        # Check for $
        if ch == '$':
            self.consume()
            return ('$',)

        # Check for /regex/
        if ch == '/':
            regex = self.parse_regex()
            return ('regex', regex)

        return None

    def parse_regex(self):
        """Parse a regex between slashes."""
        self.consume()  # consume opening /

        regex_str = ''
        while self.pos < len(self.script):
            ch = self.script[self.pos]

            if ch == '\n':
                raise ScriptError("unterminated")

            if ch == '\\':
                # Backslash escape
                self.pos += 1
                if self.pos >= len(self.script):
                    raise ScriptError("unterminated")
                next_ch = self.script[self.pos]
                if next_ch == '/':
                    regex_str += '/'
                    self.pos += 1
                else:
                    regex_str += '\\' + next_ch
                    self.pos += 1
            elif ch == '/':
                self.pos += 1
                break
            else:
                regex_str += ch
                self.pos += 1
        else:
            raise ScriptError("unterminated")

        if not regex_str:
            raise ScriptError("bad_regex")

        # Validate regex
        try:
            re.compile(regex_str)
        except re.error:
            raise ScriptError("bad_regex")

        return regex_str

    def parse_s_command(self, addr1, addr2, negate):
        """Parse s command."""
        # Get delimiter
        delimiter = self.peek()
        if delimiter not in '/, :#_@%!':
            raise ScriptError("bad_delimiter")
        self.consume()

        # Parse regex (don't validate yet)
        regex = self.parse_delimited_section(delimiter, is_regex=False)

        # Parse replacement (don't validate yet)
        repl = self.parse_delimited_section(delimiter, is_regex=False)

        # Parse flags
        flags_str = ''
        while self.pos < len(self.script):
            ch = self.peek()
            if ch and ch.isalnum():
                flags_str += self.consume()
            else:
                break

        # Parse and validate flags (this happens before regex validation per error precedence)
        flags = self.parse_s_flags(flags_str)

        # Now validate regex
        if not regex:
            raise ScriptError("bad_regex")
        try:
            re.compile(regex)
        except re.error:
            raise ScriptError("bad_regex")

        # Validate backref in replacement
        self.validate_s_replacement(repl, regex)

        self.parse_terminator()

        return ('s', addr1, addr2, negate, regex, repl, flags)

    def parse_delimited_section(self, delimiter, is_regex=False):
        """Parse a section delimited by the given character."""
        section = ''
        while self.pos < len(self.script):
            ch = self.script[self.pos]

            if ch == '\n':
                raise ScriptError("unterminated")

            if ch == '\\':
                # Backslash escape
                self.pos += 1
                if self.pos >= len(self.script):
                    raise ScriptError("unterminated")
                next_ch = self.script[self.pos]
                if next_ch == delimiter:
                    section += delimiter
                    self.pos += 1
                else:
                    section += '\\' + next_ch
                    self.pos += 1
            elif ch == delimiter:
                self.pos += 1
                break
            else:
                section += ch
                self.pos += 1
        else:
            raise ScriptError("unterminated")

        return section

    def parse_s_flags(self, flags_str):
        """Parse s command flags."""
        flags = {
            'g': False,
            'i': False,
            'p': False,
            'n': None  # numeric flag (None means 1)
        }

        i = 0
        while i < len(flags_str):
            ch = flags_str[i]

            if ch == 'g':
                if flags['g']:
                    raise ScriptError("bad_flag")
                flags['g'] = True
            elif ch == 'i':
                if flags['i']:
                    raise ScriptError("bad_flag")
                flags['i'] = True
            elif ch == 'p':
                if flags['p']:
                    raise ScriptError("bad_flag")
                flags['p'] = True
            elif ch.isdigit():
                if flags['n'] is not None:
                    raise ScriptError("bad_flag")
                num_str = ''
                while i < len(flags_str) and flags_str[i].isdigit():
                    num_str += flags_str[i]
                    i += 1
                num = int(num_str)
                if num == 0:
                    raise ScriptError("bad_flag")
                flags['n'] = num
                i -= 1  # Will be incremented at end of loop
            else:
                raise ScriptError("bad_flag")

            i += 1

        return flags

    def validate_s_replacement(self, repl, regex):
        """Validate backref numbers in replacement."""
        # Count groups in regex
        try:
            compiled = re.compile(regex)
            group_count = compiled.groups
        except re.error:
            # Already validated, shouldn't happen
            group_count = 0

        # Check for backrefs in replacement
        i = 0
        while i < len(repl):
            if repl[i] == '\\' and i + 1 < len(repl):
                next_ch = repl[i + 1]
                if next_ch in '123456789':
                    ref_num = int(next_ch)
                    if ref_num > group_count:
                        raise ScriptError("bad_backref")
                i += 2
            else:
                i += 1

    def parse_y_command(self, addr1, addr2, negate):
        """Parse y command."""
        # Get delimiter
        delimiter = self.peek()
        if delimiter not in '/, :#_@%!':
            raise ScriptError("bad_delimiter")
        self.consume()

        # Parse src
        try:
            src = self.parse_delimited_section(delimiter)
        except ScriptError:
            raise

        # Parse dst
        try:
            dst = self.parse_delimited_section(delimiter)
        except ScriptError:
            raise

        # Unescape src and dst
        src = self.unescape_y_string(src)
        dst = self.unescape_y_string(dst)

        # Check same length
        if len(src) != len(dst):
            raise ScriptError("bad_y")

        self.parse_terminator()

        return ('y', addr1, addr2, negate, src, dst)

    def unescape_y_string(self, s):
        """Unescape a y command string."""
        result = ''
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                next_ch = s[i + 1]
                if next_ch == 'n':
                    result += '\n'
                    i += 2
                elif next_ch == 't':
                    result += '\t'
                    i += 2
                else:
                    result += next_ch
                    i += 2
            else:
                result += s[i]
                i += 1
        return result

    def parse_text_command(self):
        """Parse a/i command text (rest of line)."""
        # Skip spaces and tabs at start
        self.skip_whitespace()

        # Rest of line until newline or end
        text = ''
        while self.pos < len(self.script) and self.script[self.pos] != '\n':
            text += self.consume()

        if not text:
            raise ScriptError("empty_text")

        # Unescape
        text = self.unescape_text(text)

        return text

    def unescape_text(self, s):
        """Unescape a/i command text."""
        result = ''
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                next_ch = s[i + 1]
                if next_ch == 'n':
                    result += '\n'
                    i += 2
                elif next_ch == 't':
                    result += '\t'
                    i += 2
                else:
                    result += next_ch
                    i += 2
            else:
                result += s[i]
                i += 1
        return result

    def parse_terminator(self):
        """Parse terminator (space/tab followed by ; or newline or end)."""
        self.skip_whitespace()

        if self.pos < len(self.script):
            ch = self.peek()
            if ch not in ';\n':
                raise ScriptError("trailing_garbage")
            if ch == '\n':
                self.consume()


class ScriptExecutor:
    """Execute parsed sed commands."""

    def __init__(self, commands, lines, quiet):
        self.commands = commands
        self.lines = lines
        self.quiet = quiet
        self.output = []
        self.ranges = {}  # Track range states for each command
        for i in range(len(commands)):
            self.ranges[i] = None  # None = inactive, number = start line

    def execute(self):
        """Execute all commands on all lines."""
        for line_num, line in enumerate(self.lines, 1):
            self.process_line(line_num, line)

        return '\n'.join(self.output) + ('\n' if self.output else '')

    def process_line(self, line_num, line):
        """Process a single line through all commands."""
        pattern_space = line
        append_queue = []
        quit_flag = False
        delete_flag = False

        for cmd_idx, cmd in enumerate(self.commands):
            if delete_flag or quit_flag:
                break

            applies = self.check_applies(cmd_idx, cmd, line_num, pattern_space)

            if applies:
                if cmd[0] == 's':
                    pattern_space = self.execute_s(cmd, pattern_space)
                elif cmd[0] == 'y':
                    pattern_space = self.execute_y(cmd, pattern_space)
                elif cmd[0] == 'd':
                    delete_flag = True
                elif cmd[0] == 'p':
                    self.output.append(pattern_space)
                elif cmd[0] == 'q':
                    quit_flag = True
                elif cmd[0] == 'a':
                    append_queue.append(cmd[4])
                elif cmd[0] == 'i':
                    self.output.append(cmd[4])

        # After all commands
        if not delete_flag and not self.quiet:
            self.output.append(pattern_space)

        for text in append_queue:
            self.output.append(text)

        if quit_flag:
            return True  # Signal to stop processing lines

        return False

    def check_applies(self, cmd_idx, cmd, line_num, pattern_space):
        """Check if a command applies to the current line."""
        addr1 = cmd[1]
        addr2 = cmd[2]
        negate = cmd[3]

        applies = False

        if addr1 is None and addr2 is None:
            # No address, applies to all lines
            applies = True
        elif addr2 is None:
            # Single address
            applies = self.match_address(addr1, line_num, pattern_space)
        else:
            # Range address
            range_state = self.ranges[cmd_idx]

            if range_state is None:
                # Inactive
                if self.match_address(addr1, line_num, pattern_space):
                    applies = True
                    self.ranges[cmd_idx] = line_num

                    # Check if immediately closes
                    if self.should_close_range(addr2, line_num, pattern_space, line_num):
                        self.ranges[cmd_idx] = None
            else:
                # Active
                applies = True

                # Check if closes
                if self.should_close_range(addr2, line_num, pattern_space, range_state):
                    self.ranges[cmd_idx] = None

        if negate:
            applies = not applies

        return applies

    def match_address(self, addr, line_num, pattern_space):
        """Check if an address matches."""
        if addr is None:
            return True

        if addr[0] == 'num':
            return line_num == addr[1]
        elif addr[0] == '$':
            return line_num == len(self.lines)
        elif addr[0] == 'regex':
            return bool(re.search(addr[1], pattern_space))
        elif addr[0] == '~':
            first, step = addr[1], addr[2]
            if step == 0:
                return line_num == first
            else:
                return line_num >= first and (line_num - first) % step == 0
        elif addr[0] == '+':
            # This shouldn't be called directly, only in range checking
            return False

        return False

    def should_close_range(self, addr2, line_num, pattern_space, start_line):
        """Check if range should close."""
        if addr2[0] == 'num':
            return line_num >= addr2[1]
        elif addr2[0] == '$':
            return line_num == len(self.lines)
        elif addr2[0] == 'regex':
            return bool(re.search(addr2[1], pattern_space))
        elif addr2[0] == '+':
            offset = addr2[1]
            return line_num >= start_line + offset

        return False

    def execute_s(self, cmd, pattern_space):
        """Execute s command."""
        regex = cmd[4]
        repl = cmd[5]
        flags = cmd[6]

        regex_flags = re.IGNORECASE if flags['i'] else 0
        compiled = re.compile(regex, regex_flags)

        # Find all matches
        matches = list(compiled.finditer(pattern_space))

        if not matches:
            return pattern_space

        # Determine which matches to replace
        start_match = flags['n'] if flags['n'] is not None else 1

        if flags['g']:
            # Replace all from start_match onwards
            replace_indices = set(range(start_match - 1, len(matches)))
        else:
            # Replace only start_match
            if start_match - 1 < len(matches):
                replace_indices = {start_match - 1}
            else:
                replace_indices = set()

        if not replace_indices:
            return pattern_space

        # Build result
        result = ''
        last_end = 0
        made_replacement = False

        for i, match in enumerate(matches):
            if i in replace_indices:
                # Add text before match
                result += pattern_space[last_end:match.start()]
                # Add replacement
                replacement_text = self.build_replacement(repl, match)
                result += replacement_text
                last_end = match.end()
                made_replacement = True
            else:
                # Skip this match for replacement
                pass

        # Add remaining text
        result += pattern_space[last_end:]

        if made_replacement and flags['p']:
            self.output.append(result)

        return result

    def build_replacement(self, repl, match):
        """Build replacement text from replacement pattern."""
        result = ''
        i = 0
        while i < len(repl):
            if repl[i] == '&':
                result += match.group(0)
                i += 1
            elif repl[i] == '\\' and i + 1 < len(repl):
                next_ch = repl[i + 1]
                if next_ch in '123456789':
                    group_num = int(next_ch)
                    group_text = match.group(group_num)
                    if group_text is None:
                        group_text = ''
                    result += group_text
                    i += 2
                elif next_ch == 'n':
                    result += '\n'
                    i += 2
                elif next_ch == 't':
                    result += '\t'
                    i += 2
                else:
                    result += next_ch
                    i += 2
            else:
                result += repl[i]
                i += 1
        return result

    def execute_y(self, cmd, pattern_space):
        """Execute y command."""
        src = cmd[4]
        dst = cmd[5]

        # Build translation table
        trans = {}
        for i, ch in enumerate(src):
            trans[ch] = dst[i]

        # Translate
        result = ''
        for ch in pattern_space:
            if ch in trans:
                result += trans[ch]
            else:
                result += ch

        return result


def run(script, text, quiet=False):
    """Run a sed-like script on text."""
    # Parse script
    parser = ScriptParser(script)
    commands = parser.parse()

    # Split text into lines
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()

    # Execute
    executor = ScriptExecutor(commands, lines, quiet)

    # Process lines
    for line_num, line in enumerate(lines, 1):
        if executor.process_line(line_num, line):
            break  # quit

    return '\n'.join(executor.output) + ('\n' if executor.output else '')
