from reply import Reply


def handle_request(request, sessions, clock):
    session_id = request.cookies.get("session")
    session = sessions.find(session_id)
    if session is not None and session.expires_at <= clock:
        headers = {"Set-Cookie": "session=; Max-Age=0"}
        return Reply(401, headers, "unauthenticated")
    if session is None:
        return Reply(401, {}, "unauthenticated")
    return Reply(200, {}, "welcome " + session.user)
