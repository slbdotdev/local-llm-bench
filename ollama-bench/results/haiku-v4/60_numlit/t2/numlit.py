class NumError(ValueError):
    """Exception for numeric literal parsing errors."""
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__()


def scan(text):
    """Parse numeric literals from a string separated by single spaces."""
    if not text:
        return []

    # Separator check - done FIRST
    if text[0] == ' ':
        raise NumError("space", 0)
    if text[-1] == ' ':
        raise NumError("space", len(text) - 1)

    # Check for consecutive spaces
    for i in range(len(text) - 1):
        if text[i] == ' ' and text[i + 1] == ' ':
            raise NumError("space", i + 1)

    # Split by spaces and parse each field
    fields = text.split(' ')
    records = []
    offset = 0

    for field in fields:
        record = _parse_field(field, offset)
        records.append(record)
        offset += len(field) + 1  # +1 for the space separator

    return records


def _parse_field(field, start_offset):
    """Parse a single numeric literal field."""
    p0 = start_offset
    pos = 0

    # A. Charset check
    valid_chars = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-+')
    for i, ch in enumerate(field):
        if ch not in valid_chars:
            raise NumError("char", p0 + i)

    # B. Sign
    sign = 1
    if pos < len(field) and field[pos] in '+-':
        if field[pos] == '-':
            sign = -1
        pos += 1

    # Check if body is empty
    if pos >= len(field):
        raise NumError("sign", p0)

    body_start = pos

    # C. Suffix
    suffix = ""
    suffix_pos = -1
    if len(field) > pos and field[-1] in 'uls':
        suffix = field[-1]
        suffix_pos = len(field) - 1
        field = field[:-1]
        if pos >= len(field):
            raise NumError("suffix", p0 + suffix_pos)

    # D. Structural scan
    body = field[body_start:]

    if len(body) >= 2 and body[0] == '0' and body[1] in 'XOB':
        raise NumError("prefix", p0 + body_start + 1)

    is_radix = False
    radix = 10
    is_float = False

    if len(body) >= 2 and body[0] == '0' and body[1] in 'xob':
        is_radix = True
        if body[1] == 'x':
            radix = 16
        elif body[1] == 'o':
            radix = 8
        else:  # 'b'
            radix = 2

        digits_part = body[2:]
        if not digits_part:
            raise NumError("prefix", p0 + body_start + 2)

        # Validate radix digits
        for i, ch in enumerate(digits_part):
            if radix == 16:
                if ch not in '0123456789abcdefABCDEF_':
                    raise NumError("digit", p0 + body_start + 2 + i)
            elif radix == 8:
                if ch not in '01234567_':
                    raise NumError("digit", p0 + body_start + 2 + i)
            else:  # radix == 2
                if ch not in '01_':
                    raise NumError("digit", p0 + body_start + 2 + i)

        # Check underscores in radix literals
        for i, ch in enumerate(digits_part):
            if ch == '_':
                if i == 0 or i == len(digits_part) - 1:
                    raise NumError("underscore", p0 + body_start + 2 + i)
                if digits_part[i-1] == '_' or digits_part[i+1] == '_':
                    raise NumError("underscore", p0 + body_start + 2 + i)

        digits_str = digits_part.replace('_', '')
        value = _parse_radix_int(digits_str, radix, sign)
    else:
        # Decimal literal
        intpart = ""
        fracpart = ""
        exppart = ""
        exp_sign = 1
        has_dot = False
        has_exp = False

        # Consume intpart
        i = 0
        while i < len(body) and body[i] in '0123456789_':
            intpart += body[i]
            i += 1

        # Check for dot
        dot_pos = -1
        if i < len(body) and body[i] == '.':
            has_dot = True
            dot_pos = i
            i += 1
            # Consume fracpart
            while i < len(body) and body[i] in '0123456789_':
                fracpart += body[i]
                i += 1

        # Check for exponent
        exp_pos = -1
        if i < len(body) and body[i] in 'eE':
            has_exp = True
            exp_pos = i
            i += 1
            # Optional sign
            if i < len(body) and body[i] in '+-':
                if body[i] == '-':
                    exp_sign = -1
                i += 1
            # Consume exponent digits
            while i < len(body) and body[i] in '0123456789_':
                exppart += body[i]
                i += 1

        # Check if anything is left
        if i < len(body):
            raise NumError("syntax", p0 + body_start + i)

        # E. Semantic checks
        # 1. Underscore check
        for part_name, part in [("int", intpart), ("frac", fracpart), ("exp", exppart)]:
            for i, ch in enumerate(part):
                if ch == '_':
                    # Must be strictly between two digits
                    if i == 0 or i == len(part) - 1:
                        raise NumError("underscore", p0 + body_start + _find_char_in_body(body, part_name, i))
                    if part[i-1] == '_' or part[i+1] == '_':
                        raise NumError("underscore", p0 + body_start + _find_char_in_body(body, part_name, i))

        # 2. Dangling dot
        if has_dot and not fracpart:
            raise NumError("dangling_dot", p0 + body_start + dot_pos)

        # 3. Exponent without digits
        if has_exp and not exppart:
            raise NumError("exponent", p0 + body_start + exp_pos)

        # 4. Leading zero in intpart
        intpart_clean = intpart.replace('_', '')
        if intpart_clean and len(intpart_clean) >= 2 and intpart_clean[0] == '0':
            raise NumError("leading_zero", p0 + body_start)

        # Determine if float or int
        is_float = has_dot or has_exp

        # 5. Suffix check
        if suffix:
            if is_float:
                # No suffixes allowed on floats (u, l, s all error)
                raise NumError("suffix", p0 + suffix_pos)

        # Compute value
        if is_float:
            radix = 10
            M_str = (intpart if intpart else '0').replace('_', '') + fracpart.replace('_', '')
            M = _str_to_int(M_str) if M_str else 0
            E = (exp_sign * _str_to_int(exppart.replace('_', ''))) if exppart else 0
            E -= len(fracpart.replace('_', ''))

            if E >= 0:
                value = sign * (M * (10.0 ** E))
            else:
                value = sign * (M / (10.0 ** (-E)))
        else:
            radix = 10
            intpart_clean = intpart.replace('_', '')
            value = sign * (_str_to_int(intpart_clean) if intpart_clean else 0)

    # Build canonical text
    if not is_radix:
        text = _canonical_text(value, radix, is_float, body, intpart, fracpart, exppart, exp_sign if is_float and has_exp else 1, sign)
    else:
        text = _canonical_text(value, radix, is_float, body, "", "", "", 1, sign)

    record = {
        "kind": "float" if is_float else "int",
        "radix": radix,
        "value": value,
        "text": text,
        "suffix": suffix,
        "start": p0
    }

    return record


def _find_char_in_body(body, part_name, idx):
    """Find position of a character in the given part of body."""
    count = 0
    i = 0
    in_intpart = True
    has_dot = '.' in body
    has_exp = 'e' in body or 'E' in body

    for i, ch in enumerate(body):
        if ch == '.':
            in_intpart = False
        elif ch in 'eE':
            in_intpart = False
        elif in_intpart and part_name == "int":
            if ch in '0123456789_':
                if count == idx:
                    return i
                count += 1
        elif not in_intpart and ch != '.' and ch not in 'eE' and part_name == "frac":
            if ch in '0123456789_':
                if count == idx:
                    return i
                count += 1

    return i


def _str_to_int(s):
    """Convert a string of digits to an integer without using int()."""
    result = 0
    for ch in s:
        result = result * 10 + (ord(ch) - ord('0'))
    return result


def _parse_radix_int(digits_str, radix, sign):
    """Parse digits in given radix."""
    result = 0
    for ch in digits_str:
        if ch in '0123456789':
            digit = ord(ch) - ord('0')
        else:
            digit = ord(ch.lower()) - ord('a') + 10
        result = result * radix + digit
    return sign * result


def _canonical_text(value, radix, is_float, body, intpart, fracpart, exppart, exp_sign, sign):
    """Generate canonical text representation."""
    if radix != 10:
        # Radix literal
        is_negative = value < 0
        abs_val = -value if is_negative else value

        # Convert to radix
        if abs_val == 0:
            digits = '0'
        else:
            digits = ""
            temp = abs_val
            while temp > 0:
                d = temp % radix
                if d < 10:
                    digits = chr(ord('0') + d) + digits
                else:
                    digits = chr(ord('a') + d - 10) + digits
                temp //= radix

        prefix = '0x' if radix == 16 else ('0o' if radix == 8 else '0b')
        sign_str = '-' if is_negative else ''
        return sign_str + prefix + digits

    if is_float:
        # Float literal - check negative including -0.0
        # Use the sign that was parsed, which correctly handles -0.0
        is_negative = (value < 0) or (value == 0.0 and sign < 0)
        abs_val = -value if is_negative else value

        sign_str = '-' if is_negative else ''

        # Ensure intpart is not empty
        if not intpart:
            intpart_canon = '0'
        else:
            intpart_canon = intpart.replace('_', '')

        # Ensure fracpart - if no fracpart but has exponent, use '0'
        if not fracpart and ('e' in body or 'E' in body):
            fracpart_canon = '0'
        else:
            fracpart_canon = fracpart.replace('_', '') if fracpart else '0'

        # Build canonical form
        result = sign_str + intpart_canon + '.' + fracpart_canon

        if exppart or 'e' in body or 'E' in body:
            # Compute exponent value
            exp_val = 0
            if exppart:
                exp_val = exp_sign * _str_to_int(exppart.replace('_', ''))

            if exp_val < 0:
                result += 'e' + str(exp_val)
            else:
                result += 'e' + str(exp_val)

        return result

    # Integer literal (decimal)
    is_negative = value < 0
    abs_val = -value if is_negative else value

    if abs_val == 0:
        return "0"

    digits = ""
    temp = abs_val
    while temp > 0:
        digits = chr(ord('0') + (temp % 10)) + digits
        temp //= 10

    sign_str = '-' if is_negative else ''
    return sign_str + digits


def format_number(value, spec):
    """Format a number according to the spec."""
    # Type check (must be int or float, not bool)
    if isinstance(value, bool):
        raise NumError("type", -1)
    if not isinstance(value, (int, float)):
        raise NumError("type", -1)
    if not isinstance(spec, str):
        raise NumError("type", -1)

    # Nonfinite check
    if isinstance(value, float):
        # NaN check: x != x is true only for NaN
        # Infinity check: x > 1e308 or x < -1e308 (max finite float is ~1.8e308)
        if value != value or value > 1e308 or value < -1e308:
            raise NumError("nonfinite", -1)

    # Parse spec
    parsed_spec = _parse_spec(spec)

    # Round and format the number
    result = _format_with_spec(value, parsed_spec)

    return result


def _parse_spec(spec):
    """Parse the format spec string."""
    pos = 0
    fill = ' '
    align = '>'
    sign = '-'
    use_comma = False
    width = 0
    precision = 0
    mode = 'h'

    # Check for fill/align
    if len(spec) >= 2 and spec[1] in '<>^':
        fill = spec[0]
        align = spec[1]
        pos = 2
    elif len(spec) >= 1 and spec[0] in '<>^':
        align = spec[0]
        pos = 1

    # Check for sign
    if pos < len(spec) and spec[pos] in '+-' + ' ':
        sign = spec[pos]
        pos += 1

    # Check for comma
    if pos < len(spec) and spec[pos] == ',':
        use_comma = True
        pos += 1

    # Check for width
    width_start = pos
    while pos < len(spec) and spec[pos].isdigit():
        pos += 1
    if width_start < pos:
        width_str = spec[width_start:pos]
        if width_str[0] == '0':
            raise NumError("spec", -1)
        width = _str_to_int(width_str)
        if width > 200:
            raise NumError("spec", -1)

    # Check for precision
    if pos < len(spec) and spec[pos] == '.':
        pos += 1
        prec_start = pos
        while pos < len(spec) and spec[pos].isdigit():
            pos += 1
        if prec_start == pos:
            raise NumError("spec", -1)
        precision = _str_to_int(spec[prec_start:pos])
        if precision > 20:
            raise NumError("spec", -1)

    # Check for mode
    if pos < len(spec) and spec[pos] in 'hudf':
        mode = spec[pos]
        pos += 1

    # Check for trailing characters
    if pos < len(spec):
        raise NumError("spec", -1)

    return {
        'fill': fill,
        'align': align,
        'sign': sign,
        'comma': use_comma,
        'width': width,
        'precision': precision,
        'mode': mode
    }


def _format_with_spec(value, spec):
    """Format value according to parsed spec."""
    is_negative = value < 0
    if isinstance(value, float) and value == 0.0:
        # Detect negative zero by checking string representation
        is_negative = '-' in str(value)

    # Round to precision, handling sign correctly
    if isinstance(value, float):
        if spec['mode'] == 'f':
            # Floor mode must use signed value (rounds toward -infinity, not magnitude)
            if spec['precision'] == 0:
                rounded = _floor_round(value)
                int_part = rounded
                frac_str = ''
            else:
                factor = 10 ** spec['precision']
                scaled = value * factor
                rounded = _floor_round(scaled)

                # For a floor-rounded integer, extract the actual fractional value
                # by dividing back: the fractional part is what's left after removing the integer part
                is_negative_val = rounded < 0
                abs_rounded = -rounded if is_negative_val else rounded
                int_part = abs_rounded // factor
                remainder = abs_rounded % factor
                frac_str = _int_to_frac_str(remainder, spec['precision'])

            # Take absolute value for display, sign handled separately
            int_part = abs(int_part) if spec['precision'] == 0 else int_part
            result_negative = value < 0 or is_negative
        else:
            # Other modes: round absolute value, then apply sign
            abs_val = -value if is_negative else value
            if spec['precision'] == 0:
                int_part = _round_float(abs_val, 0, spec['mode'])
                frac_str = ''
            else:
                int_part, frac_str = _round_float_to_frac(abs_val, spec['precision'], spec['mode'])
            result_negative = is_negative
    else:
        # Integer
        abs_val = -value if is_negative else value
        int_part = abs_val
        frac_str = '0' * spec['precision'] if spec['precision'] > 0 else ''
        result_negative = is_negative

    # Format integer part
    if int_part == 0:
        int_str = '0'
    else:
        int_str = ""
        temp = int_part
        while temp > 0:
            int_str = chr(ord('0') + (temp % 10)) + int_str
            temp //= 10

    # Add commas
    if spec['comma']:
        int_str = _add_commas(int_str)

    # Build number string
    if spec['precision'] > 0:
        num_str = int_str + '.' + frac_str
    else:
        num_str = int_str

    # Add sign
    if result_negative:
        num_str = '-' + num_str
    elif spec['sign'] == '+':
        num_str = '+' + num_str
    elif spec['sign'] == ' ':
        num_str = ' ' + num_str

    # Pad to width
    if spec['width'] > 0 and len(num_str) < spec['width']:
        padding = spec['width'] - len(num_str)
        if spec['align'] == '<':
            num_str = num_str + spec['fill'] * padding
        elif spec['align'] == '>':
            num_str = spec['fill'] * padding + num_str
        else:  # center
            left_pad = padding // 2
            right_pad = padding - left_pad
            num_str = spec['fill'] * left_pad + num_str + spec['fill'] * right_pad

    return num_str


def _round_float(value, precision, mode):
    """Round a float value."""
    if precision == 0:
        if mode == 'h':
            return _half_even_round(value)
        elif mode == 'u':
            return _half_up_round(value)
        elif mode == 'd':
            return _toward_zero_round(value)
        else:  # 'f'
            return _floor_round(value)
    else:
        factor = 10 ** precision
        scaled = value * factor
        if mode == 'h':
            rounded = _half_even_round(scaled)
        elif mode == 'u':
            rounded = _half_up_round(scaled)
        elif mode == 'd':
            rounded = _toward_zero_round(scaled)
        else:  # 'f'
            rounded = _floor_round(scaled)
        return rounded // factor


def _round_float_to_frac(value, precision, mode):
    """Round a float and return integer and fractional parts."""
    factor = 10 ** precision
    scaled = value * factor

    if mode == 'h':
        rounded = _half_even_round(scaled)
    elif mode == 'u':
        rounded = _half_up_round(scaled)
    elif mode == 'd':
        rounded = _toward_zero_round(scaled)
    else:  # 'f'
        rounded = _floor_round(scaled)

    int_part = rounded // factor
    frac_part = rounded % factor

    # For negative numbers, handle remainder correctly
    if rounded < 0 and frac_part != 0:
        int_part -= 1
        frac_part = factor + frac_part

    frac_str = _int_to_frac_str(frac_part, precision)

    return int_part, frac_str


def _half_even_round(value):
    """Round to nearest integer, ties to even."""
    lower = _floor_round(value)
    upper = lower + 1
    mid = lower + 0.5

    if value < mid:
        return lower
    elif value > mid:
        return upper
    else:
        if lower % 2 == 0:
            return lower
        else:
            return upper


def _half_up_round(value):
    """Round to nearest integer, ties away from zero."""
    lower = _floor_round(value)
    mid = lower + 0.5

    if value < mid:
        return lower
    else:
        return lower + 1


def _toward_zero_round(value):
    """Round toward zero (truncate)."""
    if value >= 0:
        return _floor_round(value)
    else:
        return -_floor_round(-value)


def _floor_round(value):
    """Round toward negative infinity."""
    if value >= 0:
        result = 0
        while result + 1 <= value:
            result += 1
        return result
    else:
        result = -1
        while result > value:
            result -= 1
        return result


def _int_to_frac_str(frac_part, precision):
    """Convert fractional part to string with padding."""
    s = ""
    temp = frac_part
    for _ in range(precision):
        s = chr(ord('0') + (temp % 10)) + s
        temp //= 10
    return s


def _add_commas(int_str):
    """Add comma separators to integer string."""
    result = ""
    for i, ch in enumerate(reversed(int_str)):
        if i > 0 and i % 3 == 0:
            result = ',' + result
        result = ch + result
    return result
