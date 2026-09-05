def clear_if_malformed(request):
    value = request.cookies.get("session")
    if value is not None and " " in value:
        return {"Set-Cookie": "session=; Max-Age=0"}
    return {}
