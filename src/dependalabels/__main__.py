from __future__ import annotations
import logging
from pathlib import Path
import subprocess
import click
from ghrepo import get_local_repo
from ghtoken import GHTokenNotFound, get_ghtoken
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from . import __version__
from .client import Client
from .labels import PREDEFINED, LabelDetails

log = logging.getLogger()


class DependabotUpdate(BaseModel):
    labels: list[str] = Field(default_factory=list)


class DependabotConfig(BaseModel):
    updates: list[DependabotUpdate]


def get_custom_labels(dirpath: Path | None) -> set[str]:
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


@click.command()
@click.version_option(
    __version__,
    "-V",
    "--version",
    message="%(prog)s %(version)s",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Ensure predefined labels have the same colors & descriptions as when created",
)
@click.argument(
    "dirpath",
    type=click.Path(file_okay=False, exists=True, path_type=Path),
    required=False,
)
def main(dirpath: Path | None, force: bool) -> None:
    """
    Create GitHub PR labels used by Dependabot config

    Visit <https://github.com/jwodder/dependalabels> for more information.
    """
    logging.basicConfig(
        format="[%(levelname)-8s] %(message)s",
        level=logging.INFO,
    )
    label_names = get_custom_labels(dirpath)
    if not label_names:
        log.info("No Dependabot labels to configure")
        return
    try:
        token = get_ghtoken()
    except GHTokenNotFound:
        raise click.UsageError(
            "GitHub token not found.  Set via GH_TOKEN, GITHUB_TOKEN, gh, hub,"
            " or hub.oauthtoken."
        )
    with Client(repo=get_local_repo(dirpath), token=token) as client:
        labeler = client.get_label_maker()
        for name in label_names:
            try:
                details = PREDEFINED[name]
                force_this = force
            except KeyError:
                details = LabelDetails.random()
                force_this = False
            labeler.ensure_label(name, details, force=force_this)


if __name__ == "__main__":
    main()
