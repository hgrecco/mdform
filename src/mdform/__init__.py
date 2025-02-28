"""
mdform
~~~~~~

An extension for `python-markdown`_ to generate parse forms
in Markdown based document.

:copyright: 2023 by mdform Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from markdown import Markdown

from .extension import (
    FieldFormatter,
    FormDefinition,
    FormExtension,
    Sanitizer,
    default_field_formatter,
)
from .fields import Field


def parse(
    text: str, formatter: FieldFormatter = default_field_formatter
) -> tuple[str, FormDefinition]:
    md = Markdown(extensions=[FormExtension(formatter=formatter)])
    html = md.convert(text)
    form_def: FormDefinition = md.mdform_definition  # type: ignore
    return html, form_def


__all__ = (
    "FormExtension",
    "Markdown",
    "parse",
    "Field",
    "Sanitizer",
    "FormDefinition",
    "FormDefinition",
)
