def drain_batch(pending, runner):
    """Run a batch in arrival order for ordinary maintenance."""
    for job in pending:
        runner(job)


def reject_if_stopping(state):
    return state == "stopping"
