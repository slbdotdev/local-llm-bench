"""Release-control package used by the current decision review.

The package is split into adapters so a reviewer must follow the snapshot
through the same sequence as the service.
"""
PACKAGE_NAME = "release-control"
CURRENT_SCHEMA = 7
PUBLIC_ENTRYPOINT = "decision.should_grant"

