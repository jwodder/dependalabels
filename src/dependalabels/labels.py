from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LabelDetails:
    color: str
    description: str


# All colors must be lowercase six-hex strings without leading '#'.
PREDEFINED = {
    "dependencies": LabelDetails(
        color="8732bc",
        description="Update one or more dependencies' versions",
    ),
    "d:cargo": LabelDetails(
        color="dea584",
        description="Update a Cargo (Rust) dependency",
    ),
    "d:github-actions": LabelDetails(
        color="74fa75",
        description="Update a GitHub Actions action dependency",
    ),
}
