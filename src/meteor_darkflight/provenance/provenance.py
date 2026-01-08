"""Build and serialize provenance graphs for runs."""
from typing import Any


class ProvenanceGraph:
    def __init__(self):
        """Initialize empty graph."""
        # nodes/edges store
        self.nodes = []
        self.edges = []

    def add_node(self, artifact: Any) -> None:
        """Add artifact node."""
        raise NotImplementedError()

    def add_edge(self, from_node: Any, to_node: Any) -> None:
        """Add dependency edge."""
        raise NotImplementedError()

    def serialize(self) -> Any:
        """Return serializable graph (dict)."""
        raise NotImplementedError()
