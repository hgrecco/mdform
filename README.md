![PyVersion](https://img.shields.io/pypi/pyversions/mdform?label=python)
![Package](https://img.shields.io/pypi/v/mdform?label=PyPI)
![License](https://img.shields.io/pypi/l/mdform?label=license)
[![CI](https://github.com/hgrecco/mdform/actions/workflows/ci.yml/badge.svg)](https://github.com/hgrecco/mdform/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/hgrecco/mdform/main.svg)](https://results.pre-commit.ci/latest/github/hgrecco/mdform/main)

# mdform

An extension for [python-markdown](https://python-markdown.github.io/)
to parse forms in a Markdown document.

This document:

```text
Please fill this form:

name* = ___
email = @

And also this important question:

Do you like this = () YES () NO
```

will generate the following html template:

```jinja2
Please fill this form:

{{ form.name }}
{{ form.email }}

And also this important question:

{{ form.do_you_like_this }}
```

and this form definition dictionary:

```python
{
    "name": Field(
        original_label="name", required=True, specific_field=StringField(length=None)
    ),
    "email": Field(original_label="email", required=False, specific_field=EmailField()),
    "do_you_like_this": Field(
        original_label="Do you like this",
        required=False,
        specific_field=RadioField(choices=("Y", "N"), default=None),
    ),
}
```

that you can consume to generate a form. See how we use it in
[flask-mdform](https://github.com/hgrecco/flask-mdform)

## Installation

```bash
pip install mdform
```

## Usage

```python
>>> import mdform
>>> text = "name* = ___"
>>> html, form_definition = mdform.parse(text)
```

## Syntax

The syntax is strongly based on this
[wmd](https://github.com/brikis98/wmd) fork. Briefly, each field has a
label, an optional flag to indicate if the field is required and, after
the equal, the specification of the type of field

For example, a required text field (notice the `*`):

```text
name* = ___
```

An optional text field (notice the lack of `*`):

```text
name = ___
```

An optional email field (notice the `___` is now`@`):

```text
email = @
```

Each field is parsed into an object with the following attributes

- **original_label**: `str`, label as given in the markdown
  text.
- **required**: `bool`, indicate if the `*` was
  present.
- **specific_field**: `object`, describing the field in more
  detail that might contain additional attributes.

Additionally, it has two properties:

- **is_label_hidden**: bool, indicates if `original_label`
  starts with `_` which can be used downstream to
  indicate the label should not be displayed.
- **label**: str, a clean version of `original_label` in which
  `_` prefix has been removed.

In the following lines, we will describe the syntax for each specific
field.

### Text fields (StringField)

```text
name = ___
```

or:

```text
name = ___[50]
```

Exactly 3 underscores will be matched. More will be handled as
standard underline directives.

Customizing:

```text
name = ___[length]
```

Specific field attributes:

- **length**: int or None (default)

### Integer fields (IntegerField)

```text
value = ###
```

or:

```text
value = ###[0:2:1]
```

Exactly 3 numeral will be matched. Any more will be handled as standard
directives.

Customizing:

```text
value = ###[range]
```

The `range` is parsed like a numpy range.

Specific field attributes:

- **min**: int or None (default)
- **max**: int or None (default)
- **step**: int or None (default)

### Float fields (FloatField)

```text
value = #.#f
```

or:

```text
value = #.#f[0:2:0.5]
```

Exactly 3 numbers will be matched. More will be handled as standard
directives.

Customizing:

```text
value = #.#f[range]
```

The `range` is parsed like a numpy range.

Specific field attributes:

- **min**: float or None (default)
- **max**: float or None (default)
- **step**: float or None (default)

### Decimal fields (DecimalField)

```text
value = #.#
```

or:

```text
value = #.#[0:2:0.5:1]
```

Exactly 4 numbers will be matched. More will be handled as standard
directives.

Customizing:

```text
value = #.#[range:places]
```

The `range` is parsed like a numpy range. The last (fourth
position) is always the place

Specific field attributes:

- **min**: float or None (default)
- **max**: float or None (default)
- **step**: float or None (default)
- **step**: int (default = 2)

### Text area (TextAreaField)

```text
name = AAA
```

or:

```text
name = AAA[50]
```

Exactly 3 slashes will be matched.

Customizing:

```text
name = ___[length]
```

Specific field attributes:

- **length**: int or None (default)

### Radio buttons (RadioField)

```text
sex = (x) male () female
```

Optionally, an `x` can be used to indicate the default
value.

Specific field attributes:

- **values**: tuple of str
- **default**: str

### Check boxes (CheckboxField)

```text
phones = [] Android [x] iPhone [x] Blackberry
```

Optionally, an `x` can be used to indicate the default
values.

Specific field attributes:

- **values**: tuple of strings
- **default**: tuple of str

### Drop down (SelectField)

```text
city = {BOS, SFO, (NYC)}
```

Or with user-friendly labels:

```text
city = {BOS -> Boston, SFO -> San Francisco, (NYC -> New York City)}
```

```text
city = {BOS, SFO, (NYC -> New York City)}
```

The option in parentheses will be the default.

Specific field attributes:

- **choices**: tuple of (str, str) (key, value)
- **default**: str
- **collapse_on**: str or None Item used to collapse. Format "~value"
  or "value"

### File Field (FileField)

```text
name = ...
```

or:

```text
name = ...[png]
```

```text
name = ...[png,jpg]
```

```text
name = ...[png,jpg;Only image files]
```

Specific field attributes:

- **allowed**: tuple of str
- **description**: str

### Date Field (DateField)

```text
name = d/m/y
```

### Time Field (TimeField)

```text
name = hh:mm
```

### Sections

In certain cases is useful to create a named section.

```text
[section:university]

name = ___

[section:school]

name = ___
```

will render as:

```jinja2
{{ form.university_name }}
{{ form.school_name }}
```

and the form definition dictionary:

```json
{
    "university_name": Field(
        original_label="name", required=True, specific_field=StringField(length=None)
    ),
    "school_name": Field(
        original_label="name", required=True, specific_field=StringField(length=None)
    ),
}
```

Notice that the key in the form definition dictionary (referred in the
code as `variable_name`) is not just the label: it now
contains the section name allowing multiple field with the same label.

Sections are labeled from top to bottom without nesting. To remove a
section name just do it this way.

```text
[section:university]

name = ___

[section]

name = ___
```

will render as:

```jinja2
{{ form.university_name }}
{{ form.name }}
```

### Collapsable parts

In certain cases is useful to create a part of the form which collapses
based on the value of a dropdown box. Just use the modifier
`[c]` or the dropdown item that will collapse the part of
the html and enclose the collapsable part as shown:

```text
extra = {Yes, (No[c])}

[collapse:extra]

name = ___

[endcollapse]
```

The `extra` in the `collapse` tag indicates
which dropdown box is used as control.

Alternative, you can specify in which option to open a collapsable part
with the modifier `o`:

```text
extra = {Yes[o], (No)}

[collapse:extra]

name = ___

[endcollapse]
```

## Syntax summary

```
Labeled field               <label> =
Labeled required field      <label>* =

Specific fields:
    - StringField           ___[length]         (length is optional)
    - IntegerField          ###[min:max:step]   (min, max, step are optional)
    - DecimalField          #.#[min:max:step:places]   (min, max, step, places are optional)
    - FloatField            #.#f[min:max:step]   (min, max, step are optional)
    - TextAreaField         AAA[length]         (length is optional)
    - DateField             d/m/y
    - TimeField             hh:mm
    - EmailField            @
    - RadioField            (x) A () B          (the x is optional, defines a default choice)
    - CheckboxField         [x] A [] B          (the x is optional, defines a default choice)
    - SelectField           {(A), B}            (the parenthesis are optional, defines a default choice)
    - FileField             ...[allowed]        (allowed is optional, extensions; description)

Organization:
    - Section
        [section:name]      name is a string which is prepended to the field names
    - Collapsable part      control is the name of the field controlling open and close
        [collapse:control]      of this part.
        [endcollapse]           - Use [o] to indicate that selecting that option should open the part
                                - Use [c] to indicate that selecting that option should close the part
```

## Customizing HTML output

The HTML field output can be fully customized by means of the formatter
parameter. For example, if you want to generate a
[Mako](https://www.makotemplates.org/) template just do the following:

```python
>>> def mako_field_formatter(variable_name, field):
...     return "${ " + f"form.{variable_name}" + " }"
>>>
>>> import mdform
>>> html, form_definition = mdform.parse(text, formatter=mako_field_formatter)
```

will generate the following html template:

```mako
Please fill this form:

${ form.name }
${ form.email }

And also this important question:

${ form.do_you_like_this }
```

The formatter function must take two arguments: the variable name and
the field object.

## Combining with other MD extensions

If you need to integrate `mdform` an existing workflow with
other extensions, just instantiate the markdown object as you normally
do it and pass the `FormExtension`. For example, here I am
combining `mdform` with the
[meta](https://python-markdown.github.io/extensions/meta_data/)
extension.

```python
>>> from mdform import FormExtension, Markdown # Markdown is just re-exported from python-markdown
>>> md = Markdown(extensions = [FormExtension(), 'meta'])
>>> html = md.convert(text)           # this is the jinja template
>>> form_def = md.mdform_definition   # this is the form definition
```

The form definition dict is now accesible through
`mdform_definition` attribute of the markdown object

To customize the formatter:

```python
>>> md = Markdown(extensions = [FormExtension(formatter=mako_field_formatter), 'meta'])
```

______________________________________________________________________

See [AUTHORS](https://github.com/hgrecco/mdform/blob/master/AUTHORS) for
a list of the maintainers.

To review an ordered list of notable changes for each version of a
project, see
[CHANGES](https://github.com/hgrecco/mdform/blob/master/CHANGES)
