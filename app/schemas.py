"""API schemas for request/response models."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a user (excludes server-generated fields)."""

    id: str = Field(description="Unique identifier for the user.")
    email: str = Field(description="Email address of the user.")


class UserResponse(BaseModel):
    """Schema for user responses (includes all fields)."""

    id: str = Field(description="Unique identifier for the user.")
    email: str = Field(description="Email address of the user.")
    created_at: datetime = Field(description="Timestamp when the user was created.")


class UserUpdate(BaseModel):
    """Schema for updating a user (excludes server-generated fields and ID)."""

    email: str = Field(description="Email address of the user.")


class AnnotationCreate(BaseModel):
    """Schema for creating an annotation (excludes server-generated fields)."""

    name: str = Field(description="Name of the annotation.")
    description: str | None = Field(
        default=None, description="Description of the annotation."
    )
    structure: str = Field(
        description="JSON structure of the annotation, defining its fields and layout."
    )
    user_id: str = Field(description="ID of the user who created the annotation.")


class AnnotationResponse(BaseModel):
    """Schema for annotation responses (includes all fields)."""

    id: int = Field(description="Unique identifier for the annotation.")
    name: str = Field(description="Name of the annotation.")
    description: str | None = Field(
        default=None, description="Description of the annotation."
    )
    structure: str = Field(
        description="JSON structure of the annotation, defining its fields and layout."
    )
    created_at: datetime = Field(
        description="Timestamp when the annotation was created."
    )
    user_id: str = Field(description="ID of the user who created the annotation.")


class AnnotationUpdate(BaseModel):
    """Schema for updating an annotation."""

    id: int = Field(description="Unique identifier for the annotation.")
    name: str = Field(description="Name of the annotation.")
    description: str | None = Field(
        default=None, description="Description of the annotation."
    )
    structure: str = Field(
        description="JSON structure of the annotation, defining its fields and layout."
    )


class MessageCreateBase(BaseModel):
    """Base schema for creating a chat message."""

    content: str = Field(description="Content of the chat message.")
    thread_id: str = Field(description="ID of the thread this message belongs to.")
    user_id: str = Field(description="ID of the user who sent the message.")


class MessageResponseBase(BaseModel):
    """Base schema for chat message responses."""

    id: int = Field(description="Unique identifier for the chat message.")

    content: str = Field(description="Content of the chat message.")
    thread_id: str = Field(description="ID of the thread this message belongs to.")
    timestamp: datetime = Field(description="Timestamp when the message was created.")
    user_id: str = Field(description="ID of the user who sent the message.")


class FastfillMessageCreate(MessageCreateBase):
    """Schema for creating a FastFill chat message."""

    load_annotation_id: int | None = Field(
        default=None,
        description=("ID of the annotation to load with this message, if applicable."),
    )


class FastfillMessageResponse(MessageResponseBase):
    """Schema for FastFill chat message responses."""

    form_data: str | None = Field(
        default=None,
        description=(
            "JSON string representing the form data associated with this message, "
            "if applicable. It should be completely filled out with the user's input."
        ),
    )


class FastformBuildMessageCreate(MessageCreateBase):
    """Schema for creating a FastformBuild chat message."""

    pass


class FastformBuildMessageResponse(MessageResponseBase):
    """Schema for FastformBuild chat message responses."""

    form_data: str | None = Field(
        default=None,
        description=(
            "JSON string representing the form data associated with this message."
        ),
    )
