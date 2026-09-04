"""RFC-3986-style URI reference parser, normalizer and resolver."""


class UriError(ValueError):
    """Exception for URI parsing and validation errors."""
    def __init__(self, message, kind):
        super().__init__(message)
        self.kind = kind


# Character set definitions
def _is_alpha(c):
    return ('A' <= c <= 'Z') or ('a' <= c <= 'z')


def _is_digit(c):
    return '0' <= c <= '9'


def _is_hexdig(c):
    return _is_digit(c) or ('A' <= c <= 'F') or ('a' <= c <= 'f')


def _is_unreserved(c):
    return _is_alpha(c) or _is_digit(c) or c in '-._~'


def _is_sub_delim(c):
    return c in "!$&'()*+,;="


def _is_host_char(c):
    return _is_unreserved(c) or _is_sub_delim(c) or c == '%'


def _is_userinfo_char(c):
    return _is_host_char(c) or c == ':'


def _is_path_char(c):
    return _is_userinfo_char(c) or c in '@/'


def _is_query_fragment_char(c):
    return _is_path_char(c) or c == '?'


def _is_port_char(c):
    return _is_digit(c)


def _lowercase_ascii(s):
    """Lowercase ASCII A-Z only."""
    result = []
    for c in s:
        if 'A' <= c <= 'Z':
            result.append(chr(ord(c) + 32))
        else:
            result.append(c)
    return ''.join(result)


def _uppercase_hex(c):
    """Uppercase a single hex digit."""
    if '0' <= c <= '9' or 'A' <= c <= 'F':
        return c
    elif 'a' <= c <= 'f':
        return chr(ord(c) - 32)
    else:
        return c


def _hex_to_int(hex_str):
    """Convert two hex characters to integer."""
    val = 0
    for c in hex_str:
        val = val * 16
        if '0' <= c <= '9':
            val += ord(c) - ord('0')
        elif 'A' <= c <= 'F':
            val += ord(c) - ord('A') + 10
        elif 'a' <= c <= 'f':
            val += ord(c) - ord('a') + 10
    return val


def parse(s):
    """Parse a URI reference into components."""
    if not isinstance(s, str):
        raise UriError("Input must be a string", "type")

    original_s = s
    fragment = None
    query = None
    scheme = None

    # Step 2: Extract fragment
    if '#' in s:
        idx = s.index('#')
        fragment = s[idx + 1:]
        s = s[:idx]

    # Step 3: Extract query
    if '?' in s:
        idx = s.index('?')
        query = s[idx + 1:]
        s = s[:idx]

    # Step 4: Extract scheme
    colon_idx = s.find(':')
    slash_idx = s.find('/')

    if colon_idx != -1 and (slash_idx == -1 or colon_idx < slash_idx):
        scheme_part = s[:colon_idx]
        # Validate scheme format: ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
        if not _is_alpha(scheme_part[0]):
            raise UriError("Scheme must start with a letter", "scheme")
        for c in scheme_part[1:]:
            if not (_is_alpha(c) or _is_digit(c) or c in '+--.'):
                raise UriError("Invalid character in scheme", "scheme")
        scheme = scheme_part
        s = s[colon_idx + 1:]

    # Step 5: Extract authority and path
    authority = None
    path = ""

    if s.startswith('//'):
        slash_after_auth = s.find('/', 2)
        if slash_after_auth != -1:
            authority = s[2:slash_after_auth]
            path = s[slash_after_auth:]
        else:
            authority = s[2:]
            path = ""
    else:
        path = s

    # Step 6: Split authority into userinfo, host, port
    userinfo = None
    host = None
    port = None

    if authority is not None:
        at_idx = authority.rfind('@')
        if at_idx != -1:
            userinfo = authority[:at_idx]
            host_port = authority[at_idx + 1:]
        else:
            host_port = authority

        colon_idx = host_port.rfind(':')
        if colon_idx != -1:
            host = host_port[:colon_idx]
            port = host_port[colon_idx + 1:]
        else:
            host = host_port

    # Validation in exact order
    # type check already done

    # scheme validation
    if scheme is not None:
        if not _is_alpha(scheme[0]):
            raise UriError("Scheme must start with a letter", "scheme")
        for c in scheme[1:]:
            if not (_is_alpha(c) or _is_digit(c) or c in '+--.'):
                raise UriError("Invalid character in scheme", "scheme")

    # port validation
    if port is not None:
        for c in port:
            if not _is_port_char(c):
                raise UriError("Port contains non-digit character", "port")

    # host validation
    if host is not None:
        for c in host:
            if not _is_host_char(c):
                raise UriError("Host contains invalid character", "host")

    # userinfo validation
    if userinfo is not None:
        for c in userinfo:
            if not _is_userinfo_char(c):
                raise UriError("Userinfo contains invalid character", "userinfo")

    # path, query, fragment validation for invalid characters
    for c in path:
        if not _is_path_char(c):
            raise UriError("Path contains invalid character", "char")

    if query is not None:
        for c in query:
            if not _is_query_fragment_char(c):
                raise UriError("Query contains invalid character", "char")

    if fragment is not None:
        for c in fragment:
            if not _is_query_fragment_char(c):
                raise UriError("Fragment contains invalid character", "char")

    # escape validation: scan for %XY pattern
    # Scan through original string for % not followed by two HEXDIG
    i = 0
    while i < len(original_s):
        if original_s[i] == '%':
            if i + 2 >= len(original_s):
                raise UriError("Percent escape incomplete", "escape")
            if not (_is_hexdig(original_s[i + 1]) and _is_hexdig(original_s[i + 2])):
                raise UriError("Percent escape invalid", "escape")
            i += 3
        else:
            i += 1

    return {
        "scheme": scheme,
        "userinfo": userinfo,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "fragment": fragment
    }


def unparse(d):
    """Rebuild a URI from component dict."""
    if not isinstance(d, dict):
        raise UriError("Input must be a dict", "type")

    required_keys = {"scheme", "userinfo", "host", "port", "path", "query", "fragment"}
    if set(d.keys()) != required_keys:
        raise UriError("Dict must have exactly the required keys", "form")

    # Check all values are str or None
    for key, val in d.items():
        if not (isinstance(val, str) or val is None):
            raise UriError("All values must be str or None", "type")

    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]

    # Structural validation
    if path is None:
        raise UriError("Path must not be None", "form")

    if host is None:
        if userinfo is not None or port is not None:
            raise UriError("Userinfo or port without host", "form")
        if path.startswith('//'):
            raise UriError("Path starts with // without host", "form")
    else:
        # host is not None
        if path != "" and not path.startswith('/'):
            raise UriError("Path must start with / when host is present", "form")

    if scheme is None and host is None:
        if ':' in path:
            first_segment = path.split('/')[0]
            if ':' in first_segment:
                raise UriError("First segment contains : without scheme", "form")

    # Rebuild string
    result = ""

    if scheme is not None:
        result += scheme + ":"

    if host is not None:
        result += "//"
        if userinfo is not None:
            result += userinfo + "@"
        result += host
        if port is not None:
            result += ":" + port

    result += path

    if query is not None:
        result += "?" + query

    if fragment is not None:
        result += "#" + fragment

    return result


def remove_dot_segments(path):
    """Remove . and .. segments from path."""
    in_str = path
    out = ""

    while in_str:
        # A
        if in_str.startswith('../'):
            in_str = in_str[3:]
        elif in_str.startswith('./'):
            in_str = in_str[2:]
        # B
        elif in_str.startswith('/./'):
            in_str = '/' + in_str[3:]
        elif in_str == '/.':
            in_str = '/'
        # C
        elif in_str.startswith('/../'):
            in_str = '/' + in_str[4:]
            # Remove last segment from out
            if '/' in out:
                out = out[:out.rfind('/')]
            else:
                out = ""
        elif in_str == '/..':
            in_str = '/'
            # Remove last segment from out
            if '/' in out:
                out = out[:out.rfind('/')]
            else:
                out = ""
        # D
        elif in_str == '.' or in_str == '..':
            in_str = ""
        # E
        else:
            # Move first segment to out
            if in_str.startswith('/'):
                next_slash = in_str.find('/', 1)
                if next_slash != -1:
                    out += in_str[:next_slash]
                    in_str = in_str[next_slash:]
                else:
                    out += in_str
                    in_str = ""
            else:
                next_slash = in_str.find('/')
                if next_slash != -1:
                    out += in_str[:next_slash]
                    in_str = in_str[next_slash:]
                else:
                    out += in_str
                    in_str = ""

    return out


def _canonicalize_escapes(s):
    """Canonicalize percent-escapes: uppercase and decode unreserved."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '%' and i + 2 < len(s):
            hex_pair = s[i + 1:i + 3]
            # Uppercase hex digits
            hex_pair_upper = _uppercase_hex(hex_pair[0]) + _uppercase_hex(hex_pair[1])
            char_code = _hex_to_int(hex_pair_upper)
            char = chr(char_code)
            # If unreserved, decode it
            if _is_unreserved(char):
                result.append(char)
            else:
                result.append('%' + hex_pair_upper)
            i += 3
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def normalize(s):
    """Normalize a URI reference."""
    # Parse (errors propagate)
    d = parse(s)

    # Step 1: Lowercase scheme
    if d["scheme"] is not None:
        d["scheme"] = _lowercase_ascii(d["scheme"])

    # Step 2: Canonicalize percent-escapes in userinfo, host, path, query, fragment
    if d["userinfo"] is not None:
        d["userinfo"] = _canonicalize_escapes(d["userinfo"])
    if d["host"] is not None:
        d["host"] = _canonicalize_escapes(d["host"])
    d["path"] = _canonicalize_escapes(d["path"])
    if d["query"] is not None:
        d["query"] = _canonicalize_escapes(d["query"])
    if d["fragment"] is not None:
        d["fragment"] = _canonicalize_escapes(d["fragment"])

    # Step 3: Lowercase host letters (not in escapes)
    if d["host"] is not None:
        host_result = []
        i = 0
        while i < len(d["host"]):
            if d["host"][i] == '%' and i + 2 < len(d["host"]):
                host_result.append(d["host"][i:i + 3])
                i += 3
            elif 'A' <= d["host"][i] <= 'Z':
                host_result.append(chr(ord(d["host"][i]) + 32))
                i += 1
            else:
                host_result.append(d["host"][i])
                i += 1
        d["host"] = ''.join(host_result)

    # Step 4: Port handling
    if d["port"] is not None:
        if d["port"] == "":
            d["port"] = None
        else:
            # Remove leading zeros
            port_int = int(d["port"])
            port_str = str(port_int)
            # Check for default port
            scheme = d["scheme"]
            if (scheme in ('http', 'ws') and port_int == 80) or \
               (scheme in ('https', 'wss') and port_int == 443):
                d["port"] = None
            else:
                d["port"] = port_str

    # Step 5: Remove dot segments
    if d["host"] is not None or d["path"].startswith('/'):
        d["path"] = remove_dot_segments(d["path"])

    # Step 6: Recomposition guard
    if d["host"] is None and d["path"].startswith('//'):
        d["path"] = '/.' + d["path"]

    return unparse(d)


def resolve(base, ref):
    """Resolve a reference URI against a base URI."""
    if not isinstance(base, str):
        raise UriError("Base must be a string", "type")
    if not isinstance(ref, str):
        raise UriError("Ref must be a string", "type")

    # Parse base and check for scheme
    B = parse(base)
    if B["scheme"] is None:
        raise UriError("Base URI must have a scheme", "base")

    # Parse ref
    R = parse(ref)

    # Compute target components
    if R["scheme"] is not None:
        # R has scheme
        T_scheme = R["scheme"]
        T_userinfo = R["userinfo"]
        T_host = R["host"]
        T_port = R["port"]
        T_path = remove_dot_segments(R["path"])
        T_query = R["query"]
    elif R["host"] is not None:
        # R has host but no scheme
        T_scheme = B["scheme"]
        T_userinfo = R["userinfo"]
        T_host = R["host"]
        T_port = R["port"]
        T_path = remove_dot_segments(R["path"])
        T_query = R["query"]
    else:
        # R has neither scheme nor host
        T_scheme = B["scheme"]
        T_userinfo = B["userinfo"]
        T_host = B["host"]
        T_port = B["port"]

        if R["path"] == "":
            T_path = B["path"]
            if R["query"] is not None:
                T_query = R["query"]
            else:
                T_query = B["query"]
        else:
            T_query = R["query"]
            if R["path"].startswith('/'):
                T_path = remove_dot_segments(R["path"])
            else:
                # Merge paths
                if B["host"] is not None and B["path"] == "":
                    merged = "/" + R["path"]
                else:
                    if '/' in B["path"]:
                        merged = B["path"][:B["path"].rfind('/') + 1] + R["path"]
                    else:
                        merged = R["path"]
                T_path = remove_dot_segments(merged)

    T_fragment = R["fragment"]

    # Create target dict
    T = {
        "scheme": T_scheme,
        "userinfo": T_userinfo,
        "host": T_host,
        "port": T_port,
        "path": T_path,
        "query": T_query,
        "fragment": T_fragment
    }

    # Normalize and return
    result = unparse(T)
    return normalize(result)
