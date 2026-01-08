"""Plugin discovery loader using entry points."""
from typing import Any, List


def discover_plugins(group: str = "meteor.darkflight.plugins") -> List[Any]:
    """Return list of plugin manifests discovered."""
    raise NotImplementedError()
