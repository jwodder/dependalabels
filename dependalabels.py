from __future__ import annotations
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import subprocess
from typing import Optional
import click
from ghrepo import get_local_repo
from github import Github
from github.Repository import Repository
from pydantic import BaseModel, Field
from ruamel.yaml import YAML

log = logging.getLogger()


@dataclass
class LabelDetails:
    color: str
    description: str


LABELS = {
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


class DependabotUpdate(BaseModel):
    labels: list[str] = Field(default_factory=list)


class DependabotConfig(BaseModel):
    updates: list[DependabotUpdate]


def get_custom_labels(dirpath: Optional[Path]) -> set[str]:
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=dirpath,
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    toplevel = Path(r.stdout.strip())
    with (toplevel / ".github" / "dependabot.yml").open() as fp:
        cfg = DependabotConfig.model_validate(YAML(typ="safe").load(fp))
    return {lb for update in cfg.updates for lb in update.labels}


def get_github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        r = subprocess.run(
            ["git", "config", "hub.oauthtoken"],
            stdout=subprocess.PIPE,
            text=True,
        )
        if r.returncode != 0 or not r.stdout.strip():
            raise click.UsageError(
                "GitHub OAuth token not set.  Set via GITHUB_TOKEN"
                " environment variable or hub.oauthtoken Git config option."
            )
        token = r.stdout.strip()
    return token


def ensure_labels(repo: Repository, labels: dict[str, LabelDetails]) -> None:
    extant = {lb.name: lb for lb in repo.get_labels()}
    for name, details in labels.items():
        try:
            lb = extant[name]
        except KeyError:
            log.info("Creating label %r", name)
            repo.create_label(
                name, color=details.color, description=details.description
            )
        else:
            if lb.color != details.color or lb.description != details.description:
                log.info("Editing label %r", name)
                lb.edit(name, color=details.color, description=details.description)


@click.command()
@click.argument(
    "dirpath",
    type=click.Path(file_okay=False, exists=True, path_type=Path),
    required=False,
)
def main(dirpath: Optional[Path]) -> None:
    logging.basicConfig(
        format="[%(levelname)-8s] %(message)s",
        level=logging.INFO,
    )
    label_names = get_custom_labels(dirpath)
    if not label_names:
        log.info("No Dependabot labels to configure")
        return
    labels = []
    for lb in label_names:
        try:
            labels.append(LABELS[lb])
        except KeyError:
            raise click.UsageError(f"Unknown label {lb!r}")
    gh = Github(get_github_token())
    repo = gh.get_repo(str(get_local_repo(dirpath)))
    ensure_labels(repo, labels)


if __name__ == "__main__":
    main()
