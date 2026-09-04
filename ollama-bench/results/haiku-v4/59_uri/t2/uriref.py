"""RFC-3986 URI reference parser, normalizer, and resolver."""

# Character set definitions
ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
DIGIT = '0123456789'
HEXDIG = '0123456789ABCDEFabcdef'
UNRESERVED = ALPHA + DIGIT + '-._~'
SUB_DELIMS = "!$&'()*+,;="
HOST_CHARS = UNRESERVED + SUB_DELIMS + '%'
USERINFO_CHARS = HOST_CHARS + ':'
PATH_CHARS = USERINFO_CHARS + '@/'
QUERY_FRAG_CHARS = PATH_CHARS + '?'
PORT_CHARS = DIGIT


class UriError(ValueError):
    """Exception raised for URI parsing/validation errors."""
    def __init__(self, message, kind):
        super().__init__(message)
        self.kind = kind


def parse(s):
    """Parse a URI string into its components.

    Returns a dict with keys: scheme, userinfo, host, port, path, query, fragment.
    Each value is either a str or None.
    """
    # Validation 1: type
    if not isinstance(s, str):
        raise UriError("Not a string", "type")

    original = s

    # Step 2: Extract fragment
    if '#' in s:
        s, fragment = s.split('#', 1)
    else:
        fragment = None

    # Step 3: Extract query
    if '?' in s:
        s, query = s.split('?', 1)
    else:
        query = None

    # Step 4: Extract scheme
    colon_idx = s.find(':')
    slash_idx = s.find('/')

    scheme = None
    if colon_idx >= 0 and (slash_idx < 0 or colon_idx < slash_idx):
        scheme = s[:colon_idx]
        s = s[colon_idx + 1:]

    # Validation 2: scheme format
    if scheme is not None:
        if not scheme or scheme[0] not in ALPHA:
            raise UriError("Invalid scheme", "scheme")
        for ch in scheme[1:]:
            if ch not in ALPHA + DIGIT + '+-.' :
                raise UriError("Invalid scheme", "scheme")

    # Step 5: Extract authority and path
    userinfo = None
    host = None
    port = None

    if s.startswith('//'):
        s = s[2:]
        # Find the authority part (up to next / or end)
        slash_idx = s.find('/')
        if slash_idx >= 0:
            authority = s[:slash_idx]
            path = s[slash_idx:]
        else:
            authority = s
            path = ""

        # Step 6: Split authority
        # Find last @
        at_idx = authority.rfind('@')
        if at_idx >= 0:
            userinfo = authority[:at_idx]
            host_port = authority[at_idx + 1:]
        else:
            host_port = authority

        # Find last : in host_port
        colon_idx = host_port.rfind(':')
        if colon_idx >= 0:
            host = host_port[:colon_idx]
            port = host_port[colon_idx + 1:]
        else:
            host = host_port
    else:
        path = s

    # Validation 3: port
    if port is not None:
        for ch in port:
            if ch not in PORT_CHARS:
                raise UriError("Invalid character in port", "port")

    # Validation 4: host
    if host is not None:
        for ch in host:
            if ch not in HOST_CHARS:
                raise UriError("Invalid character in host", "host")

    # Validation 5: userinfo
    if userinfo is not None:
        for ch in userinfo:
            if ch not in USERINFO_CHARS:
                raise UriError("Invalid character in userinfo", "userinfo")

    # Validation 6: char in path, query, fragment (in that order)
    for ch in path:
        if ch not in PATH_CHARS:
            raise UriError("Invalid character in path", "char")

    if query is not None:
        for ch in query:
            if ch not in QUERY_FRAG_CHARS:
                raise UriError("Invalid character in query", "char")

    if fragment is not None:
        for ch in fragment:
            if ch not in QUERY_FRAG_CHARS:
                raise UriError("Invalid character in fragment", "char")

    # Validation 7: escape sequences in original string
    i = 0
    while i < len(original):
        if original[i] == '%':
            if i + 2 >= len(original):
                raise UriError("Invalid escape sequence", "escape")
            h1, h2 = original[i + 1], original[i + 2]
            if h1 not in HEXDIG or h2 not in HEXDIG:
                raise UriError("Invalid escape sequence", "escape")
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
    """Rebuild a URI string from a component dict."""
    # Validation 1: type
    if not isinstance(d, dict):
        raise UriError("Not a dict", "type")

    # Validation 2: form - exact keys
    expected_keys = {"scheme", "userinfo", "host", "port", "path", "query", "fragment"}
    if set(d.keys()) != expected_keys:
        raise UriError("Invalid keys", "form")

    # Validation 3: type of values
    for key, value in d.items():
        if value is not None and not isinstance(value, str):
            raise UriError(f"Invalid value type for {key}", "type")

    # Validation 4: structural problems
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]

    # path cannot be None
    if path is None:
        raise UriError("path cannot be None", "form")

    # host is None while userinfo or port is not None
    if host is None and (userinfo is not None or port is not None):
        raise UriError("host is None but userinfo or port is not", "form")

    # host is not None while path is neither "" nor starting with /
    if host is not None and path != "" and not path.startswith('/'):
        raise UriError("host is not None but path does not start with /", "form")

    # host is None while path starts with //
    if host is None and path.startswith('//'):
        raise UriError("host is None but path starts with //", "form")

    # scheme and host are both None while first segment of path contains :
    if scheme is None and host is None:
        # First segment is text before first / or whole path if no /
        first_segment = path.split('/', 1)[0]
        if ':' in first_segment:
            raise UriError("First segment of path contains : when scheme and host are None", "form")

    # Build the URI
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


def _canonicalize_escapes(s):
    """Canonicalize percent-escapes in a string."""
    result = ""
    i = 0
    while i < len(s):
        if s[i] == '%' and i + 2 < len(s):
            h1, h2 = s[i + 1], s[i + 2]
            if h1 in HEXDIG and h2 in HEXDIG:
                # Uppercase hex digits
                h1_upper = h1.upper()
                h2_upper = h2.upper()
                # Get character
                ch_code = int(h1_upper + h2_upper, 16)
                ch = chr(ch_code)
                # Check if unreserved - if so, decode it
                if ch in UNRESERVED:
                    result += ch
                else:
                    result += "%" + h1_upper + h2_upper
                i += 3
            else:
                result += s[i]
                i += 1
        else:
            result += s[i]
            i += 1
    return result


def _lowercase_host(s):
    """Lowercase all ASCII letters in a host name, preserving percent-escapes."""
    result = ""
    i = 0
    while i < len(s):
        if s[i] == '%' and i + 2 < len(s):
            # This is part of a percent-escape, keep it as is
            result += s[i:i + 3]
            i += 3
        elif s[i] in ALPHA:
            result += s[i].lower()
            i += 1
        else:
            result += s[i]
            i += 1
    return result


def _remove_dot_segments(path):
    """Remove dot segments from a path per RFC 3986."""
    input_buffer = path
    output = ""

    while input_buffer:
        # A
        if input_buffer.startswith('../'):
            input_buffer = input_buffer[3:]
        elif input_buffer.startswith('./'):
            input_buffer = input_buffer[2:]
        # B
        elif input_buffer.startswith('/./'):
            input_buffer = '/' + input_buffer[3:]
        elif input_buffer == '/.':
            input_buffer = '/'
        # C
        elif input_buffer.startswith('/../'):
            input_buffer = '/' + input_buffer[4:]
            # Remove last segment of output
            if '/' in output:
                output = output[:output.rfind('/')]
            else:
                output = ""
        elif input_buffer == '/..':
            input_buffer = '/'
            # Remove last segment of output
            if '/' in output:
                output = output[:output.rfind('/')]
            else:
                output = ""
        # D
        elif input_buffer in ('.', '..'):
            input_buffer = ""
        # E
        else:
            # Move first segment to output
            if input_buffer.startswith('/'):
                seg_end = input_buffer.find('/', 1)
                if seg_end == -1:
                    seg_end = len(input_buffer)
            else:
                seg_end = input_buffer.find('/')
                if seg_end == -1:
                    seg_end = len(input_buffer)

            output += input_buffer[:seg_end]
            input_buffer = input_buffer[seg_end:]

    return output


def normalize(s):
    """Normalize a URI string."""
    # Parse
    d = parse(s)

    # 1. Lowercase scheme
    if d["scheme"] is not None:
        d["scheme"] = d["scheme"].lower()

    # 2. Canonicalize percent-escapes
    for key in ["userinfo", "host", "path", "query", "fragment"]:
        if d[key] is not None:
            d[key] = _canonicalize_escapes(d[key])

    # 3. Lowercase host
    if d["host"] is not None:
        d["host"] = _lowercase_host(d["host"])

    # 4. Normalize port
    if d["port"] is not None:
        if d["port"] == "":
            d["port"] = None
        else:
            port_val = int(d["port"])
            d["port"] = str(port_val)

            # Remove default ports
            scheme = d["scheme"]
            if (scheme == "http" or scheme == "ws") and port_val == 80:
                d["port"] = None
            elif (scheme == "https" or scheme == "wss") and port_val == 443:
                d["port"] = None

    # 5. Apply remove_dot_segments to path
    if d["host"] is not None or d["path"].startswith('/'):
        d["path"] = _remove_dot_segments(d["path"])

    # 6. Recomposition guard
    if d["host"] is None and d["path"].startswith('//'):
        d["path"] = "/." + d["path"]

    return unparse(d)


def _merge(b, r):
    """Merge a relative reference path with a base path."""
    if b["host"] is not None and b["path"] == "":
        return "/" + r["path"]
    else:
        # B's path up to and including its last /
        if '/' in b["path"]:
            return b["path"][:b["path"].rfind('/') + 1] + r["path"]
        else:
            return r["path"]


def resolve(base, ref):
    """Resolve a relative reference URI against a base URI."""
    # Type check
    if not isinstance(base, str):
        raise UriError("base is not a string", "type")
    if not isinstance(ref, str):
        raise UriError("ref is not a string", "type")

    # Parse base
    b = parse(base)

    # Check base has scheme
    if b["scheme"] is None:
        raise UriError("base has no scheme", "base")

    # Parse ref
    r = parse(ref)

    # Compute target components T
    t = {
        "scheme": None,
        "userinfo": None,
        "host": None,
        "port": None,
        "path": None,
        "query": None,
        "fragment": None
    }

    if r["scheme"] is not None:
        # R has scheme
        t["scheme"] = r["scheme"]
        t["userinfo"] = r["userinfo"]
        t["host"] = r["host"]
        t["port"] = r["port"]
        t["path"] = _remove_dot_segments(r["path"])
        t["query"] = r["query"]
    elif r["host"] is not None:
        # R has host but no scheme
        t["scheme"] = b["scheme"]
        t["userinfo"] = r["userinfo"]
        t["host"] = r["host"]
        t["port"] = r["port"]
        t["path"] = _remove_dot_segments(r["path"])
        t["query"] = r["query"]
    else:
        # R has no scheme and no host
        t["scheme"] = b["scheme"]
        t["userinfo"] = b["userinfo"]
        t["host"] = b["host"]
        t["port"] = b["port"]

        if r["path"] == "":
            # R has empty path
            t["path"] = b["path"]
            if r["query"] is not None:
                t["query"] = r["query"]
            else:
                t["query"] = b["query"]
        else:
            # R has non-empty path
            t["query"] = r["query"]
            if r["path"].startswith('/'):
                t["path"] = _remove_dot_segments(r["path"])
            else:
                t["path"] = _remove_dot_segments(_merge(b, r))

    t["fragment"] = r["fragment"]

    # Normalize T (apply normalization steps 1-6)

    # 1. Lowercase scheme
    if t["scheme"] is not None:
        t["scheme"] = t["scheme"].lower()

    # 2. Canonicalize percent-escapes
    for key in ["userinfo", "host", "path", "query", "fragment"]:
        if t[key] is not None:
            t[key] = _canonicalize_escapes(t[key])

    # 3. Lowercase host
    if t["host"] is not None:
        t["host"] = _lowercase_host(t["host"])

    # 4. Normalize port
    if t["port"] is not None:
        if t["port"] == "":
            t["port"] = None
        else:
            port_val = int(t["port"])
            t["port"] = str(port_val)

            # Remove default ports
            scheme = t["scheme"]
            if (scheme == "http" or scheme == "ws") and port_val == 80:
                t["port"] = None
            elif (scheme == "https" or scheme == "wss") and port_val == 443:
                t["port"] = None

    # 5. Apply remove_dot_segments to path
    if t["host"] is not None or t["path"].startswith('/'):
        t["path"] = _remove_dot_segments(t["path"])

    # 6. Recomposition guard
    if t["host"] is None and t["path"].startswith('//'):
        t["path"] = "/." + t["path"]

    return unparse(t)
