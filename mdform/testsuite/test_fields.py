import pytest

from mdform.fields import (
    CheckboxField,
    DateField,
    DecimalField,
    EmailField,
    Field,
    FileField,
    FloatField,
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    TimeField,
)


def test_label():
    assert Field.match("name = @") == ("name", False, EmailField())
    assert Field.match("name* = @") == ("name", True, EmailField())
    assert Field.match("name * = @") == ("name", True, EmailField())
    assert Field.match("name* = AAA") == ("name", True, TextAreaField(length=None))

    # No matched field
    assert Field.match("name = XYZ") is None


def test_string_field():
    assert StringField.match("_") is None
    assert StringField.match("__") is None
    assert StringField.match("____") is None
    assert StringField.match("___") == dict(length=None)
    assert StringField.match("___[30]") == dict(length=30)
    assert StringField.match(" ___[30]") == dict(length=30)
    assert StringField.match("___[30] ") == dict(length=30)
    assert StringField.match(" ___[30] ") == dict(length=30)
    assert StringField.match("___[]") == dict(length=None)

    f = Field.from_str("name = ___[]")
    assert isinstance(f.specific_field, StringField)
    assert f.specific_field.length is None
    f = Field.from_str("name = ___[30]")
    assert isinstance(f.specific_field, StringField)
    assert f.specific_field.length == 30


def test_integer_field():
    assert IntegerField.match("") is None
    assert IntegerField.match("###[]") is None
    assert IntegerField.match("###[0:2:1:0]") is None
    assert IntegerField.match("###[0:s:1]") is None
    assert IntegerField.match("###[0:0.4:1]") is None

    assert IntegerField.match("###") == dict(min=None, max=None, step=None)
    assert IntegerField.match("###[2]") == dict(min=None, max=2, step=None)
    assert IntegerField.match("###[0:2]") == dict(min=0, max=2, step=None)
    assert IntegerField.match("###[0:2:1]") == dict(min=0, max=2, step=1)
    assert IntegerField.match("###[0::1]") == dict(min=0, max=None, step=1)

    f = Field.from_str("name = ###")
    assert isinstance(f.specific_field, IntegerField)
    assert f.specific_field.min is None
    assert f.specific_field.max is None
    assert f.specific_field.step is None

    f = Field.from_str("name = ###[0:2:1]")
    assert isinstance(f.specific_field, IntegerField)
    assert f.specific_field.min == 0
    assert f.specific_field.max == 2
    assert f.specific_field.step == 1


def test_decimal_field():
    assert DecimalField.match("") is None
    assert DecimalField.match("#.#[]") is None
    assert DecimalField.match("#.#[0:s:1]") is None
    assert DecimalField.match("#.#[0:0:1:0:0]") is None

    assert DecimalField.match("#.#") == dict(min=None, max=None, step=None, places=2)
    assert DecimalField.match("#.#[2]") == dict(min=None, max=2.0, step=None, places=2)
    assert DecimalField.match("#.#[0:2]") == dict(min=0.0, max=2.0, step=None, places=2)
    assert DecimalField.match("#.#[0:2:1]") == dict(
        min=0.0, max=2.0, step=1.0, places=2
    )
    assert DecimalField.match("#.#[0:2:0.5]") == dict(
        min=0.0, max=2.0, step=0.5, places=2
    )
    assert DecimalField.match("#.#[0::0.5]") == dict(
        min=0.0, max=None, step=0.5, places=2
    )
    assert DecimalField.match("#.#[0::0.5:3]") == dict(
        min=0.0, max=None, step=0.5, places=3
    )

    f = Field.from_str("name = #.#")
    assert isinstance(f.specific_field, DecimalField)
    assert f.specific_field.min is None
    assert f.specific_field.max is None
    assert f.specific_field.step is None

    f = Field.from_str("name = #.#[0:2:1:3]")
    assert isinstance(f.specific_field, DecimalField)
    assert f.specific_field.min == 0
    assert f.specific_field.max == 2
    assert f.specific_field.step == 1
    assert f.specific_field.places == 3


def test_float_field():
    assert FloatField.match("") is None
    assert FloatField.match("#.#f[]") is None
    assert FloatField.match("#.#f[0:2:1:0]") is None
    assert FloatField.match("#.#f[0:s:1]") is None

    assert FloatField.match("#.#f") == dict(min=None, max=None, step=None)
    assert FloatField.match("#.#f[2]") == dict(min=None, max=2.0, step=None)
    assert FloatField.match("#.#f[0:2]") == dict(min=0.0, max=2.0, step=None)
    assert FloatField.match("#.#f[0:2:1]") == dict(min=0.0, max=2.0, step=1.0)
    assert FloatField.match("#.#f[0:2:0.5]") == dict(min=0.0, max=2.0, step=0.5)
    assert FloatField.match("#.#f[0::0.5]") == dict(min=0.0, max=None, step=0.5)

    f = Field.from_str("name = #.#f")
    assert isinstance(f.specific_field, FloatField)
    assert f.specific_field.min is None
    assert f.specific_field.max is None
    assert f.specific_field.step is None

    f = Field.from_str("name = #.#f[0:2:1]")
    assert isinstance(f.specific_field, FloatField)
    assert f.specific_field.min == 0
    assert f.specific_field.max == 2
    assert f.specific_field.step == 1


def test_area_field():
    assert TextAreaField.match("A") is None
    assert TextAreaField.match("AA") is None
    assert TextAreaField.match("AAAA") is None
    assert TextAreaField.match("AAA") == dict(length=None)
    assert TextAreaField.match("AAA[30]") == dict(length=30)
    assert TextAreaField.match(" AAA[30]") == dict(length=30)
    assert TextAreaField.match("AAA[30] ") == dict(length=30)
    assert TextAreaField.match(" AAA[30] ") == dict(length=30)
    assert TextAreaField.match("AAA[]") == dict(length=None)

    f = Field.from_str("name = AAA[]")
    assert isinstance(f.specific_field, TextAreaField)
    assert f.specific_field.length is None
    f = Field.from_str("name = AAA[30]")
    assert isinstance(f.specific_field, TextAreaField)
    assert f.specific_field.length == 30


def test_date_field():
    assert DateField.match("") is None
    assert DateField.match("d/m/y") == dict()
    assert DateField.match(" d/m/y") == dict()
    assert DateField.match(" d/m/y ") == dict()

    f = Field.from_str("name = d/m/y")
    assert isinstance(f.specific_field, DateField)


def test_time_field():
    assert TimeField.match("") is None
    assert TimeField.match("hh:mm") == dict()
    assert TimeField.match(" hh:mm") == dict()
    assert TimeField.match(" hh:mm ") == dict()

    f = Field.from_str("name = hh:mm")
    assert isinstance(f.specific_field, TimeField)


def test_email_field():
    assert EmailField.match("") is None
    assert EmailField.match("@") == dict()
    assert EmailField.match(" @") == dict()
    assert EmailField.match(" @ ") == dict()

    f = Field.from_str("name = @")
    assert isinstance(f.specific_field, EmailField)


def test_checkbox_field():
    assert CheckboxField.match("") is None
    assert CheckboxField.match("[] A [] B []") == dict(
        choices=("A", "B", ""), default=tuple()
    )
    assert CheckboxField.match("[] A [x] B [] C") == dict(
        choices=("A", "B", "C"), default=("B",)
    )
    assert CheckboxField.match("[] A [x] B [x] C") == dict(
        choices=("A", "B", "C"), default=("B", "C")
    )
    assert CheckboxField.match("[] A [] B [] C") == dict(
        choices=("A", "B", "C"), default=tuple()
    )

    assert CheckboxField.match("[] Apple [] Banana [] Coconut") == dict(
        choices=("Apple", "Banana", "Coconut"), default=tuple()
    )

    f = Field.from_str("name = [] A [] B [] C")
    assert isinstance(f.specific_field, CheckboxField)
    assert f.specific_field.choices == ("A", "B", "C")
    assert f.specific_field.default == tuple()

    f = Field.from_str("name = [] A [x] B [] C")
    assert isinstance(f.specific_field, CheckboxField)
    assert f.specific_field.choices == ("A", "B", "C")
    assert f.specific_field.default == ("B",)


def test_radio_field():
    assert RadioField.match("") is None
    assert RadioField.match("() A () B ()") == dict(
        choices=("A", "B", ""), default=None
    )
    assert RadioField.match("() A (x) B () C") == dict(
        choices=("A", "B", "C"), default="B"
    )
    assert RadioField.match("() A () B () C") == dict(
        choices=("A", "B", "C"), default=None
    )

    assert RadioField.match("() Apple () Banana () Coconut") == dict(
        choices=("Apple", "Banana", "Coconut"), default=None
    )

    f = Field.from_str("name = () A () B () C")
    assert isinstance(f.specific_field, RadioField)
    assert f.specific_field.choices == ("A", "B", "C")
    assert f.specific_field.default is None

    f = Field.from_str("name = () A (x) B () C")
    assert isinstance(f.specific_field, RadioField)
    assert f.specific_field.choices == ("A", "B", "C")
    assert f.specific_field.default == "B"


def test_select_field():
    assert SelectField.match("{ A, B, C") is None
    assert SelectField.match("{ A, B, C}") == dict(
        choices=(("A", "A"), ("B", "B"), ("C", "C")), default=None, collapse_on=None
    )
    assert SelectField.match("{ A, B, (C)}") == dict(
        choices=(("A", "A"), ("B", "B"), ("C", "C")), default="C", collapse_on=None
    )
    assert SelectField.match("{ A->J, B, (C->P)}") == dict(
        choices=(("A", "J"), ("B", "B"), ("C", "P")), default="C", collapse_on=None
    )

    assert SelectField.match("{ A, B[c], C}") == dict(
        choices=(("A", "A"), ("B", "B"), ("C", "C")), default=None, collapse_on="B"
    )
    assert SelectField.match("{ A, B, (C[c])}") == dict(
        choices=(("A", "A"), ("B", "B"), ("C", "C")), default="C", collapse_on="C"
    )
    assert SelectField.match("{ A[c]->J, B, (C->P)}") == dict(
        choices=(("A", "J"), ("B", "B"), ("C", "P")), default="C", collapse_on="A"
    )

    assert SelectField.match("{ A, B[o], C}") == dict(
        choices=(("A", "A"), ("B", "B"), ("C", "C")), default=None, collapse_on="~B"
    )

    assert SelectField.match("{ Apple, Banana, Coconut}") == dict(
        choices=(("Apple", "Apple"), ("Banana", "Banana"), ("Coconut", "Coconut")),
        default=None,
        collapse_on=None,
    )

    assert SelectField.match("{ Apple->Jelly, Banana, Coconut->Pear}") == dict(
        choices=(("Apple", "Jelly"), ("Banana", "Banana"), ("Coconut", "Pear")),
        default=None,
        collapse_on=None,
    )

    with pytest.raises(ValueError):
        assert SelectField.match("{ A, B[o], C[o]}")

    with pytest.raises(ValueError):
        assert SelectField.match("{ A, B[c], C[c]}")

    f = Field.from_str("name = { A, B[c], C}")
    assert isinstance(f.specific_field, SelectField)
    assert f.specific_field.choices == (("A", "A"), ("B", "B"), ("C", "C"))
    assert f.specific_field.default is None
    assert f.specific_field.collapse_on == "B"


def test_filefield():
    assert FileField.match("") is None
    assert FileField.match("...") == dict(allowed=None, description=None)
    assert FileField.match("...[png]") == dict(allowed=("png",), description=None)
    assert FileField.match("...[png,jpg]") == dict(
        allowed=("png", "jpg"), description=None
    )
    assert FileField.match("...[png;image files only]") == dict(
        allowed=("png",), description="image files only"
    )
    assert FileField.match("...[png,jpg;image files only]") == dict(
        allowed=("png", "jpg"), description="image files only"
    )

    f = Field.from_str("name = ...[png,jpg;image files only]")
    assert isinstance(f.specific_field, FileField)
    assert f.specific_field.allowed == ("png", "jpg")
    assert f.specific_field.description == "image files only"
