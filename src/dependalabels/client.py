from __future__ import annotations
from collections.abc import Iterator
from dataclasses import InitVar, dataclass, field
import logging
from typing import Any
from ghrepo import GHRepo
import requests
from .labels import LabelDetails

log = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"


@dataclass
class Client:
    repo: GHRepo
    token: InitVar[str]
    session: requests.Session = field(init=False)

    def __post_init__(self, token: str) -> None:
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"bearer {token}"

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.session.close()

    def paginate(self, url: str) -> Iterator:
        while True:
            r = self.session.get(url)
            r.raise_for_status()
            yield from r.json()
            url2 = r.links.get("next", {}).get("url")
            if url2 is None:
                return
            url = url2

    def get_label_maker(self) -> LabelMaker:
        log.info("Fetching current labels for %s ...", self.repo)
        labels: dict[str, LabelDetails] = {}
        for lbl in self.paginate(
            f"{GITHUB_API_URL}/repos/{self.repo.owner}/{self.repo.name}/labels"
        ):
            labels[lbl["name"]] = LabelDetails(
                color=lbl["color"], description=lbl["description"]
            )
        return LabelMaker(client=self, labels=labels)


@dataclass
class LabelMaker:
    client: Client
    labels: dict[str, LabelDetails]

    @property
    def label_url(self) -> str:
        return (
            f"{GITHUB_API_URL}/repos/{self.client.repo.owner}"
            f"/{self.client.repo.name}/labels"
        )

    def ensure_label(
        self, name: str, details: LabelDetails, force: bool = False
    ) -> None:
        payload: dict[str, str | None] = {}
        try:
            extant = self.labels[name]
        except KeyError:
            log.info("Creating %r label", name)
            payload = {
                "name": name,
                "color": details.color,
                "description": details.description,
            }
            r = self.client.session.post(self.label_url, json=payload)
            r.raise_for_status()
            data = r.json()
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
                log.info("Updating %s for %r label", ", ".join(payload.keys()), name)
                self.client.session.patch(
                    f"{self.label_url}/{name}", json=payload
                ).raise_for_status()
            else:
                log.info("%r label already exists; not modifying", name)
