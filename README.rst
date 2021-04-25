.. image:: https://img.shields.io/pypi/v/mdform.svg
    :target: https://pypi.python.org/pypi/mdform
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/mdform.svg
    :target: https://pypi.python.org/pypi/mdform
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/mdform.svg
    :target: https://pypi.python.org/pypi/mdform
    :alt: Python Versions

.. image:: https://travis-ci.org/hgrecco/mdform.svg?branch=master
    :target: https://travis-ci.org/hgrecco/mdform
    :alt: CI

.. image:: https://coveralls.io/repos/github/hgrecco/mdform/badge.svg?branch=master
    :target: https://coveralls.io/github/hgrecco/mdform?branch=master
    :alt: Coverage



mdform
======

An extension for `python-markdown`_ to generate parse forms in Markdown
based document.

This document:

.. code-block:: text

    Please fill this form:

    name* = ___
    email = @

    And also this important question:

    Do you like this = () YES () NO

will generate the following jinja template:

.. code-block:: text

    Please fill this form:

    {{ form.name }}
    {{ form.email }}

    And also this important question:

    {{ form.do_you_like_this }}


and this definition dictionary:

.. code-block:: python

    {'name': {'type': 'StringField',
              'required': True,
              'length': None
              },
     'email': {'type': 'EmailField',
               'required': False
              },
     'do_you_like_this': {'type': 'OptionField',
                          'required': False,
                          'items': ('YES', 'NO'),
                          'default': None
                          }
    }

that you can consume to generate a form.

Installation
------------

.. code-block:: bash

    pip install mdform

Usage
-----

.. code-block:: python

    >>> from mdform import FormExtension, Markdown # Markdown is just re-exported from python-markdown
    >>> md = Markdown(extensions = [FormExtension()])
    >>> html = md.convert(text)           # this is the jinja template
    >>> form_dict = md.mdform_definition  # this is the definition dict

The html output will be a jinja2_ template and a dictionary describing
the form (**mdform_definition**)


Syntax
------

The syntax is strongly based on this wmd_ fork.

All fields are parsed into a dictionary (**mdform_definition**). The keys are
the form labels and the value is another dictionary with the following
elements:

- type: str
  (e.g. StringField, TextAreaField, etc)


Text fields (StringField)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    name = ___

or:

.. code-block:: text

    name = ___[50]

Exactly 3 underscores will be matched. Any more will be handled as standard underline directives.

Customizing:

.. code-block:: text

    name = ___[length]

Specific dict values:

- length : int or None (default)


Integer fields (IntegerField)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    value = ###

or:

.. code-block:: text

    value = ###[0:2:1]

Exactly 3 numeral will be matched. Any more will be handled as standard directives.

Customizing:

.. code-block:: text

    value = ###[range]

The `range` is parsed like a numpy range.

Specific dict values:

- min : int or None (default)
- max : int or None (default)
- step : int or None (default)


Float fields (FloatField)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    value = #.#

or:

.. code-block:: text

    value = #.#[0:2:0.5]

Exactly 3 numeral will be matched. Any more will be handled as standard directives.

Customizing:

.. code-block:: text

    value = #.#[range]

The `range` is parsed like a numpy range.

Specific dict values:

- min : float or None (default)
- max : float or None (default)
- step : float or None (default)


Text area (TextAreaField)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    name = AAA

or:

.. code-block:: text

    name = AAA[50]

Exactly 3 slashes will be matched.

Customizing:

.. code-block:: text

    name = ___[length]

Specific dict values:

- length : int or None (default)


Radio buttons (RadioField)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    sex = (x) male () female

Optionally, an `x` can be used to indicate the default value.

Specific dict values:

- values : tuple of str
- default : str


Check boxes (CheckboxField)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    phones = [] Android [x] iPhone [x] Blackberry

Optionally, an `x` can be used to indicate the default values.

Specific dict values:

- values : tuple of strings
- default : tuple of str


Drop down (SelectField)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    city = {BOS, SFO, (NYC)}

Or with user-friendly labels:

.. code-block:: text

    city = {BOS -> Boston, SFO -> San Francisco, (NYC -> New York City)}

.. code-block:: text

    city = {BOS, SFO, (NYC -> New York City)}

The option in parenthesis will be the default.

Specific dict values:

- choices : tuple of (str, str) (key, value)
- default : str
- collapse_on: str or None
  Item used to collapse. Format "~value" or "value"


File Field (FileField)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    name = ...

or:

.. code-block:: text

    name = ...[png]


.. code-block:: text

    name = ...[png,jpg]


.. code-block:: text

    name = ...[png,jpg;Only image files]


Specific dict values:

- allowed : tuple of str
- description : str


Date Field (DateField)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    name = d/m/y


Time Field (TimeField)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    name = hh:mm



Required fields
~~~~~~~~~~~~~~~

To flag a field as required, just add an asterisk after the name.

.. code-block:: text

    zip code* = ___


Specific dict values:

- required: bool


Sections
~~~~~~~~

In certain cases is useful to create a named section.

.. code-block:: text

    [section:university]

    name = ___

    [section:school]

    name = ___

will render as:

    {{ form.university_name }}
    {{ form.school_name }}

and:

.. code-block:: python

    {'university_name': {'type': 'StringField',
                         'required': True,
                         'length': None
                         },
     'school_name': {'type': 'StringField',
                     'required': True,
                     'length': None
                     }
    }

Sections are labeled from top to bottom, no remove a section name just do it this way.

.. code-block:: text

    [section:university]

    name = ___

    [section]

    name = ___

will render as:

.. code-block:: text

    {{ form.university_name }}
    {{ form.name }}


Collapsable parts
~~~~~~~~~~~~~~~~~

In certain cases is useful to create a part of the form which collapses based
on the value of a dropdown box. Just use the modifier `[c]` for the dropdown item
that will collapse the part of the html and enclose the collapsable part as
shown:

.. code-block:: text

    extra = {Yes, (No[c])}

    [collapse:extra]

    name = ___

    [endcollapse]

The `extra` in the `collapse` tag indicates which dropdown box is used as control.


See AUTHORS_ for a list of the maintainers.

To review an ordered list of notable changes for each version of a project,
see CHANGES_


.. _`python-markdown`: https://python-markdown.github.io/
.. _`wmd`: https://github.com/brikis98/wmd
.. _`AUTHORS`: https://github.com/hgrecco/mdform/blob/master/AUTHORS
.. _`CHANGES`: https://github.com/hgrecco/mdform/blob/master/CHANGES
.. _jinja2: https://jinja.palletsprojects.com/
