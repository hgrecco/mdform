"""
    mdform.fields
    ~~~~~~~~~~~~~

    Labeled field               <label> =
    Labeled required field      <label>* =

    Fields:
        - StringField           ___[length]     (length is optional)
        - IntegerField          ###[min:max:step]
        - FloatField            #.#[min:max:step]
        - TextAreaField         AAA[length]     (length is optional)
        - DateField             d/m/y
        - TimeField             hh:mm
        - EmailField            @
        - RadioField            (x) A () B      (the x is optional, defines a default choice)
        - CheckboxField         [x] A [] B      (the x is optional, defines a default choice)
        - SelectField           {(A), B}        (the parenthesis are optional, defines a default choice)
        - FileField             ...[allowed]    (allowed is optional, extensions; description)

    Organization:
        - Section
            [section:name]      name is a string which is prepended to the field names
        - Collapsable part      control is the name of the field controlling open and close
            [collapse:control]      of this part.
            [endcollapse]           - Use [o] to indicate that selecting that option should open the part
                                    - Use [c] to indicate that selecting that option should close the part

    :copyright: 2020 by mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import re
from abc import abstractmethod
from typing import Any, AnyStr, Dict, Match, NewType, Optional, Pattern, Tuple

FieldDict = NewType("FieldDict", Dict[str, Any])

#: End of line with spaces or tabs before.
EOL = r"[ \t]?$"

#: Section definition.
SECTION_RE = re.compile(r"\[section[ \t]*(:(?P<name>.*))?\]", re.UNICODE)

#: Open of collapsable part.
COLLAPSE_OPEN_RE = re.compile(r"\[collapse[ \t]*(:(?P<name>.*))?\]", re.UNICODE)

#: Close of collapsable part.
COLLAPSE_CLOSE_RE = re.compile(r"\[endcollapse]")


def _parse_or_none(el: str, typ):
    if el == "none":
        return None
    return typ(el)


def _parse_range_args(s: str, typ):
    if s is None:
        return None, None, None

    s = [_parse_or_none(el, typ) for el in s.lower().strip().split(":")]

    if len(s) == 1:
        return None, s[0], None
    elif len(s) == 2:
        return s[0], s[1], None
    elif len(s) == 3:
        return s[0], s[1], s[2]

    raise ValueError


class _RegexField:

    #: The regex pattern to match
    PATTERN: str = ""

    #: The compiled regex pattern to match.
    REGEX: Pattern

    @classmethod
    def _preprocess_pattern(cls):
        return cls.PATTERN

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.PATTERN:
            cls.REGEX = re.compile(cls._preprocess_pattern(), re.UNICODE)


class Field(_RegexField):
    """A field of any kind with label.

    Used as an entry point, it match the label and then test all registered specific fields.

    The format for optional fields is:

        label = <pending>

    and for required fields is:

        label* = <pending>

    where `<pending>` is the specific field.

    """

    PATTERN = (
        r"(?P<label>\w[\w \t\-]*)(?P<required>\*)?[ \t]*=[ \t]*(?P<pending>.*)[ \t]*"
        + EOL
    )

    FIELD_TYPES = []

    @classmethod
    def match(cls, line: str) -> Optional[Tuple[str, FieldDict]]:
        """Match a string containing (maybe) a form field with label.

        Returns None if no field was match
        """
        m = cls.REGEX.match(line)
        if not m:
            return None

        for ft in cls.FIELD_TYPES:
            matched = ft.match(m.group("pending"))

            if matched is None:
                continue

            label = m.group("label").strip()
            required = not m.group("required") is None

            return label, FieldDict(
                dict(type=ft.__name__, required=required, **matched)
            )

        return None


class SpecificField(_RegexField):
    """Base class for all specific fields."""

    @classmethod
    def _preprocess_pattern(cls):
        return "[ \t]*" + cls.PATTERN + "[ \t]*" + EOL

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Field.FIELD_TYPES.append(cls)

    @classmethod
    @abstractmethod
    def process(cls, m: Optional[Match[AnyStr]]) -> FieldDict:
        """Process a matched string. Usually you must subclass this
        to produce
        """

    @classmethod
    def match(cls, line: str) -> Optional[FieldDict]:
        """Try to match the pattern to the provided line.

        Parameters
        ----------
        line : str
            The line to be parsed.
        Returns
        -------
        None or dict
            None indicates that the line was not matched.
        """

        m = cls.REGEX.match(line)
        if not m:
            return None

        return cls.process(m)


class StringField(SpecificField):
    """Used to take single line input."""

    PATTERN = r"___(\[(?P<length>\d*)\])?"

    @classmethod
    def process(cls, m):
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


class IntegerField(SpecificField):
    """Used to take single line input."""

    PATTERN = r"###(\[(?P<range>[\d:]*)\])?" + EOL

    @classmethod
    def process(cls, m):
        try:
            mn, mx, step = _parse_range_args(m.group("range"), int)
        except Exception:
            return None

        return dict(min=mn, max=mx, step=step)


class FloatField(SpecificField):
    """Used to take single line input."""

    PATTERN = r"#\.#(\[(?P<range>[\d\.:]*)\])?" + EOL

    @classmethod
    def process(cls, m):
        try:
            mn, mx, step = _parse_range_args(m.group("range"), float)
        except Exception:
            return None

        return dict(min=mn, max=mx, step=step)


class TextAreaField(SpecificField):
    """Used to take multi-line input."""

    PATTERN = r"AAA(\[(?P<length>\d*)\])?" + EOL

    @classmethod
    def process(cls, m):
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


class DateField(SpecificField):
    """Used to take date input.

    Currently, there is no way to specify the format.
    """

    PATTERN = r"d/m/y"

    @classmethod
    def process(cls, m):
        return dict()


class TimeField(SpecificField):
    """Used to take time input.

    Currently, there is no way to specify the format.
    """

    PATTERN = r"hh:mm"

    @classmethod
    def process(cls, m):
        return dict()


class EmailField(SpecificField):
    """A string field with email validation."""

    PATTERN = r"@"

    @classmethod
    def process(cls, m):
        return dict()


class RadioField(SpecificField):
    """Used to select among mutually exclusive inputs."""

    PATTERN = r"(?P<content>\(x?\)[ \t]*[\w \t\-]+[\(\)\w \t\-]*)"

    SUBREGEX = re.compile(
        r"\((?P<is_default>x?)\)[ \t]*(?P<label>[a-zA-Z0-9 \t_\-]?)", re.UNICODE
    )

    @classmethod
    def process(cls, m):
        items = []
        default = None

        for matched in cls.SUBREGEX.finditer(m.group("content")):
            label = matched.group("label").strip()

            items.append(label)

            if matched.group("is_default") == "x":
                default = label

        return dict(choices=tuple(items), default=default)


class CheckboxField(SpecificField):
    """Used to select among non-exclusive inputs."""

    PATTERN = r"(?P<content>\[x?\][ \t]*[\w \t\-]+[\[\]\w \t\-]*)"
    SUBREGEX = re.compile(
        r"\[(?P<is_default>x?)\][ \t]*(?P<label>[a-zA-Z0-9 \t_\-]?)", re.UNICODE
    )

    @classmethod
    def process(cls, m):
        items = []
        default = []

        for matched in cls.SUBREGEX.finditer(m.group("content")):
            label = matched.group("label").strip()

            items.append(label)

            if matched.group("is_default") == "x":
                default.append(label)

        return dict(choices=tuple(items), default=tuple(default))


class SelectField(SpecificField):
    """Used to select among mutually exclusive inputs, with a dropdown."""

    PATTERN = r"\{(?P<content>([\w \t\->_,\(\)\[\]]+))\}"

    @classmethod
    def process(cls, m):
        items = []
        default = None

        collapse_on = None

        for item in m.group("content").split(","):
            is_default = False

            item = item.strip()
            if item.startswith("(") and item.endswith(")"):
                item = item[1:-1].strip()
                is_default = True

            if "->" in item:
                pair = tuple(s.strip() for s in item.split("->"))
            else:
                pair = (item, item)

            if "[c]" in pair[0]:
                # collapse
                if collapse_on is not None:
                    raise ValueError("Can only collapse on a single item.")
                item0 = pair[0].replace("[c]", "")
                item1 = pair[1].replace("[c]", "")
                collapse_on = item0
                pair = (item0, item1)

            if "[o]" in pair[0]:
                # open
                if collapse_on is not None:
                    raise ValueError("Can only collapse on a single item.")
                item0 = pair[0].replace("[o]", "")
                item1 = pair[1].replace("[o]", "")
                collapse_on = "~" + item0
                pair = (item0, item1)

            items.append(pair)
            if is_default:
                default = pair[0]

        return dict(choices=tuple(items), default=default, collapse_on=collapse_on)


class FileField(SpecificField):
    """Used to upload a file."""

    PATTERN = r"...(\[(?P<allowed>[\w \t,;]*)\])?" + EOL

    @classmethod
    def process(cls, m):
        allowed = m.group("allowed") or None
        description = None

        if allowed is not None:
            if ";" in allowed:
                allowed, description = allowed.split(";", 1)

            if "," in allowed:
                allowed = tuple(s.strip() for s in allowed.split(","))
            else:
                allowed = (allowed,)

        return dict(allowed=allowed, description=description)
