"""
Create GitHub PR labels used by Dependabot config

When setting up Dependabot_ to automatically create pull requests for
out-of-date dependencies, you have the option of specifying custom labels
to be applied to these PRs; however, if you forget to actually create the
labels in your repository, Dependabot won't create them for you, and so they
won't be used.

The ``dependalabels`` command provides a simple solution: it extracts the
custom labels from your ``dependabot.yml`` file and ensures that the labels all
exist in your GitHub repository.

.. _Dependabot: https://docs.github.com/en/code-security/dependabot

Visit <https://github.com/jwodder/dependalabels> for more information.
"""

__version__ = "0.1.0.dev"
__author__ = "John T. Wodder II"
__author_email__ = "dependalabels@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/dependalabels"
