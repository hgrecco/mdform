"""
    mdform
    ~~~~~~

    An extension for `python-markdown`_ to generate parse forms
    in Markdown based document.

    :copyright: 2023 by mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import pkg_resources
from markdown import Markdown

from .extension import FormExtension
from .fields import Field

try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution("mdform").version
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"


def parse(text: str, formatter=None) -> tuple[str, dict[str, Field]]:
    md = Markdown(extensions=[FormExtension(formatter=formatter)])
    html = md.convert(text)
    form_def = md.mdform_definition
    return html, form_def


__all__ = (FormExtension, __version__, Markdown, parse)
