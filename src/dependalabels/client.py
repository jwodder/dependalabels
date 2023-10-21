from __future__ import annotations
from dataclasses import InitVar, dataclass
import logging
from urllib.parse import quote
from ghrepo import GHRepo
import ghreq
from . import __url__, __version__
from .labels import LabelDetails

log = logging.getLogger(__name__)


@dataclass
class Client(ghreq.Client):
    repo: GHRepo
    token: InitVar[str]

    def __post_init__(self, token: str) -> None:
        super().__init__(
            token=token,
            user_agent=ghreq.make_user_agent("dependalabels", __version__, url=__url__),
        )

    def get_label_maker(self) -> LabelMaker:
        log.info("Fetching current labels for %s ...", self.repo)
        labels: dict[str, LabelDetails] = {}
        endpoint = self / "repos" / self.repo.owner / self.repo.name / "labels"
        for lbl in endpoint.paginate():
            labels[lbl["name"]] = LabelDetails(
                color=lbl["color"], description=lbl["description"]
            )
        return LabelMaker(endpoint=endpoint, labels=labels)


@dataclass
class LabelMaker:
    endpoint: ghreq.Endpoint
    labels: dict[str, LabelDetails]

    def ensure_label(
        self, name: str, details: LabelDetails, force: bool = False
    ) -> None:
        payload: dict[str, str | None] = {}
        try:
            extant = self.labels[name]
        except KeyError:
            if details.predefined:
                log.info(
                    "Creating label %r (color: %s, description: %r)",
                    name,
                    details.color,
                    details.description,
                )
            else:
                log.info("Creating label %r (random color: %s)", name, details.color)
            payload = {
                "name": name,
                "color": details.color,
                "description": details.description,
            }
            data = self.endpoint.post(payload)
            self.labels[name] = LabelDetails(
                color=data["color"], description=data["description"]
            )
        else:
            if force:
                if details.color != extant.color:
                    payload["color"] = details.color
                    extant.color = details.color
                if (details.description or "") != (extant.description or ""):
                    payload["description"] = details.description
                    extant.description = details.description
            if payload:
                log.info("Updating %s for label %r", ", ".join(payload.keys()), name)
                (self.endpoint / quote(name)).patch(payload)
            elif details.predefined:
                log.info("Label %r already exists; not modifying", name)
            else:
                log.info("Label %r already exists", name)
