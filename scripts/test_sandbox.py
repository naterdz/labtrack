"""Run unchanged pytest assertions where socket wakeups are restricted.

Polling bounds selector waits; this does not change application or test outcomes.
Use ordinary pytest outside the restricted environment.
"""

import selectors
import sys

import pytest

original_select = selectors.EpollSelector.select


def polling_select(self, timeout=None):
    return original_select(self, min(timeout, 0.01) if timeout is not None else 0.01)


if __name__ == "__main__":
    selectors.EpollSelector.select = polling_select
    raise SystemExit(pytest.main(sys.argv[1:] or ["-q", "backend/tests"]))
