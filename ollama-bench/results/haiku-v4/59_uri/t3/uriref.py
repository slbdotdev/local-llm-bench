class UriError(ValueError):
    """Exception for URI parsing and validation errors."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(f"URI error: {kind}")


# Character set definitions
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
DIGIT = "0123456789"
HEXDIG = "0123456789ABCDEFabcdef"
UNRESERVED = set(ALPHA + DIGIT + "-._~")
SUB_DELIMS = set("!$&'()*+,;=")

HOST_CHARS = UNRESERVED | SUB_DELIMS | {"%"}
USERINFO_CHARS = HOST_CHARS | {":"}
PATH_CHARS = USERINFO_CHARS | {"@", "/"}
QUERY_CHARS = PATH_CHARS | {"?"}
FRAGMENT_CHARS = QUERY_CHARS


def parse(s):
    """Parse a URI reference string into components."""
    # Validation step 1: type check
    if not isinstance(s, str):
        raise UriError("type")

    # Split fragment (step 2)
    fragment_idx = s.find("#")
    if fragment_idx != -1:
        fragment = s[fragment_idx + 1:]
        s_no_frag = s[:fragment_idx]
    else:
        fragment = None
        s_no_frag = s

    # Split query (step 3)
    query_idx = s_no_frag.find("?")
    if query_idx != -1:
        query = s_no_frag[query_idx + 1:]
        s_no_query = s_no_frag[:query_idx]
    else:
        query = None
        s_no_query = s_no_frag

    # Extract scheme (step 4)
    colon_idx = s_no_query.find(":")
    slash_idx = s_no_query.find("/")

    if colon_idx != -1 and (slash_idx == -1 or colon_idx < slash_idx):
        scheme = s_no_query[:colon_idx]
        s_after_scheme = s_no_query[colon_idx + 1:]

        # Validate scheme format (must match ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ))
        if not scheme or scheme[0] not in ALPHA:
            raise UriError("scheme")
        for c in scheme[1:]:
            if c not in ALPHA + DIGIT + "+-." :
                raise UriError("scheme")
    else:
        scheme = None
        s_after_scheme = s_no_query

    # Extract authority and path (step 5)
    if s_after_scheme.startswith("//"):
        s_after_slashes = s_after_scheme[2:]
        slash_in_auth = s_after_slashes.find("/")
        if slash_in_auth != -1:
            authority = s_after_slashes[:slash_in_auth]
            path = s_after_slashes[slash_in_auth:]
        else:
            authority = s_after_slashes
            path = ""

        # Split authority (step 6)
        at_idx = authority.rfind("@")
        if at_idx != -1:
            userinfo = authority[:at_idx]
            host_port = authority[at_idx + 1:]
        else:
            userinfo = None
            host_port = authority

        colon_hp = host_port.rfind(":")
        if colon_hp != -1:
            host = host_port[:colon_hp]
            port = host_port[colon_hp + 1:]
        else:
            host = host_port
            port = None
    else:
        userinfo = None
        host = None
        port = None
        path = s_after_scheme

    # Validation in order
    # Step 1: type - already checked above

    # Step 2: scheme - already validated above

    # Step 3: port - must contain only DIGIT
    if port is not None:
        for c in port:
            if c not in DIGIT:
                raise UriError("port")

    # Step 4: host - must contain only host chars
    if host is not None:
        for c in host:
            if c not in HOST_CHARS:
                raise UriError("host")

    # Step 5: userinfo - must contain only userinfo chars
    if userinfo is not None:
        for c in userinfo:
            if c not in USERINFO_CHARS:
                raise UriError("userinfo")

    # Step 6: char - path, query, fragment must contain valid chars
    for c in path:
        if c not in PATH_CHARS:
            raise UriError("char")

    if query is not None:
        for c in query:
            if c not in QUERY_CHARS:
                raise UriError("char")

    if fragment is not None:
        for c in fragment:
            if c not in FRAGMENT_CHARS:
                raise UriError("char")

    # Step 7: escape - all % must be followed by two HEXDIG
    idx = 0
    while idx < len(s):
        if s[idx] == "%":
            if idx + 2 >= len(s):
                raise UriError("escape")
            if s[idx + 1] not in HEXDIG or s[idx + 2] not in HEXDIG:
                raise UriError("escape")
            idx += 3
        else:
            idx += 1

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
    """Rebuild a URI string from components."""
    # Check 1: d must be a dict
    if not isinstance(d, dict):
        raise UriError("type")

    # Check 2: must have exactly the 7 keys
    expected_keys = {"scheme", "userinfo", "host", "port", "path", "query", "fragment"}
    if set(d.keys()) != expected_keys:
        raise UriError("form")

    # Check 3: all values must be str or None
    for v in d.values():
        if v is not None and not isinstance(v, str):
            raise UriError("type")

    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]

    # Check 4: structural problems
    if path is None:
        raise UriError("form")

    if host is None:
        if userinfo is not None or port is not None:
            raise UriError("form")
    else:
        if path and not path.startswith("/"):
            raise UriError("form")

    if host is None and path.startswith("//"):
        raise UriError("form")

    if scheme is None and host is None:
        # Check if first segment contains ':'
        slash_pos = path.find("/")
        if slash_pos == -1:
            first_segment = path
        else:
            first_segment = path[:slash_pos]
        if ":" in first_segment:
            raise UriError("form")

    # Build the result
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
    """Remove dot segments from a path."""
    input_buf = path
    output = ""

    while input_buf:
        # Rule A: remove ../  or ./
        if input_buf.startswith("../"):
            input_buf = input_buf[3:]
        elif input_buf.startswith("./"):
            input_buf = input_buf[2:]
        # Rule B: replace /./ with / or /. becomes /
        elif input_buf.startswith("/./"):
            input_buf = "/" + input_buf[3:]
        elif input_buf == "/.":
            input_buf = "/"
        # Rule C: replace /../ with / and remove last segment of output
        elif input_buf.startswith("/../"):
            input_buf = "/" + input_buf[4:]
            # Remove last segment from output
            last_slash = output.rfind("/")
            if last_slash != -1:
                output = output[:last_slash]
            else:
                output = ""
        elif input_buf == "/..":
            input_buf = "/"
            # Remove last segment from output
            last_slash = output.rfind("/")
            if last_slash != -1:
                output = output[:last_slash]
            else:
                output = ""
        # Rule D: remove . or ..
        elif input_buf in (".", ".."):
            input_buf = ""
        # Rule E: move first segment to output
        else:
            if input_buf.startswith("/"):
                seg_end = input_buf.find("/", 1)
                if seg_end == -1:
                    segment = input_buf
                    input_buf = ""
                else:
                    segment = input_buf[:seg_end]
                    input_buf = input_buf[seg_end:]
            else:
                seg_end = input_buf.find("/")
                if seg_end == -1:
                    segment = input_buf
                    input_buf = ""
                else:
                    segment = input_buf[:seg_end]
                    input_buf = input_buf[seg_end:]
            output += segment

    return output


def normalize(s):
    """Normalize a URI reference."""
    # Parse (errors propagate)
    parsed = parse(s)

    scheme = parsed["scheme"]
    userinfo = parsed["userinfo"]
    host = parsed["host"]
    port = parsed["port"]
    path = parsed["path"]
    query = parsed["query"]
    fragment = parsed["fragment"]

    # Step 1: lowercase scheme
    if scheme is not None:
        scheme = scheme.lower()

    # Step 2: canonicalize percent-escapes
    def canonicalize_escapes(s):
        if s is None:
            return None
        result = ""
        i = 0
        while i < len(s):
            if s[i] == "%":
                hex_chars = s[i+1:i+3].upper()
                result += "%"
                result += hex_chars
                hex_val = int(hex_chars, 16)
                # Check if it's an unreserved character
                char = chr(hex_val)
                if char in UNRESERVED:
                    result = result[:-3]  # Remove the %XX
                    result += char
                i += 3
            else:
                result += s[i]
                i += 1
        return result

    userinfo = canonicalize_escapes(userinfo)
    host = canonicalize_escapes(host) if host is not None else None
    path = canonicalize_escapes(path)
    query = canonicalize_escapes(query)
    fragment = canonicalize_escapes(fragment)

    # Step 3: lowercase host (not in escapes)
    if host is not None:
        result = ""
        i = 0
        while i < len(host):
            if host[i] == "%":
                result += host[i:i+3]
                i += 3
            else:
                c = host[i]
                if c in ALPHA:
                    result += c.lower()
                else:
                    result += c
                i += 1
        host = result

    # Step 4: normalize port
    if port is not None:
        if port == "":
            port = None
        else:
            # Rewrite as decimal without leading zeros
            port_num = int(port)
            port = str(port_num)

            # Remove if default for scheme
            if scheme in ("http", "ws") and port_num == 80:
                port = None
            elif scheme in ("https", "wss") and port_num == 443:
                port = None

    # Step 5: remove dot segments from path
    if host is not None or path.startswith("/"):
        path = remove_dot_segments(path)

    # Step 6: recomposition guard
    if host is None and path.startswith("//"):
        path = "/." + path

    # Serialize
    return unparse({
        "scheme": scheme,
        "userinfo": userinfo,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "fragment": fragment
    })


def resolve(base, ref):
    """Resolve a URI reference against a base URI."""
    # Check types
    if not isinstance(base, str) or not isinstance(ref, str):
        raise UriError("type")

    # Parse base (errors propagate)
    b_parsed = parse(base)

    # Check if base has scheme
    if b_parsed["scheme"] is None:
        raise UriError("base")

    # Parse ref (errors propagate)
    r_parsed = parse(ref)

    # Compute target components
    if r_parsed["scheme"] is not None:
        # R has a scheme
        t_scheme = r_parsed["scheme"]
        t_userinfo = r_parsed["userinfo"]
        t_host = r_parsed["host"]
        t_port = r_parsed["port"]
        t_path = remove_dot_segments(r_parsed["path"])
        t_query = r_parsed["query"]
    elif r_parsed["host"] is not None:
        # R has a host
        t_scheme = b_parsed["scheme"]
        t_userinfo = r_parsed["userinfo"]
        t_host = r_parsed["host"]
        t_port = r_parsed["port"]
        t_path = remove_dot_segments(r_parsed["path"])
        t_query = r_parsed["query"]
    else:
        # R has no host
        t_scheme = b_parsed["scheme"]
        t_userinfo = b_parsed["userinfo"]
        t_host = b_parsed["host"]
        t_port = b_parsed["port"]

        if r_parsed["path"] == "":
            # R has empty path
            t_path = b_parsed["path"]
            t_query = r_parsed["query"] if r_parsed["query"] is not None else b_parsed["query"]
        else:
            t_query = r_parsed["query"]
            if r_parsed["path"].startswith("/"):
                t_path = remove_dot_segments(r_parsed["path"])
            else:
                # Merge paths
                if b_parsed["host"] is not None and b_parsed["path"] == "":
                    merged = "/" + r_parsed["path"]
                else:
                    last_slash = b_parsed["path"].rfind("/")
                    if last_slash != -1:
                        merged = b_parsed["path"][:last_slash + 1] + r_parsed["path"]
                    else:
                        merged = r_parsed["path"]
                t_path = remove_dot_segments(merged)

    t_fragment = r_parsed["fragment"]

    # Apply normalize to target
    target_dict = {
        "scheme": t_scheme,
        "userinfo": t_userinfo,
        "host": t_host,
        "port": t_port,
        "path": t_path,
        "query": t_query,
        "fragment": t_fragment
    }

    # Normalize the target
    return normalize(unparse(target_dict))
