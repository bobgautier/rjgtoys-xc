"""
A basic wrapper over :mod:`json` that ensures input uses :class:`Thing`
and that output is consistent and repeatable.
"""

import io
import json

from ._thing import Thing


def json_loads(s, object_hook=None):
    """Load a string from JSON returning a :class:`Thing`."""

    return json.loads(s, object_hook=object_hook or Thing)


def json_load(stream, object_hook=None):
    """Load JSON from a stream and return a :class:`Thing`."""
    return json.load(io.TextIOWrapper(stream), object_hook=object_hook or Thing)


def json_dumps(obj):
    """Produce consistent repeatable JSON from an object."""

    return json.dumps(obj, indent=None, sort_keys=True)
