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

An extension for `python-markdown`_ to generate parse a form in Markdown
based document.

This document:

.. code-block::

    Please fill this form:

    name* = ___
    email = @

    And also this important question:

    Do you like this = () YES () NO

will generate the following jinja template:

.. code-block::

    Please fill this form:

    {{ form.name }}
    {{ form.email }}

    And also this important question:

    {{ form.do_you_like_this }}


and this dict:

.. code-block::python

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

.. code-block::

    pip install mdform

Usage
-----

.. code-block::python

    >>> import markdown
    >>> md = markdown.Markdown(extensions = ['form'])
    >>> html = md.convert(text)  # this is the jinja template
    >>> form_dict = md.Form      # this is the definition dict



Syntax
------

The syntax is strongly based on this wmd_ fork.

Text fields
~~~~~~~~~~~

.. code-block::

    name = ___

or:

.. code-block::

    name = ___[50]

Exactly 3 underscores will be matched. Any more will be handled as standard underline directives.


Text area
~~~~~~~~~

.. code-block::

    name = |||

or:

.. code-block::

    name = |||[50]

Exactly 3 slashes will be matched.


Radio buttons
~~~~~~~~~~~~~

.. code-block::

    sex = (x) male () female

The option with an `x` will be the default.


Check boxes
~~~~~~~~~~~

.. code-block::

    phones = [] Android [x] iPhone [x] Blackberry

The option with an `x` will be the default.


Drop down
~~~~~~~~~

.. code-block::

    city = {BOS, SFO, (NYC)}

Or with user-friendly labels:

.. code-block::

    city = {BOS -> Boston, SFO -> San Francisco, (NYC -> New York City)}

.. code-block::

    city = {BOS, SFO, (NYC -> New York City)}

The option in parenthesis will be the default.


File Field
~~~~~~~~~~

.. code-block::

    name = ...

or:

.. code-block::

    name = ...[png]


.. code-block::

    name = ...[png,jpg]


.. code-block::

    name = ...[png,jpg;Only image files]


Required fields
~~~~~~~~~~~~~~~

To flag a field as required, just add an asterisk after the name.

.. code-block::

    zip code* = ___


Sections
~~~~~~~~

In certain cases is useful to create a named section.

.. code-block::

    [section:university]

    name = ___

    [section:school]

    name = ___

will render as:

    {{ form.university_name }}
    {{ form.school_name }}

and:

.. code-block::

    {'university_name': {'type': 'StringField',
                         'required': True,
                         'length': None
                         },
     'school_name': {'type': 'StringField',
                     'required': True,
                     'length': None
                     }
    }


Collapsable parts
~~~~~~~~~~~~~~~~~

In certain cases is useful to create a part of the form which collapses based
on the value of a dropdown box. Just use the modifier `[c]` for the dropdown item
that will collapse the part of the html and enclose the collapsable part as
shown:

.. code-block::

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