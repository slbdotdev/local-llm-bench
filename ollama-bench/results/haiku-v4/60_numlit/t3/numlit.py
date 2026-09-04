"""numlit - numeric literal scanner and formatter."""


class NumError(ValueError):
    """Exception for numeric literal errors."""

    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind, pos)


def scan(text):
    """Scan numeric literals from space-separated string.

    Args:
        text: String containing space-separated numeric literals

    Returns:
        List of token records (dicts)

    Raises:
        NumError: If parsing fails
    """
    if not text:
        return []

    # Separator check (done first)
    if text[0] == ' ':
        raise NumError("space", 0)
    if text[-1] == ' ':
        raise NumError("space", len(text) - 1)

    for i in range(len(text) - 1):
        if text[i] == ' ' and text[i + 1] == ' ':
            raise NumError("space", i + 1)

    # Split by single space
    fields = text.split(' ')
    records = []

    # Track position in original text
    pos = 0
    for field in fields:
        record = _parse_field(field, pos, text)
        records.append(record)
        pos += len(field) + 1  # +1 for space

    return records


def _parse_field(field, start_pos, full_text):
    """Parse a single numeric literal field."""

    # A. Charset check
    valid_chars = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-+')
    for i, ch in enumerate(field):
        if ch not in valid_chars:
            raise NumError("char", start_pos + i)

    # B. Sign parsing
    p0 = 0
    sign = 1
    if field and field[0] in '+-':
        if field[0] == '-':
            sign = -1
        p0 = 1

    body = field[p0:]
    if not body:
        raise NumError("sign", start_pos)

    # C. Suffix check
    suffix = ""
    if body and body[-1] in 'uls':
        suffix = body[-1]
        body = body[:-1]
        if not body:
            raise NumError("suffix", start_pos + p0 + len(field) - 1)

    # Parse the body
    body_start = start_pos + p0
    return _parse_body(body, body_start, sign, suffix, start_pos)


def _parse_body(body, body_start, sign, suffix, field_start):
    """Parse the body part of a numeric literal."""

    # Check for radix prefixes
    is_radix = False
    radix = 10

    if len(body) >= 2 and body[0] == '0':
        if body[1] in 'xX':
            if body[1] == 'X':
                raise NumError("prefix", body_start + 1)
            is_radix = True
            radix = 16
            digits_start = 2
        elif body[1] in 'oO':
            if body[1] == 'O':
                raise NumError("prefix", body_start + 1)
            is_radix = True
            radix = 8
            digits_start = 2
        elif body[1] in 'bB':
            if body[1] == 'B':
                raise NumError("prefix", body_start + 1)
            is_radix = True
            radix = 2
            digits_start = 2

    if is_radix:
        # RADIX literal
        if digits_start >= len(body):
            raise NumError("prefix", body_start + digits_start)

        radix_digits = body[digits_start:]
        valid_radix_chars = {
            2: '01_',
            8: '01234567_',
            16: '0123456789abcdefABCDEF_'
        }

        for i, ch in enumerate(radix_digits):
            if ch not in valid_radix_chars[radix]:
                raise NumError("digit", body_start + digits_start + i)

        # Parse radix value
        clean_digits = radix_digits.replace('_', '')
        value = _parse_int_value(clean_digits, radix, sign)

        # Semantic checks for radix
        _check_underscore_radix(radix_digits, body_start + digits_start)

        # Canonical text for radix
        text = _canonical_radix_text(clean_digits, sign, radix, value)

        return {
            "kind": "int",
            "radix": radix,
            "value": value,
            "text": text,
            "suffix": suffix,
            "start": field_start
        }

    # DECIMAL literal
    intpart = ""
    i = 0
    while i < len(body) and body[i] in '0123456789_':
        intpart += body[i]
        i += 1

    fracpart = ""
    has_dot = False
    if i < len(body) and body[i] == '.':
        has_dot = True
        dot_pos = i
        i += 1
        while i < len(body) and body[i] in '0123456789_':
            fracpart += body[i]
            i += 1

    exppart = ""
    exp_sign = 1
    has_exp = False
    if i < len(body) and body[i] in 'eE':
        has_exp = True
        exp_pos = i
        i += 1
        if i < len(body) and body[i] in '+-':
            if body[i] == '-':
                exp_sign = -1
            i += 1
        while i < len(body) and body[i] in '0123456789_':
            exppart += body[i]
            i += 1

    # Check for leftover characters
    if i < len(body):
        raise NumError("syntax", body_start + i)

    # Semantic checks (in order)

    # 1. Underscore check
    _check_underscore_decimal(intpart, body_start)
    _check_underscore_decimal(fracpart, body_start + len(intpart) + (1 if has_dot else 0))
    if has_exp:
        exp_start = body_start + len(intpart) + (1 if has_dot else 0) + len(fracpart)
        if has_dot:
            exp_start += 1
        exp_start += 1  # skip 'e'
        if exp_sign == -1:
            exp_start += 1
        _check_underscore_decimal(exppart, exp_start)

    # 2. Dangling dot check
    if has_dot and not fracpart:
        raise NumError("dangling_dot", body_start + len(intpart))

    # 3. Exponent check
    if has_exp and not exppart:
        raise NumError("exponent", body_start + len(intpart) + (1 if has_dot else 0) + len(fracpart))

    # 4. Leading zero check (DECIMAL only, intpart)
    clean_intpart = intpart.replace('_', '')
    if clean_intpart and len(clean_intpart) >= 2 and clean_intpart[0] == '0':
        raise NumError("leading_zero", body_start)

    # Determine if float or int
    is_float = has_dot or has_exp

    # 5. Suffix check
    if suffix:
        if is_float and suffix in 'ul':
            # Float with u or l suffix
            raise NumError("suffix", body_start + len(intpart) + (1 if has_dot else 0) + len(fracpart) + (1 if has_exp else 0) + len(exppart))
        if not is_float and suffix == 's':
            # Int with s suffix
            raise NumError("suffix", body_start + len(intpart) + (1 if has_dot else 0) + len(fracpart) + (1 if has_exp else 0) + len(exppart))

    # Compute value
    if is_float:
        value = _parse_float_value(intpart, fracpart, exppart, exp_sign, sign)
    else:
        clean_int = clean_intpart if intpart else '0'
        value = sign * _string_to_int(clean_int, 10)

    # Canonical text
    if is_float:
        text = _canonical_float_text(intpart, fracpart, exppart, exp_sign, sign, value)
    else:
        if value == 0:
            text = "0"
        else:
            text = "-" + clean_intpart if sign == -1 else clean_intpart

    return {
        "kind": "float" if is_float else "int",
        "radix": 10,
        "value": value,
        "text": text,
        "suffix": suffix,
        "start": field_start
    }


def _check_underscore_decimal(part, start_pos):
    """Check underscore placement in a decimal digit run."""
    if not part:
        return

    for i, ch in enumerate(part):
        if ch == '_':
            # Check if between two digits
            left_ok = i > 0 and part[i - 1] in '0123456789'
            right_ok = i < len(part) - 1 and part[i + 1] in '0123456789'
            if not (left_ok and right_ok):
                raise NumError("underscore", start_pos + i)


def _check_underscore_radix(part, start_pos):
    """Check underscore placement in radix digits."""
    if not part:
        return

    for i, ch in enumerate(part):
        if ch == '_':
            # Check if between two digits
            left_ok = i > 0 and part[i - 1] != '_'
            right_ok = i < len(part) - 1 and part[i + 1] != '_'
            if not (left_ok and right_ok):
                raise NumError("underscore", start_pos + i)


def _parse_int_value(digits, radix, sign):
    """Parse integer value from digits in given radix."""
    value = _string_to_int(digits, radix)
    return sign * value


def _parse_float_value(intpart, fracpart, exppart, exp_sign, sign):
    """Parse float value using exact procedure."""
    clean_int = intpart.replace('_', '') or '0'
    clean_frac = fracpart.replace('_', '')
    clean_exp = exppart.replace('_', '') or '0'

    D = clean_int + clean_frac
    M = _string_to_int(D, 10)
    E = _string_to_int(clean_exp, 10) * exp_sign - len(clean_frac)

    if E >= 0:
        magnitude = M * (10.0 ** E)
    else:
        magnitude = M / (10.0 ** -E)

    return -magnitude if sign == -1 else magnitude


def _string_to_int(s, radix):
    """Convert string to int in given radix."""
    if not s:
        return 0
    result = 0
    for ch in s:
        if ch in '0123456789':
            digit = ord(ch) - ord('0')
        elif ch in 'abcdef':
            digit = ord(ch) - ord('a') + 10
        elif ch in 'ABCDEF':
            digit = ord(ch) - ord('A') + 10
        else:
            continue
        result = result * radix + digit
    return result


def _canonical_radix_text(digits, sign, radix, value):
    """Generate canonical text for radix literal."""
    if value == 0:
        prefix = '0x' if radix == 16 else ('0o' if radix == 8 else '0b')
        return prefix + '0'

    # Remove leading zeros
    digits_clean = digits.lstrip('0') or '0'

    prefix = '0x' if radix == 16 else ('0o' if radix == 8 else '0b')
    text = prefix + digits_clean.lower()

    if sign == -1:
        text = '-' + text

    return text


def _canonical_float_text(intpart, fracpart, exppart, exp_sign, sign, value):
    """Generate canonical text for float literal."""
    clean_int = intpart.replace('_', '') or '0'
    clean_frac = fracpart.replace('_', '')
    clean_exp = exppart.replace('_', '') or '0'

    # Determine sign
    if sign == -1 or (isinstance(value, float) and value < 0):
        sign_str = '-'
    else:
        sign_str = ''

    # Build text
    text = sign_str + clean_int + '.' + (clean_frac if clean_frac else '0')

    if exppart or fracpart:  # if there's an explicit exponent or if we need to show one
        # Only add exponent if original had one
        if exppart:
            exp_val = _string_to_int(clean_exp, 10) * exp_sign
            if exp_val < 0:
                text += 'e-' + _remove_leading_zeros(str(-exp_val))
            else:
                text += 'e' + _remove_leading_zeros(str(exp_val))
        else:
            # Check if original had exponent (exppart would be non-empty if it did)
            pass

    return text


def _remove_leading_zeros(s):
    """Remove leading zeros from string, keeping at least one."""
    if not s:
        return '0'
    stripped = s.lstrip('0')
    return stripped if stripped else '0'


def format_number(value, spec):
    """Format a number according to spec.

    Args:
        value: int or float to format
        spec: format specification string

    Returns:
        Formatted string

    Raises:
        NumError: If formatting fails
    """

    # Error check 1: type
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumError("type", -1)
    if not isinstance(spec, str):
        raise NumError("type", -1)

    # Error check 2: nonfinite
    if isinstance(value, float):
        if value != value:  # NaN
            raise NumError("nonfinite", -1)
        # Check for infinity: x * 0 != 0 for both +inf and -inf
        if value * 0 != 0:
            raise NumError("nonfinite", -1)

    # Parse spec
    fill_char = ' '
    align = '>'
    sign_mode = '-'
    use_grouping = False
    width = 0
    precision = 0
    rounding_mode = 'h'

    spec_str = spec
    idx = 0

    # Parse fill/align
    if len(spec_str) >= 2 and spec_str[1] in '<>^':
        fill_char = spec_str[0]
        align = spec_str[1]
        idx = 2
    elif len(spec_str) >= 1 and spec_str[0] in '<>^':
        align = spec_str[0]
        idx = 1

    # Parse sign
    if idx < len(spec_str) and spec_str[idx] in '+-' + ' ':
        sign_mode = spec_str[idx]
        idx += 1

    # Parse grouping
    if idx < len(spec_str) and spec_str[idx] == ',':
        use_grouping = True
        idx += 1

    # Parse width
    width_start = idx
    while idx < len(spec_str) and spec_str[idx].isdigit():
        idx += 1

    if width_start < idx:
        width_str = spec_str[width_start:idx]
        if width_str[0] == '0':
            raise NumError("spec", -1)
        width = _string_to_int(width_str, 10)
        if width > 200:
            raise NumError("spec", -1)

    # Parse precision
    if idx < len(spec_str) and spec_str[idx] == '.':
        idx += 1
        prec_start = idx
        while idx < len(spec_str) and spec_str[idx].isdigit():
            idx += 1

        if prec_start == idx:
            raise NumError("spec", -1)

        precision_str = spec_str[prec_start:idx]
        precision = _string_to_int(precision_str, 10)
        if precision > 20:
            raise NumError("spec", -1)

    # Parse mode
    if idx < len(spec_str):
        if spec_str[idx] in 'hudf':
            rounding_mode = spec_str[idx]
            idx += 1

        # Check for extra characters
        if idx < len(spec_str):
            raise NumError("spec", -1)

    # Determine if value is negative (including -0.0)
    is_negative = _is_negative(value)

    # Format the number
    if isinstance(value, float):
        # Round to precision decimal places
        rounded = _round_float(value, precision, rounding_mode)
        # Check if rounded value is negative
        is_negative = is_negative or _is_negative(rounded)
    else:
        rounded = value

    # Render integer and fractional parts (without sign)
    int_part, frac_part = _split_unsigned_number(rounded, precision, is_negative)

    # Add grouping to integer part if needed
    if use_grouping:
        int_part = _add_grouping(int_part)

    # Build the number string
    if precision > 0:
        num_str = int_part + '.' + frac_part
    else:
        num_str = int_part

    # Add sign
    if sign_mode == '+':
        if is_negative:
            num_str = '-' + num_str
        else:
            num_str = '+' + num_str
    elif sign_mode == ' ':
        if is_negative:
            num_str = '-' + num_str
        else:
            num_str = ' ' + num_str
    else:  # '-'
        if is_negative:
            num_str = '-' + num_str

    # Add padding
    if len(num_str) < width:
        padding_needed = width - len(num_str)
        if align == '<':
            num_str = num_str + fill_char * padding_needed
        elif align == '^':
            left_pad = padding_needed // 2
            right_pad = padding_needed - left_pad
            num_str = fill_char * left_pad + num_str + fill_char * right_pad
        else:  # '>'
            num_str = fill_char * padding_needed + num_str

    return num_str


def _round_float(value, precision, mode):
    """Round a float to given precision and return the rounded float."""
    multiplier = 10 ** precision

    # For integers, no rounding needed
    if isinstance(value, int):
        return value

    # Work with absolute value for rounding
    abs_val = abs(value)
    scaled = abs_val * multiplier

    if mode == 'h':  # half-even
        int_scaled = _round_half_even_int(scaled)
    elif mode == 'u':  # half-up (away from zero)
        int_scaled = _round_half_up_int(scaled)
    elif mode == 'd':  # truncate toward zero
        int_scaled = _floor_float(scaled)
    elif mode == 'f':  # floor toward negative infinity
        int_scaled = _floor_float(scaled)
    else:
        int_scaled = _round_half_even_int(scaled)

    # Convert back to float
    result = int_scaled / multiplier
    if value < 0:
        result = -result
    return result


def _round_half_even_int(scaled):
    """Round to nearest even (return int)."""
    lower = _floor_float(scaled)
    upper = lower + 1

    mid = lower + 0.5
    if scaled < mid:
        return lower
    elif scaled > mid:
        return upper
    else:
        # Tie - round to even
        if lower % 2 == 0:
            return lower
        else:
            return upper


def _round_half_up_int(scaled):
    """Round half-up (away from zero) - return int."""
    return _floor_float(scaled + 0.5)


def _floor_float(x):
    """Floor function using integer arithmetic."""
    if x >= 0:
        return x.__floor__()
    else:
        result = x.__floor__()
        if result == x:
            return result
        return result


def _is_negative(value):
    """Check if value is negative, including -0.0."""
    if isinstance(value, float):
        # Check for negative zero
        return value < 0 or (value == 0 and _is_negative_zero_float(value))
    else:
        return value < 0


def _is_negative_zero_float(f):
    """Check if float is negative zero."""
    # Negative zero has a sign bit set but is equal to 0
    # The string representation of -0.0 starts with '-'
    return f == 0 and str(f).startswith('-')


def _split_unsigned_number(value, precision, is_negative):
    """Split rounded number into unsigned integer and fractional parts."""
    # Work with absolute value
    abs_value = abs(value)

    if isinstance(value, float):
        multiplier = 10 ** precision
        scaled = abs_value * multiplier

        # The value should already be rounded, so just extract digits
        int_scaled = _floor_float(scaled)

        # Get integer and fractional parts
        if precision == 0:
            return (str(int_scaled), '')
        else:
            digits = str(int_scaled)
            if len(digits) <= precision:
                frac_str = '0' * (precision - len(digits)) + digits
                int_str = '0'
            else:
                split_pos = len(digits) - precision
                int_str = digits[:split_pos]
                frac_str = digits[split_pos:]

            return (int_str, frac_str)
    else:
        return (str(abs_value), '0' * precision)


def _add_grouping(int_str):
    """Add comma grouping to unsigned integer string."""
    # Group from right
    result = []
    for i, digit in enumerate(reversed(int_str)):
        if i > 0 and i % 3 == 0:
            result.append(',')
        result.append(digit)

    return ''.join(reversed(result))
