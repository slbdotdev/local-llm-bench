"""Numeric literal scanner and formatter."""
import math


class NumError(ValueError):
    """Exception for numeric literal errors."""

    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind, pos)


def scan(text):
    """Scan numeric literals from text."""
    if not text:
        return []

    # Separator check first
    if text[0] == " ":
        raise NumError("space", 0)
    if text[-1] == " ":
        raise NumError("space", len(text) - 1)
    for i in range(len(text) - 1):
        if text[i] == " " and text[i + 1] == " ":
            raise NumError("space", i + 1)

    # Split by space and parse each field
    fields = text.split(" ")
    records = []
    pos = 0

    for field in fields:
        record = _parse_field(field, pos)
        records.append(record)
        pos += len(field) + 1

    return records


def _parse_field(field, start_pos):
    """Parse a single field into a record."""
    p0 = start_pos
    pos = 0

    # A. Charset check
    allowed = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-+")
    for i, ch in enumerate(field):
        if ch not in allowed:
            raise NumError("char", start_pos + i)

    # B. Sign
    sign = 1
    if pos < len(field) and field[pos] in "+-":
        if field[pos] == "-":
            sign = -1
        pos += 1

    if pos >= len(field):
        raise NumError("sign", p0)

    # C. Suffix
    suffix = ""
    suffix_pos = -1
    body_end = len(field)
    if field[-1] in "uls":
        suffix = field[-1]
        suffix_pos = start_pos + len(field) - 1
        body_end = len(field) - 1

    if pos >= body_end:
        raise NumError("suffix", suffix_pos)

    # D. Structural scan
    body = field[pos:body_end]
    body_pos = start_pos + pos

    # Check for uppercase radix prefix
    if len(body) >= 2 and body[0] == "0" and body[1] in "XOB":
        raise NumError("prefix", body_pos + 1)

    # Check for lowercase radix prefix
    if len(body) >= 2 and body[0] == "0" and body[1] in "xob":
        radix = {"x": 16, "o": 8, "b": 2}[body[1]]
        if len(body) == 2:
            raise NumError("prefix", body_pos + 2)

        radix_digits = body[2:]
        # Check all chars are valid for radix
        for i, ch in enumerate(radix_digits):
            if radix == 2 and ch not in "01_":
                raise NumError("digit", body_pos + 2 + i)
            elif radix == 8 and ch not in "01234567_":
                raise NumError("digit", body_pos + 2 + i)
            elif radix == 16 and ch not in "0123456789abcdefABCDEF_":
                raise NumError("digit", body_pos + 2 + i)

        # Parse radix number
        value = _parse_radix(radix_digits, radix)
        if sign == -1:
            value = -value

        text = _canonical_int(value, radix)
        return {
            "kind": "int",
            "radix": radix,
            "value": value,
            "text": text,
            "suffix": suffix,
            "start": p0,
        }

    # Decimal number
    intpart = ""
    fracpart = ""
    exppart = ""
    i = 0

    while i < len(body) and body[i] in "0123456789_":
        intpart += body[i]
        i += 1

    if i < len(body) and body[i] == ".":
        i += 1
        while i < len(body) and body[i] in "0123456789_":
            fracpart += body[i]
            i += 1

    if i < len(body) and body[i] in "eE":
        i += 1
        if i < len(body) and body[i] in "+-":
            exppart += body[i]
            i += 1
        while i < len(body) and body[i] in "0123456789_":
            exppart += body[i]
            i += 1

    if i < len(body):
        raise NumError("syntax", body_pos + i)

    # E. Semantic checks
    # 1. Underscore check
    _check_underscores(intpart, body_pos)
    dot_offset = len(intpart) + (1 if "." in body else 0)
    _check_underscores(fracpart, body_pos + dot_offset)

    # For exponent part, extract just the digits
    if "e" in body or "E" in body:
        exp_idx = body.find("e")
        if exp_idx == -1:
            exp_idx = body.find("E")
        exp_str = body[exp_idx + 1 :]
        # Skip the optional +/- sign
        exp_digits_start = 0
        if exp_str and exp_str[0] in "+-":
            exp_digits_start = 1
        exp_digits = exp_str[exp_digits_start:]
        exp_offset = body_pos + exp_idx + 1 + exp_digits_start
        _check_underscores(exp_digits, exp_offset)

    # 2. Dangling dot
    if "." in body and fracpart == "":
        raise NumError("dangling_dot", body_pos + body.find("."))

    # 3. Exponent
    has_exp = "e" in body or "E" in body
    if has_exp:
        exp_idx = body.find("e")
        if exp_idx == -1:
            exp_idx = body.find("E")
        # Check if expdigits is empty (only +/- after e)
        exp_str = body[exp_idx + 1 :]
        exp_digits = exp_str.lstrip("+-").replace("_", "")
        if exp_digits == "":
            raise NumError("exponent", body_pos + exp_idx)

    # 4. Leading zero (decimal only)
    intpart_clean = intpart.replace("_", "")
    if intpart_clean and len(intpart_clean) >= 2 and intpart_clean[0] == "0":
        raise NumError("leading_zero", body_pos)

    # 5. Suffix check
    is_float = "." in body or has_exp
    if suffix:
        if is_float and suffix in "ul":
            raise NumError("suffix", suffix_pos)
        if not is_float and suffix == "s":
            raise NumError("suffix", suffix_pos)

    # Parse value
    fracpart_clean = fracpart.replace("_", "")
    exppart_clean = exppart.replace("_", "")

    if is_float:
        value = _parse_float(intpart_clean, fracpart_clean, exppart_clean, sign)
        text = _canonical_float(value, intpart_clean, fracpart_clean, exppart_clean)
    else:
        value = _parse_int(intpart_clean, sign)
        text = _canonical_int(value, 10)

    return {
        "kind": "float" if is_float else "int",
        "radix": 10,
        "value": value,
        "text": text,
        "suffix": suffix,
        "start": p0,
    }


def _check_underscores(part, part_offset):
    """Check that underscores in a part are strictly between two digits."""
    if not part:
        return

    for i, ch in enumerate(part):
        if ch == "_":
            # Underscore must be strictly between two digits
            # Check if it's at the boundary
            if i == 0 or i == len(part) - 1:
                raise NumError("underscore", part_offset + i)
            # Check if neighbors are both digits
            if not (part[i - 1].isdigit() and part[i + 1].isdigit()):
                raise NumError("underscore", part_offset + i)


def _parse_int(digits_str, sign):
    """Parse integer from clean digit string."""
    if not digits_str:
        return 0
    value = 0
    for ch in digits_str:
        value = value * 10 + (ord(ch) - ord("0"))
    return value * sign


def _parse_radix(digits_str, radix):
    """Parse radix number."""
    clean = digits_str.replace("_", "")
    if not clean:
        return 0
    value = 0
    for ch in clean:
        if ch in "0123456789":
            digit = ord(ch) - ord("0")
        elif ch in "abcdef":
            digit = ord(ch) - ord("a") + 10
        else:
            digit = ord(ch) - ord("A") + 10
        value = value * radix + digit
    return value


def _parse_float(intpart, fracpart, exppart, sign):
    """Parse float using exact procedure."""
    # Combine digits
    if not intpart:
        intpart = "0"
    d = intpart + fracpart

    # Parse as integer
    m = 0
    for ch in d:
        m = m * 10 + (ord(ch) - ord("0"))

    # Calculate exponent
    e = 0
    if exppart:
        # exppart might have + or - at start
        exp_str = exppart
        if exp_str[0] in "+-":
            exp_sign = 1 if exp_str[0] == "+" else -1
            exp_str = exp_str[1:]
        else:
            exp_sign = 1
        e = 0
        for ch in exp_str:
            e = e * 10 + (ord(ch) - ord("0"))
        e = e * exp_sign

    e = e - len(fracpart)

    # Compute magnitude
    if e >= 0:
        mag = m * (10.0 ** e)
    else:
        mag = m / (10.0 ** (-e))

    # Apply sign
    if sign == -1:
        mag = -mag

    return mag


def _canonical_int(value, radix):
    """Get canonical text for integer."""
    if value == 0:
        if radix == 10:
            return "0"
        else:
            prefix = {16: "0x", 8: "0o", 2: "0b"}[radix]
            return prefix + "0"

    is_negative = value < 0
    abs_val = value if value >= 0 else -value

    if radix == 10:
        digits = ""
        v = abs_val
        while v > 0:
            digits = str(v % 10) + digits
            v = v // 10
        if is_negative:
            return "-" + digits
        return digits
    else:
        # Convert to base
        digits = ""
        v = abs_val
        base_map = {16: "0123456789abcdef", 8: "01234567", 2: "01"}
        base_str = base_map[radix]
        while v > 0:
            digits = base_str[v % radix] + digits
            v = v // radix

        # Strip leading zeros
        digits = digits.lstrip("0") or "0"

        prefix = {16: "0x", 8: "0o", 2: "0b"}[radix]
        if is_negative:
            return "-" + prefix + digits
        return prefix + digits


def _canonical_float(value, intpart, fracpart, exppart):
    """Get canonical text for float."""
    # Check if value is negative (including -0.0)
    is_negative = value < 0.0 or (value == 0.0 and _is_negative_zero(value))

    # Get integer part
    int_str = intpart if intpart else "0"

    # Get fraction part
    frac_str = fracpart if fracpart else "0"

    # Get exponent part
    exp_str = ""
    if exppart:
        if exppart[0] in "+-":
            exp_sign = exppart[0]
            exp_digits = exppart[1:]
        else:
            exp_sign = ""
            exp_digits = exppart

        exp_val = 0
        for ch in exp_digits:
            exp_val = exp_val * 10 + (ord(ch) - ord("0"))

        if exp_sign == "-":
            exp_str = "e-" + str(exp_val)
        else:
            exp_str = "e" + str(exp_val)

    # Build canonical form
    result = ""
    if is_negative:
        result += "-"
    result += int_str + "." + frac_str
    result += exp_str

    return result


def _is_negative_zero(value):
    """Check if a float value is negative zero."""
    if value != 0.0:
        return False
    # Use math.copysign to check the sign bit
    return math.copysign(1.0, value) < 0


def format_number(value, spec):
    """Format a number according to spec."""
    # Type check
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumError("type", -1)
    if not isinstance(spec, str):
        raise NumError("type", -1)

    # Nonfinite check
    if isinstance(value, float):
        if math.isnan(value):
            raise NumError("nonfinite", -1)
        if math.isinf(value):
            raise NumError("nonfinite", -1)

    # Parse spec
    try:
        fill, align, use_comma, width, precision, sign, mode = _parse_spec(spec)
    except (ValueError, IndexError):
        raise NumError("spec", -1)

    # Determine if value is negative
    is_negative = value < 0 or (isinstance(value, float) and value == 0.0 and _is_negative_zero(value))

    # Get sign character
    if sign == "-":  # Default
        sign_char = "-" if is_negative else ""
    elif sign == "+":
        sign_char = "-" if is_negative else "+"
    elif sign == " ":
        sign_char = "-" if is_negative else " "
    else:
        sign_char = ""

    # Round to precision (this handles negative values internally)
    rounded_int, rounded_frac = _round_number(value, precision, mode)

    # Format the integer part (use absolute value)
    abs_int = rounded_int if rounded_int >= 0 else -rounded_int
    int_str = str(abs_int)

    # Apply comma grouping to integer part
    if use_comma:
        int_str = _group_with_commas(int_str)

    # Build the number string
    if precision > 0:
        frac_str = str(rounded_frac).zfill(precision)
        number_str = int_str + "." + frac_str
    else:
        number_str = int_str

    # Combine sign and number
    result = sign_char + number_str

    # Apply padding
    if width > 0 and len(result) < width:
        padding_len = width - len(result)

        if align == "<":
            result = result + fill * padding_len
        elif align == "^":
            left_pad = padding_len // 2
            right_pad = padding_len - left_pad
            result = fill * left_pad + result + fill * right_pad
        else:  # align == ">" (default)
            result = fill * padding_len + result

    return result


def _parse_spec(spec):
    """Parse format spec string."""
    if not spec:
        return " ", ">", False, 0, 0, "-", "h"

    pos = 0

    # Parse fill/align
    fill = " "
    align = ">"
    if len(spec) >= 2 and spec[1] in "<>^":
        fill = spec[0]
        align = spec[1]
        pos = 2
    elif len(spec) >= 1 and spec[0] in "<>^":
        align = spec[0]
        pos = 1

    # Parse sign
    sign = "-"
    if pos < len(spec) and spec[pos] in "+-":
        sign = spec[pos]
        pos += 1
    elif pos < len(spec) and spec[pos] == " ":
        sign = " "
        pos += 1

    # Parse comma
    use_comma = False
    if pos < len(spec) and spec[pos] == ",":
        use_comma = True
        pos += 1

    # Parse width
    width = 0
    width_start = pos
    while pos < len(spec) and spec[pos].isdigit():
        width = width * 10 + (ord(spec[pos]) - ord("0"))
        pos += 1

    # Check for leading zero in width
    if width_start < pos and spec[width_start] == "0":
        raise ValueError("width with leading zero")
    if width > 200:
        raise ValueError("width > 200")

    # Parse precision
    precision = 0
    if pos < len(spec) and spec[pos] == ".":
        pos += 1
        if pos >= len(spec) or not spec[pos].isdigit():
            raise ValueError("precision with no digits")
        prec_start = pos
        while pos < len(spec) and spec[pos].isdigit():
            precision = precision * 10 + (ord(spec[pos]) - ord("0"))
            pos += 1
        if precision > 20:
            raise ValueError("precision > 20")

    # Parse mode
    mode = "h"
    if pos < len(spec) and spec[pos] in "hudf":
        mode = spec[pos]
        pos += 1

    # Check for unknown trailing characters
    if pos < len(spec):
        raise ValueError("unknown trailing characters")

    return fill, align, use_comma, width, precision, sign, mode


def _round_number(value, precision, mode):
    """Round number to precision decimal places."""
    if precision == 0:
        # Round to integer
        int_val = _round_to_int(value, mode)
        return (int_val, 0)

    # Multiply by 10^precision
    factor = 10 ** precision
    scaled = value * factor

    # Round to integer
    int_val = _round_to_int(scaled, mode)

    # Split into integer and fractional parts
    # For negative numbers, we need to be careful with division
    abs_int = int_val if int_val >= 0 else -int_val
    int_part = abs_int // factor
    frac_part = abs_int % factor

    # Apply sign to integer part only
    if int_val < 0:
        int_part = -int_part

    return (int_part, frac_part)


def _round_to_int(value, mode):
    """Round a value to an integer using the specified mode.

    Value can be negative. Returns the integer result (may be negative).
    """
    is_negative = value < 0
    abs_val = value if value >= 0 else -value

    if mode == "h":  # half-even
        result = _half_even_round(abs_val)
    elif mode == "u":  # half-up
        result = _half_up_round(abs_val)
    elif mode == "d":  # toward zero
        result = _truncate(abs_val)
    elif mode == "f":  # floor
        # For negative values, floor means rounding toward more negative
        # So -3.2 should become -4
        if is_negative:
            # For negative values, we need to round up in magnitude
            result = _ceil(abs_val)
        else:
            result = _floor(abs_val)
    else:
        result = _half_even_round(abs_val)

    return -result if is_negative else result


def _half_even_round(value):
    """Round to nearest integer, ties to even."""
    low = _floor(value)
    high = low + 1

    low_dist = value - low
    high_dist = high - value

    if high_dist < low_dist:
        return high
    elif low_dist < high_dist:
        return low
    else:  # Tie: round to even
        return low if low % 2 == 0 else high


def _half_up_round(value):
    """Round to nearest integer, ties away from zero."""
    if value >= 0:
        low = _floor(value)
        high = low + 1
        low_dist = value - low
        high_dist = high - value
        if high_dist <= low_dist:
            return high
        else:
            return low
    else:
        low = _floor(value)
        high = low + 1
        low_dist = low - value
        high_dist = value - high
        if high_dist <= low_dist:
            return low
        else:
            return high


def _truncate(value):
    """Truncate toward zero."""
    return _floor(value) if value >= 0 else -_floor(-value)


def _floor(value):
    """Floor function (toward negative infinity)."""
    if isinstance(value, int):
        return value
    # For floats - use math.trunc to get integer part without calling int()
    lower = math.trunc(value)
    return lower if value >= lower else lower - 1


def _ceil(value):
    """Ceiling function (toward positive infinity)."""
    if isinstance(value, int):
        return value
    lower = _floor(value)
    return lower if value == lower else lower + 1


def _group_with_commas(num_str):
    """Add comma grouping to number string."""
    if len(num_str) <= 3:
        return num_str

    result = []
    for i, ch in enumerate(reversed(num_str)):
        if i > 0 and i % 3 == 0:
            result.append(",")
        result.append(ch)

    return "".join(reversed(result))
