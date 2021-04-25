"""
    mdform
    ~~~~~~

    An extension for `python-markdown`_ to generate parse forms in Markdown based document.

    :copyright: 2020 by mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import pkg_resources
from markdown import Markdown

from .extension import FormExtension

try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution("mdform").version
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"

__all__ = (FormExtension, __version__, Markdown)
