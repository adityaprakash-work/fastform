"""API endpoints."""

import json
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from guidance.models import Model
from sqlmodel import Session

from .models import Annotation, Message, User
from .schemas import (
    AnnotationCreate,
    AnnotationResponse,
    AnnotationUpdate,
    FastfillMessageCreate,
    FastfillMessageResponse,
    FastformBuildMessageCreate,
    FastformBuildMessageResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from .services import (
    AnnotationService,
    FastfillMessageService,
    FastformBuildMessageService,
    UserService,
)


def get_session(request: Request) -> Generator[Session, None, None]:
    """Dependency that yields a database session from the application's engine."""
    db_engine = request.app.state.db_engine
    with Session(db_engine) as session:
        yield session


def get_models(request: Request) -> dict[str, Model]:
    """Dependency to retrieve the language model from the request state."""
    return request.app.state.models


def user_service_dependency(session: Session = Depends(get_session)) -> UserService:
    """Dependency function to inject UserService."""
    return UserService(session)


def fastformbuild_service_dependency(
    session: Session = Depends(get_session),
) -> FastformBuildMessageService:
    return FastformBuildMessageService(session)


def fastfill_service_dependency(
    session: Session = Depends(get_session),
) -> FastformBuildMessageService:
    """Dependency function to inject FastformBuildMessageService."""
    return FastfillMessageService(session)


def annotation_service_dependency(
    session: Session = Depends(get_session),
) -> AnnotationService:
    """Dependency function to inject AnnotationService."""
    return AnnotationService(session)


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/{user_id}", response_model=UserResponse, summary="Retrieve a user")
def read_user(
    user_id: str,
    user_service: UserService = Depends(user_service_dependency),
) -> User:
    """Retrieve a user by their ID."""
    return user_service.get_user_by_id(user_id)


@user_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(user_service_dependency),
) -> User:
    """Create a new user."""
    return user_service.create_user(user_data)


@user_router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update an existing user",
)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(user_service_dependency),
) -> User:
    """Update an existing user."""
    return user_service.update_user(user_id, user_data)


@user_router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user"
)
def delete_user(
    user_id: str,
    user_service: UserService = Depends(user_service_dependency),
):
    """Delete a user by their ID."""
    user_service.delete_user(user_id)


annotation_router = APIRouter(prefix="/annotation", tags=["Annotation"])


@annotation_router.get(
    "/{annotation_id}",
    response_model=AnnotationResponse,
    summary="Retrieve an annotation",
)
def read_annotation(
    annotation_id: int,
    annotation_service: AnnotationService = Depends(annotation_service_dependency),
) -> Annotation:
    """Retrieve an annotation by its ID."""
    return annotation_service.get_annotation_by_id(annotation_id)


@annotation_router.get(
    "",
    response_model=list[AnnotationResponse],
    summary="List annotations by user",
)
def list_annotations_by_user(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    annotation_service: AnnotationService = Depends(annotation_service_dependency),
) -> list[Annotation]:
    """List all annotations created by a specific user."""
    return annotation_service.list_annotations_by_user(user_id, skip, limit)


@annotation_router.post(
    "",
    response_model=AnnotationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new annotation",
)
def create_annotation(
    annotation_data: AnnotationCreate,
    annotation_service: AnnotationService = Depends(annotation_service_dependency),
) -> Annotation:
    """Create a new annotation."""
    return annotation_service.create_annotation(annotation_data)


@annotation_router.put(
    "/{annotation_id}",
    response_model=AnnotationResponse,
    summary="Update an existing annotation",
)
def update_annotation(
    annotation_id: int,
    annotation_data: AnnotationUpdate,
    annotation_service: AnnotationService = Depends(annotation_service_dependency),
) -> Annotation:
    """Update an existing annotation."""
    return annotation_service.update_annotation(annotation_id, annotation_data)


@annotation_router.delete(
    "/{annotation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an annotation",
)
def delete_annotation(
    annotation_id: int,
    annotation_service: AnnotationService = Depends(annotation_service_dependency),
):
    """Delete an annotation by its ID."""
    annotation_service.delete_annotation(annotation_id)


fastformbuild_router = APIRouter(prefix="/fastformbuild", tags=["FastformBuild"])


@fastformbuild_router.post(
    "/chat",
    response_model=FastformBuildMessageResponse,
    summary="Send a chat message to FastformBuild and get a response",
)
def fastformbuild_chat(
    message_data: FastformBuildMessageCreate,
    form_pages: list[bytes] | None = None,
    models: dict = Depends(get_models),
    service: FastformBuildMessageService = Depends(fastformbuild_service_dependency),
) -> FastformBuildMessageResponse:
    """Send a chat message and return the response messages as a
    FastformBuildMessageResponse.
    """
    lm = models["gpt-4o-mini"]
    response_messages = service.chat(lm, message_data, form_pages)

    # Take the last message which will be used as the main response
    last_message = response_messages[-1] if response_messages else None
    if not last_message:
        raise HTTPException(status_code=500, detail="No response")

    # Extract form data if available (from first message when 2 messages are returned)
    form_data = None
    if len(response_messages) == 2:
        try:
            first_content = json.loads(response_messages[0].content)
            if "content" in first_content and len(first_content["content"]) > 0:
                form_data = first_content["content"][0].get("text")
        except Exception as e:
            print(f"Error parsing form data: {e}")

    return FastformBuildMessageResponse(
        id=last_message.id,
        content=last_message.content,
        thread_id=last_message.thread_id,
        timestamp=last_message.timestamp,
        user_id=last_message.user_id,
        form_data=form_data,
    )


@fastformbuild_router.get(
    "/threads/{user_id}",
    response_model=list[str],
    summary="Get all thread IDs belonging to a user",
)
def get_threads_by_user(
    user_id: str,
    service: FastformBuildMessageService = Depends(fastformbuild_service_dependency),
) -> list[int]:
    return service.get_threads_by_user(user_id)


@fastformbuild_router.get(
    "/threads/{thread_id}/history",
    response_model=list[FastformBuildMessageResponse],
    summary="Get message history for a thread",
)
def get_thread_history(
    thread_id: str,
    service: FastformBuildMessageService = Depends(fastformbuild_service_dependency),
):
    """Get the message history for a thread by thread_id."""
    messages = service._get_thread_history(thread_id)
    return [
        FastformBuildMessageResponse(
            id=m.id,
            content=m.content,
            thread_id=m.thread_id,
            timestamp=m.timestamp,
            user_id=m.user_id,
            form_data=None,
        )
        for m in messages
    ]


fastfill_router = APIRouter(prefix="/fastfill", tags=["FastFill"])


@fastfill_router.post(
    "/chat",
    response_model=FastfillMessageResponse,
    summary="Send a chat message to FastFill and get a response",
)
def fastfill_chat(
    message_data: FastfillMessageCreate,
    models: dict = Depends(get_models),
    service: FastfillMessageService = Depends(fastfill_service_dependency),
) -> FastfillMessageResponse:
    """Send a chat message and return the response messages as a
    FastFillMessageResponse.
    """
    lm = models["gpt-4o-mini"]
    response_messages = service.chat(lm, message_data)

    # Take the last message which will be used as the main response
    last_message = response_messages[-1] if response_messages else None
    if not last_message:
        raise HTTPException(status_code=500, detail="No response")

    # Extract form data if available (from first message when 2 messages are returned)
    form_data = None
    if len(response_messages) == 2:
        try:
            first_content = json.loads(response_messages[0].content)
            if "content" in first_content and len(first_content["content"]) > 0:
                form_data = first_content["content"][0].get("text")
        except Exception as e:
            print(f"Error parsing form data: {e}")

    return FastfillMessageResponse(
        id=last_message.id,
        content=last_message.content,
        thread_id=last_message.thread_id,
        timestamp=last_message.timestamp,
        user_id=last_message.user_id,
        form_data=form_data,
    )


@fastfill_router.get(
    "/threads/{user_id}",
    response_model=list[str],
    summary="Get all thread IDs belonging to a user",
)
def get_fastfill_threads_by_user(
    user_id: str,
    service: FastfillMessageService = Depends(fastfill_service_dependency),
) -> list[int]:
    """Get all thread IDs belonging to a user."""
    return service.get_threads_by_user(user_id)


@fastfill_router.get(
    "/threads/{thread_id}/history",
    response_model=list[FastfillMessageResponse],
    summary="Get message history for a FastFill thread",
)
def get_fastfill_thread_history(
    thread_id: str,
    service: FastfillMessageService = Depends(fastfill_service_dependency),
):
    """Get the message history for a FastFill thread by thread_id."""
    messages = service._get_thread_history(thread_id)
    return [
        FastfillMessageResponse(
            id=m.id,
            content=m.content,
            thread_id=m.thread_id,
            timestamp=m.timestamp,
            user_id=m.user_id,
            form_data=None,
        )
        for m in messages
    ]


v1_router = APIRouter(prefix="/v1")


@v1_router.get("/", summary="API root endpoint")
def api_root() -> dict:
    """Root endpoint for the API."""
    return {"message": "FastForm API", "version": "v1"}


v1_router.include_router(user_router)
v1_router.include_router(annotation_router)
v1_router.include_router(fastformbuild_router)
v1_router.include_router(fastfill_router)
