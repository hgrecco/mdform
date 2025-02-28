"""
mdform.extension
~~~~~~~~~~~~~~~~

An extension for `python-markdown`_ to generate parse forms
in Markdown based document.

:copyright: 2023 by mdform Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import re
import typing as ty
from typing import Any

import unidecode
from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from .fields import COLLAPSE_CLOSE_RE, COLLAPSE_OPEN_RE, SECTION_RE, Field

COLLAPSE_OPEN_HTML = r'<div id="accordion-%s">'
COLLAPSE_CLOSE_HTML = r"</div>"


FormDefinition = dict[str, Field]
Sanitizer = ty.Callable[[str], str]
FieldFormatter = ty.Callable[[str, Field], str]


def default_label_sanitizer(s: str) -> str:
    """Default label to variable sanitizer

    Parameters
    ----------
    s : str
        label

    Returns
    -------
    str
        an identifier representing the variable
    """

    out: str = unidecode.unidecode(s)

    # Remove invalid characters
    out = re.sub(r"[^0-9a-zA-Z_]", "_", out)

    # Remove leading characters until we find a letter or underscore
    out = re.sub(r"^[^a-zA-Z_]+", "_", out)

    return out


def default_field_formatter(variable_name: str, field: Field) -> str:
    """Default form field formatter.

    Parameters
    ----------
    variable_name : str
        field name.
    field : Field
        definition of the field.

    Returns
    -------
    str
        an HTML or similar formatter.
    """
    return "{{ " + f"form.{variable_name}" + " }}"


def _value_to_name(value: str | None) -> str:
    if value is None:
        return ""
    return value.lower().strip()


class FormPreprocessor(Preprocessor):
    """Form processor for Python-Markdown.

    Parameters
    ----------
    md
    sanitizer : callable str -> str
        label sanitizer function that will be used.
    formatter : callable (str, Field) -> str
        form field formatter function.
    """

    def __init__(
        self,
        md: Markdown,
        sanitizer: Sanitizer = default_label_sanitizer,
        formatter: FieldFormatter = default_field_formatter,
    ):
        super().__init__(md)
        self.sanitizer = sanitizer
        self.formatter = formatter

    def run(self, lines: ty.Iterable[str]) -> list[str]:
        """Parse Form and store in Markdown.Form."""
        unnamed_collapese_cnt = 0
        form = {}
        section = None

        out: list[str] = []
        for line in lines:
            m1 = SECTION_RE.match(line)
            if m1:
                section = _value_to_name(m1.group("name"))
                continue

            m1 = COLLAPSE_OPEN_RE.match(line)
            if m1:
                control_field = _value_to_name(m1.group("name"))
                if control_field:
                    control_field = self.sanitizer(control_field)
                else:
                    control_field = str(unnamed_collapese_cnt)
                    unnamed_collapese_cnt += 1
                if section:
                    control_field = f"{section}_{control_field}"

                out.append(COLLAPSE_OPEN_HTML % control_field)
                continue

            m1 = COLLAPSE_CLOSE_RE.match(line)
            if m1:
                out.append(COLLAPSE_CLOSE_HTML)
                continue

            try:
                field = Field.from_str(line)
            except ValueError:
                out.append(line)
                continue

            variable_name = self.sanitizer(field.label.lower())

            if section:
                variable_name: str = f"{section}_{variable_name}"

            if variable_name in form:
                raise ValueError(
                    f"Duplicate variable name found in form: {variable_name}"
                )

            form[variable_name] = field

            out.append(self.formatter(variable_name, field))

        self.md.mdform_definition = form  # type: ignore
        return out


class FormExtension(Extension):
    """Form extension for Python-Markdown."""

    # Implementation note: we do not implement reset
    # as the only property (mdform_definition) is
    # overwritten in each run.

    def __init__(self, **kwargs: Any):
        self.config = {
            "sanitizer": [default_label_sanitizer, "Function to sanitize the label"],
            "formatter": [
                default_field_formatter,
                "Use format template for fields. "
                "The signature must be (str, dict)->str",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown):
        md.preprocessors.register(
            FormPreprocessor(
                md, self.getConfig("sanitizer"), self.getConfig("formatter")
            ),
            "form",
            30,
        )


def makeExtension(**kwargs: Any):
    return FormExtension(**kwargs)  # pragma: no cover
