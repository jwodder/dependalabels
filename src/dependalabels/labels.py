# All colors must be lowercase six-hex strings without leading '#'.
from __future__ import annotations
from dataclasses import dataclass
import random

# These are the "default colors" listed when creating a label via GitHub's web
# UI as of 2023-09-24:
COLORS = [
    "0052cc",
    "006b75",
    "0e8a16",
    "1d76db",
    "5319e7",
    "b60205",
    "bfd4f2",
    "bfdadc",
    "c2e0c6",
    "c5def5",
    "d4c5f9",
    "d93f0b",
    "e99695",
    "f9d0c4",
    "fbca04",
    "fef2c0",
]


@dataclass
class LabelDetails:
    color: str
    description: str | None
    predefined: bool = False

    @classmethod
    def random(cls) -> LabelDetails:
        return cls(color=random.choice(COLORS), description=None)


PREDEFINED = {
    "dependencies": LabelDetails(
        color="8732bc",
        description="Update one or more dependencies' versions",
        predefined=True,
    ),
    "d:cargo": LabelDetails(
        color="dea584",
        description="Update a Cargo (Rust) dependency",
        predefined=True,
    ),
    "d:github-actions": LabelDetails(
        color="74fa75",
        description="Update a GitHub Actions action dependency",
        predefined=True,
    ),
    "d:python": LabelDetails(
        color="3572a5",
        description="Update a Python dependency",
        predefined=True,
    ),
}
