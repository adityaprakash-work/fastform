"""Fastform Schema Definitions."""

from enum import Enum
from typing import Generic, TypeVar

from pydantic import (
    BaseModel as PydanticBaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

FORBID_EXTRA = {"extra": "forbid"}
SET_TO_NULLV = "This field is to be set to null. The frontend will fill it in later."

t = TypeVar("t", bound="Annotation")


class BaseModel(PydanticBaseModel):
    """Base class that forbids undeclared attributes by default.

    All schema models inherit from this to ensure only declared fields are allowed.
    Example:
        class MyModel(BaseModel):
            x: int
            y: str
    """

    model_config = ConfigDict(**FORBID_EXTRA)


class Coordinate(BaseModel):
    """Represents an (x, y) point on the form (e.g. bounding box corner).

    Both x and y are to be set to null while constructing the form schema. The frontend
    will fill in the actual coordinates when rendering the form.

    Example:
        Coordinate(x=None, y=None)
    """

    x: int | None = Field(..., description="X coordinate" + SET_TO_NULLV)
    y: int | None = Field(..., description="Y coordinate" + SET_TO_NULLV)


class AnnotationEnum(Enum):
    """Enumeration for annotation types.

    This is used to identify the type of annotation in the form schema.
    Example:
        AnnotationEnum.text_field
    """

    text_field = "TextField"
    text_area_field = "TextAreaField"
    number_field = "NumberField"
    date_field = "DateField"
    checkbox_field = "CheckboxField"
    radio_field = "RadioField"
    select_field = "SelectField"
    file_field = "FileField"
    image_field = "ImageField"
    signature_field = "SignatureField"
    email_field = "EmailField"
    url_field = "UrlField"
    phone_field = "PhoneField"
    list_field = "ListField"


class Annotation(BaseModel):
    """Base class for all field annotations on a scanned form.

    Holds common metadata:
    - title: label of the field
    - description: helper text for frontend
    - bbox: list of two Coordinates [upper-left, lower-right]
    - element_name: type of annotation (from AnnotationEnum)

    Example:
        Annotation(
            title="Full Name",
            description="Enter your full legal name",
            bbox=[Coordinate(x=None, y=None), Coordinate(x=None, y=None)]
        )
    """

    title: str = Field(..., description="Annotation title")
    description: str = Field(..., description="Annotation description")
    bbox: list[Coordinate] = Field(
        ..., description="[UL, LR] bounding-box coordinates", min_length=2, max_length=2
    )
    element_name: AnnotationEnum


# ℹ️ Primitive field types
class TextField(Annotation):
    """Single-line text input field.

    Inherits title, description, bbox. Agent sets `value` to null; frontend fills in.
    """

    value: str | None = Field(..., description="Text value" + SET_TO_NULLV)


class TextAreaField(Annotation):
    """Multi-line text input field.

    Supports a maximum character length. Useful for comments or long-form input.
    """

    value: str | None = Field(..., description="Multiline text value" + SET_TO_NULLV)
    max_length: int | None = Field(..., description="Optional maximum characters")


class NumberField(Annotation):
    """Numeric input (integer or float).

    Optionally constrain with min_value and max_value.
    """

    value: int | float | None = Field(..., description="Numeric value" + SET_TO_NULLV)
    min_value: int | float | None = Field(..., description="Minimum value")
    max_value: int | float | None = Field(..., description="Maximum value")


class DateField(Annotation):
    """Date picker field (ISO 8601 format YYYY-MM-DD)."""

    value: str | None = Field(..., description="ISO 8601 date" + SET_TO_NULLV)


class CheckboxField(Annotation):
    """Boolean checkbox field."""

    value: bool | None = Field(..., description="Checked or not" + SET_TO_NULLV)


class RadioField(Annotation):
    """Single-choice option group (radio buttons)."""

    options: list[str] = Field(..., description="Option labels")
    value: str | None = Field(..., description="Selected option" + SET_TO_NULLV)


class SelectOption(BaseModel):
    """Option entry for dropdowns and multi-selects."""

    label: str = Field(..., description="Display label")
    value: str | int | float = Field(..., description="Stored option value")


class SelectField(Annotation):
    """Dropdown field supporting single or multiple selections."""

    options: list[SelectOption] = Field(..., description="Available options")
    multi: bool = Field(..., description="Allow multiple selections?")
    value: list[SelectOption] | SelectOption | None = Field(
        ..., description="Chosen option(s)" + SET_TO_NULLV
    )

    @model_validator(mode="after")
    def check_select(cls, values: dict[str, object]) -> dict[str, object]:
        multi = values.get("multi")
        val = values.get("value")
        if multi and val is not None and not isinstance(val, list):
            raise ValueError("When multi=True, value must be a list")
        if not multi and isinstance(val, list):
            raise ValueError("When multi=False, value must be a single item")
        return values


class FileField(Annotation):
    """Generic file upload field."""

    allowed: list[str] = Field(..., description="Allowed MIME types")
    max_mb: int | None = Field(..., description="Max file size in MB")
    value: str | None = Field(..., description="File ID or URI" + SET_TO_NULLV)


class ImageField(FileField):
    """Specialized FileField for images (JPEG, PNG, WEBP)."""

    allowed: list[str] = Field(
        ...,
        description="Image references." + SET_TO_NULLV,
    )


class SignatureField(Annotation):
    """Field for capturing hand-drawn signatures as Data URIs."""

    value: str | None = Field(..., description="Signature as dataURI" + SET_TO_NULLV)


class EmailField(Annotation):
    """Email input (string, validated on frontend)."""

    value: str | None = Field(..., description="Email address" + SET_TO_NULLV)


class UrlField(Annotation):
    """URL input (string, validated on frontend)."""

    value: str | None = Field(..., description="URL" + SET_TO_NULLV)


class PhoneField(Annotation):
    """International phone number input (E.164 format)."""

    value: str | None = Field(..., description="Phone number" + SET_TO_NULLV)


class ListField(Annotation, Generic[t]):
    """Collection of repeating annotations (e.g., multiple addresses)."""

    items: list[t] | None = Field(..., description="Items list" + SET_TO_NULLV)


class AnnotationGroupEnum(Enum):
    """Enumeration for annotation group types.

    This is used to identify the type of annotation group in the form schema.
    Example:
        AnnotationGroupEnum.section_group
    """

    section_group = "SectionGroup"
    repeat_group = "RepeatGroup"
    wizard_step = "WizardStep"
    table_group = "TableGroup"


class AnnotationGroup(BaseModel):
    """Generic container grouping multiple annotations.

    Holds:
    - title: label of the group
    - description: helper text for frontend
    - annotations: list of contained annotations
    - element_name: type of annotation group (from AnnotationGroupEnum)
    """

    title: str
    description: str
    annotations: list[Annotation] = Field(
        ..., min_length=1, description="Contained annotations"
    )
    element_name: AnnotationGroupEnum


class SectionGroup(AnnotationGroup):
    """Logical section of the form that may collapse."""

    collapsible: bool
    collapsed: bool


class RepeatGroup(AnnotationGroup):
    """Repeatable block (e.g., multiple contact methods)."""

    min_val: int = Field(..., description="Min repeats")
    max_val: int | None = Field(..., description="Max repeats")


class WizardStep(AnnotationGroup):
    """Step in a multi-page/wizard form."""

    order: int | None = Field(..., description="Step index")
    optional: bool


class TableGroup(AnnotationGroup):
    """Tabular layout (rows x columns)."""

    columns: list[str]
    rows: list[
        list[
            TextField
            | TextAreaField
            | NumberField
            | DateField
            | CheckboxField
            | RadioField
            | SelectField
            | FileField
            | ImageField
            | SignatureField
            | EmailField
            | UrlField
            | PhoneField
            | ListField[t]
            | SectionGroup
            | RepeatGroup
            | WizardStep
        ]
    ]

    @field_validator("rows", mode="after")
    def match_columns(cls, rows, info):
        columns = info.data.get("columns", [])
        for row in rows or []:
            if len(row) != len(columns):
                raise ValueError("Row length must equal number of columns")
        return rows


class Form(BaseModel):
    """Root schema representing an entire form layout for scanned documents."""

    title: str
    description: str
    elements: list[
        TextField
        | TextAreaField
        | NumberField
        | DateField
        | CheckboxField
        | RadioField
        | SelectField
        | FileField
        | ImageField
        | SignatureField
        | EmailField
        | UrlField
        | PhoneField
        | ListField[t]
        | SectionGroup
        | RepeatGroup
        | WizardStep
        | TableGroup
    ]


__all__ = [
    "Coordinate",
    "Annotation",
    "TextField",
    "TextAreaField",
    "NumberField",
    "DateField",
    "CheckboxField",
    "RadioField",
    "SelectOption",
    "SelectField",
    "FileField",
    "ImageField",
    "SignatureField",
    "EmailField",
    "UrlField",
    "PhoneField",
    "ListField",
    "AnnotationGroup",
    "SectionGroup",
    "RepeatGroup",
    "WizardStep",
    "TableGroup",
    "Form",
]
