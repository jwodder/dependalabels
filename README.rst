.. image:: https://www.repostatus.org/badges/latest/concept.svg
    :target: https://www.repostatus.org/#concept
    :alt: Project Status: Concept – Minimal or no implementation has been done
          yet, or the repository is only intended to be a limited example,
          demo, or proof-of-concept.

.. image:: https://github.com/jwodder/dependalabels/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/dependalabels/actions?workflow=Test
    :alt: CI Status

.. image:: https://img.shields.io/github/license/jwodder/dependalabels.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/dependalabels>`_
| `Issues <https://github.com/jwodder/dependalabels/issues>`_

When setting up Dependabot_ to automatically create pull requests for
out-of-date dependencies, you have the option of specifying custom labels
to be applied to these PRs; however, if you forget to actually create the
labels in your repository, Dependabot won't create them for you, and so they
won't be used.

The ``dependalabels`` command provides a simple solution: it extracts the
custom labels from your ``dependabot.yml`` file and ensures that the labels all
exist in your GitHub repository.

.. _Dependabot: https://docs.github.com/en/code-security/dependabot


Installation
============
``dependalabels`` requires Python 3.10 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install git+https://github.com/jwodder/dependalabels.git


Usage
=====

::

    dependalabels [<options>] [<dirpath>]

``dependalabels`` operates on the Git repository at the specified path,
defaulting to the current directory.  The repository's ``origin`` remote must
point to a corresponding GitHub repository.  ``dependalabels`` reads
``.github/dependabot.yml`` at the root of the local repository and ensures that
each custom label listed therein exists in the GitHub repository.

``dependalabels`` predefines certain labels and gives them specific colors and
descriptions; all other labels are given random colors and empty descriptions.

Options
-------

-f, --force             If a predefined label already exists in the GitHub
                        repository, ensure its color and description have the
                        same values as used by ``dependalabels`` when creating
                        the label.

Authentication
--------------

``dependalabels`` requires a GitHub access token with appropriate permissions
in order to run.  Specify the token either via the ``GITHUB_TOKEN`` environment
variable or as the value of the ``hub.oauthtoken`` Git config option in your
``~/.gitconfig`` file.
