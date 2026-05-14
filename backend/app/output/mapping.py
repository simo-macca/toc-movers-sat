"""Variable mapping serialization to JSON."""

import json


def mapping_to_json(mapping: dict[int, str]) -> str:
    """Serialize a variable ID mapping to pretty-printed JSON.

    Args:
        mapping: Dictionary mapping integer variable IDs to symbolic names.

    Returns:
        Indented, key-sorted JSON string.
    """
    return json.dumps(mapping, indent=2, sort_keys=True)
