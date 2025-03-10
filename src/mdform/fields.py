"""
mdform.fields
~~~~~~~~~~~~~

Labeled field               <label> =
Labeled required field      <label>* =

Specific fields:
    - StringField           ___[length]
                            (length is optional)
    - IntegerField          ###[min:max:step]
                            (min, max, step are optional)
    - DecimalField          #.#[min:max:step:places]
                            (min, max, step, places are optional)
    - FloatField            #.#f[min:max:step]
                            (min, max, step are optional)
    - TextAreaField         AAA[length]
                            (length is optional)
    - DateField             d/m/y
    - TimeField             hh:mm
    - EmailField            @
    - RadioField            (x) A () B
                            (the x is optional, defines a default choice)
    - CheckboxField         [x] A [] B
                            (the x is optional, defines a default choice)
    - SelectField           {(A), B}
                            (the parenthesis are optional, defines a default choice)
    - FileField             ...[allowed]
                            (allowed is optional, extensions; description)

Organization:
    - Section
        [section:name]      name is a string which is prepended
                            to the field names
    - Collapsable part      control is the name of the field
                            controlling open and close
        [collapse:control]      of this part.
        [endcollapse]           - Use [o] to indicate that selecting
                                  that option should open the part
                                - Use [c] to indicate that selecting
                                  that option should close the part

:copyright: 2023 by mdform Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import re
import typing
from abc import abstractmethod
from dataclasses import dataclass
from re import Match, Pattern
from typing import Any, ClassVar, TypeVar

#: End of s with spaces or tabs before.
EOL = r"[ \t]?$"

#: Section definition.
SECTION_RE = re.compile(r"\[section[ \t]*(:(?P<name>.*))?\]", re.UNICODE)

#: Open of collapsable part.
COLLAPSE_OPEN_RE = re.compile(r"\[collapse[ \t]*(:(?P<name>.*))?\]", re.UNICODE)

#: Close of collapsable part.
COLLAPSE_CLOSE_RE = re.compile(r"\[endcollapse]")


T = TypeVar("T")


def _strgroup(m: Match[str], groupname: str) -> str:
    out = m.group(groupname)

    if not isinstance(out, str):
        raise Exception(
            f"Cannnot handle content in regex group {groupname}."
            f"Expected str, found {out} ({type(out)}))"
        )

    return out.strip()


def _strgroup_none(m: Match[str], groupname: str) -> str | None:
    out = m.group(groupname)

    if out is None:
        return None

    return _strgroup(m, groupname)


def _parse_or_none(el: str, typ: typing.Callable[[str], T]) -> T | None:
    el = el.strip()
    if el:
        return typ(el)
    return None


def _parse_or_raise(el: str, typ: typing.Callable[[str], T]) -> T:
    el = el.strip()
    if not el:
        raise ValueError("Cannot parse an empty string.")
    return typ(el)


def _parse_range_args(
    input: str | None, typ: typing.Callable[[str], T]
) -> tuple[T | None, T | None, T | None]:
    if input is None:
        return None, None, None

    s = input.lower().strip()

    if s == "":
        raise ValueError("Could not parse range arguments from empty string.")

    parts = [_parse_or_none(el, typ) for el in s.split(":")]

    if len(parts) == 1:
        return None, parts[0], None
    elif len(parts) == 2:
        return parts[0], parts[1], None
    elif len(parts) == 3:
        return parts[0], parts[1], parts[2]

    raise ValueError(
        f"Could not parse range arguments from {input}."
        f"Up to 3 values expected, {len(parts)} given."
    )


def _parse_range_round_args(
    input: str | None, ndigits: int = 2
) -> tuple[float | None, float | None, float | None, int]:
    if input is None:
        return None, None, None, 2

    s = input.lower().strip()

    if s == "":
        raise ValueError("Could not parse range-round arguments from empty string.")

    parts = s.split(":")

    if len(parts) > 4:
        raise ValueError(
            f"Could not parse range arguments from {input}."
            f"Up to 4 values expected, {len(parts)} given."
        )

    if len(parts) == 4:
        ndigits = _parse_or_raise(parts[3], int)

    range_parts = [_parse_or_none(el, float) for el in parts[:3]]

    if len(range_parts) == 1:
        return None, range_parts[0], None, ndigits
    elif len(parts) == 2:
        return range_parts[0], range_parts[1], None, ndigits
    else:
        return range_parts[0], range_parts[1], range_parts[2], ndigits


@dataclass(frozen=True)
class _RegexField:
    #: The compiled regex pattern to match.
    _REGEX: ClassVar[Pattern[str]]

    #: The regex pattern to match
    _PATTERN: ClassVar[str] = ""

    @classmethod
    def _preprocess_pattern(cls):
        """Overload this method in subclass to modify
        a regex pattern before compiling."""
        return cls._PATTERN

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if cls._PATTERN:
            cls._REGEX = re.compile(cls._preprocess_pattern(), re.UNICODE)


@dataclass(frozen=True)
class Field(_RegexField):
    """A field of any kind with label.

    Used as an entry point, it match the label
    and then test all registered specific fields.

    The format for optional fields is:

        label = <pending>

    and for required fields is:

        label* = <pending>

    where `<pending>` is the specific field.

    """

    _PATTERN = (
        r"(?P<label>\w[\w \t\-]*)(?P<required>\*)?[ \t]*=[ \t]*(?P<pending>.*)[ \t]*"
        + EOL
    )

    _FIELD_TYPES: ClassVar[list[type[SpecificField]]] = []

    original_label: str
    required: bool
    specific_field: SpecificField

    @property
    def is_label_hidden(self) -> bool:
        """Return true if the label is supposed to be hidden (starts with _)"""
        return self.original_label.startswith("_")

    @property
    def label(self) -> str:
        if self.is_label_hidden:
            return self.original_label[1:]
        return self.original_label

    @classmethod
    def match(cls, s: str) -> tuple[str, bool, SpecificField] | None:
        """Match a string containing (maybe) a form field with label.

        Returns None if no field was match
        """
        m = cls._REGEX.match(s)
        if not m:
            return None

        for ft in cls._FIELD_TYPES:
            matched = ft.match(_strgroup(m, "pending"))

            if matched is None:
                continue

            label = _strgroup(m, "label")
            required = m.group("required") is not None

            return label, required, ft(**matched)

        return None

    @classmethod
    def from_str(cls, s: str) -> Field:
        m = cls.match(s)
        if m is not None:
            label, required, spefic_field = m
            return cls(label, required, spefic_field)
        raise ValueError("Could not match labeled field")


@dataclass(frozen=True)
class SpecificField(_RegexField):
    """Base class for all specific fields."""

    @classmethod
    def _preprocess_pattern(cls):
        return "[ \t]*" + cls._PATTERN + "[ \t]*" + EOL

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        Field._FIELD_TYPES.append(cls)

    @classmethod
    @abstractmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        """Process a matched string. Usually you must subclass this
        to produce
        """

    @classmethod
    def match(cls, line: str) -> dict[str, Any] | None:
        """Try to match the pattern to the provided s.

        Parameters
        ----------
        line : str
            The s to be parsed.

        Returns
        -------
        None or dict
            None indicates that the s was not matched.
        """

        m = cls._REGEX.match(line)
        if not m:
            return None

        return cls.process(m)


@dataclass(frozen=True)
class StringField(SpecificField):
    """Used to take single string input."""

    _PATTERN = r"___(\[(?P<length>\d*)\])?"

    length: int | None

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


@dataclass(frozen=True)
class IntegerField(SpecificField):
    """Used to take single integer input."""

    _PATTERN = r"###(\[(?P<range>[\d:]*)\])?"

    min: int | None = None
    max: int | None = None
    step: int | None = None

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        try:
            mn, mx, step = _parse_range_args(_strgroup_none(m, "range"), int)
        except Exception:
            return None

        return dict(min=mn, max=mx, step=step)


@dataclass(frozen=True)
class DecimalField(SpecificField):
    """Used to take single decimal input."""

    _PATTERN = r"#\.#(\[(?P<range>[\d\.:]*)\])?"

    min: float | None = None
    max: float | None = None
    step: float | None = None
    places: int | None = 2

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        try:
            mn, mx, step, places = _parse_range_round_args(_strgroup_none(m, "range"))
        except Exception:
            return None

        return dict(min=mn, max=mx, step=step, places=places)


@dataclass(frozen=True)
class FloatField(SpecificField):
    """Used to take single float input."""

    _PATTERN = r"#\.#f(\[(?P<range>[\d\.:]*)\])?"

    min: float | None = None
    max: float | None = None
    step: float | None = None

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        try:
            mn, mx, step = _parse_range_args(_strgroup_none(m, "range"), float)
        except Exception:
            return None

        return dict(min=mn, max=mx, step=step)


@dataclass(frozen=True)
class TextAreaField(SpecificField):
    """Used to take multi-line input."""

    _PATTERN = r"AAA(\[(?P<length>\d*)\])?"

    length: int | None = None

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        length = m.group("length") or None
        if length is not None:
            length = int(length)

        return dict(length=length)


@dataclass(frozen=True)
class DateField(SpecificField):
    """Used to take date input.

    Currently, there is no way to specify the format.
    """

    _PATTERN = r"d/m/y"

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        return dict()


@dataclass(frozen=True)
class TimeField(SpecificField):
    """Used to take time input.

    Currently, there is no way to specify the format.
    """

    _PATTERN = r"hh:mm"

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        return dict()


@dataclass(frozen=True)
class EmailField(SpecificField):
    """A string field with email validation."""

    _PATTERN = r"@"

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        return dict()


@dataclass(frozen=True)
class RadioField(SpecificField):
    """Used to select among mutually exclusive inputs."""

    _PATTERN = r"(?P<content>\(x?\)[ \t]*[\w \t\-]+[\(\)\w \t\-]*)"

    _SUB_REGEX = re.compile(
        r"\((?P<is_default>x?)\)[ \t]*(?P<label>[a-zA-Z0-9 \t_\-]*)", re.UNICODE
    )

    choices: tuple[str, ...]
    default: str

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        items: list[str] = []
        default = None

        for matched in cls._SUB_REGEX.finditer(_strgroup(m, "content")):
            label = matched.group("label").strip()

            items.append(label)

            if matched.group("is_default") == "x":
                default = label

        return dict(choices=tuple(items), default=default)


@dataclass(frozen=True)
class CheckboxField(SpecificField):
    """Used to select among non-exclusive inputs."""

    _PATTERN = r"(?P<content>\[x?\][ \t]*[\w \t\-]+[\[\]\w \t\-]*)"
    _SUB_REGEX = re.compile(
        r"\[(?P<is_default>x?)\][ \t]*(?P<label>[a-zA-Z0-9 \t_\-]*)", re.UNICODE
    )

    choices: tuple[str, ...]
    default: str

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        items: list[str] = []
        default: list[str] = []

        for matched in cls._SUB_REGEX.finditer(_strgroup(m, "content")):
            label = _strgroup(matched, "label").strip()

            items.append(label)

            if _strgroup(matched, "is_default") == "x":
                default.append(label)

        return dict(choices=tuple(items), default=tuple(default))


@dataclass(frozen=True)
class SelectField(SpecificField):
    """Used to select among mutually exclusive inputs, with a dropdown."""

    _PATTERN = r"\{(?P<content>([\w \t\->_,\(\)\[\]]+))\}"

    choices: tuple[tuple[str, str], ...]
    default: str
    collapse_on: str

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
        items: list[tuple[str, str]] = []
        default = None

        collapse_on = None

        for item in _strgroup(m, "content").split(","):
            is_default = False

            item = item.strip()
            if item.startswith("(") and item.endswith(")"):
                item = item[1:-1].strip()
                is_default = True

            if "->" in item:
                pair: tuple[str, str] = tuple(s.strip() for s in item.split("->", 1))  # type: ignore
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


@dataclass(frozen=True)
class FileField(SpecificField):
    """Used to upload a file."""

    _PATTERN = r"\.\.\.(\[(?P<allowed>[\w \t,;]*)\])?"

    allowed: tuple[str, ...] | None
    description: str | None

    @classmethod
    def process(cls, m: Match[str]) -> dict[str, Any] | None:
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
