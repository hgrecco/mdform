"""
    mdform.extension
    ~~~~~~~~~~~~~~~~

    An extension for `python-markdown`_ to generate parse forms in Markdown based document.

    :copyright: 2020 by mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import re
from typing import Dict

import unidecode
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from .fields import COLLAPSE_CLOSE_RE, COLLAPSE_OPEN_RE, SECTION_RE, Field, FieldDict

COLLAPSE_OPEN_HTML = r'<div id="accordion-%s">'
COLLAPSE_CLOSE_HTML = r"</div>"


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

    s = unidecode.unidecode(s)

    # Remove invalid characters
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s)

    # Remove leading characters until we find a letter or underscore
    s = re.sub(r"^[^a-zA-Z_]+", "_", s)

    return s


def default_field_formatter(variable_name: str, variable_dict: FieldDict) -> str:
    """Default form field formatter.

    Parameters
    ----------
    variable_name : str
        field name.
    variable_dict : FieldDict
        definition dictionary of the field.

    Returns
    -------
    str
        an HTML or similar formatter.
    """
    return "{{ " + f"form.{variable_name}" + " }}"


def _value_to_name(value):
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
    formatter : callable (str, dict) -> str
        form field formatter function.
    """

    # dictionary mapping labels to
    mdform_definition: Dict[str, FieldDict] = {}

    def __init__(self, md, sanitizer=None, formatter=default_field_formatter):
        self.sanitizer = sanitizer or (lambda s: s)
        if formatter is None:
            formatter = default_field_formatter
        self.formatter = formatter
        super().__init__(md)

    def run(self, lines):
        """ Parse Form and store in Markdown.Form. """
        unnamed_collapese_cnt = 0
        form = {}
        section = None

        out = []
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
                    control_field = "%s_%s" % (section, control_field)

                out.append(COLLAPSE_OPEN_HTML % control_field)
                continue

            m1 = COLLAPSE_CLOSE_RE.match(line)
            if m1:
                out.append(COLLAPSE_CLOSE_HTML)
                continue

            label_value = Field.match(line)

            if label_value:
                label, value = label_value

                nolabel = False
                if label.startswith("_"):
                    label = label[1:]
                    nolabel = True

                variable_name = self.sanitizer(label.lower())

                if section:
                    variable_name = "%s_%s" % (section, variable_name)

                form[variable_name] = variable_dict = dict(
                    label=label, nolabel=nolabel, **value
                )

                out.append(self.formatter(variable_name, variable_dict))
            else:
                out.append(line)

        self.md.mdform_definition = form
        return out


class FormExtension(Extension):
    """Form extension for Python-Markdown."""

    def __init__(self, **kwargs):
        self.config = {
            "sanitizer": [default_label_sanitizer, "Function to sanitize the label"],
            "formatter": [
                default_field_formatter,
                "Use format template for fields. The signature must be (str, dict)->str",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.md = md
        md.preprocessors.register(
            FormPreprocessor(
                md, self.getConfig("sanitizer"), self.getConfig("formatter")
            ),
            "form",
            30,
        )

    def reset(self):
        self.md.mdform_definition = {}


def makeExtension(**kwargs):
    return FormExtension(**kwargs)
