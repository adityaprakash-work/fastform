"""Service layer for business logic."""

import base64
import json

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from .ai import (
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_FILL,
    ContentMessage,
    Model,
    fastformbuild_chat,
    fastformfill_chat,
)
from .models import Annotation, Message, User
from .schemas import (
    AnnotationCreate,
    AnnotationUpdate,
    FastfillMessageCreate,
    FastformBuildMessageCreate,
    UserCreate,
    UserUpdate,
)


class UserService:
    """Service class for user-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: str) -> User:
        """Retrieve a user by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The user with the given ID.
        """
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found",
            )
        return user

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: The data for the new user.

        Returns:
            The newly created user.
        """
        existing_user = self.session.get(User, user_data.id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with ID '{user_data.id}' already exists",
            )

        new_user = User(
            id=user_data.id,
            email=user_data.email,
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """Update an existing user.

        Args:
            user_id: The ID of the user to update.
            user_data: The data for the updated user.

        Returns:
            The updated user.
        """
        existing_user = self.session.get(User, user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found",
            )

        existing_user.email = user_data.email
        self.session.add(existing_user)
        self.session.commit()
        self.session.refresh(existing_user)
        return existing_user

    def delete_user(self, user_id: str) -> None:
        """Delete a user by their ID.

        Args:
            user_id: The ID of the user to delete.
        """
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found",
            )
        self.session.delete(user)
        self.session.commit()


class AnnotationService:
    """Service class for annotation-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_annotation_by_id(self, annotation_id: int) -> Annotation:
        """Retrieve an annotation by its ID.

        Args:
            annotation_id: The ID of the annotation to retrieve.

        Returns:
            The annotation with the given ID.
        """
        annotation = self.session.get(Annotation, annotation_id)
        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation '{annotation_id}' not found",
            )
        return annotation

    def list_annotations_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[Annotation]:
        """List all annotations created by a specific user.

        Args:
            user_id: The ID of the user whose annotations to list.
            skip: The number of annotations to skip.
            limit: The maximum number of annotations to return.

        Returns:
            A list of annotations created by the user.
        """
        return self.session.exec(
            select(Annotation)
            .where(Annotation.user_id == user_id)
            .offset(skip)
            .limit(limit)
        ).all()

    def create_annotation(self, annotation_data: AnnotationCreate) -> Annotation:
        """Create a new annotation.

        Args:
            annotation_data: The data for the new annotation.

        Returns:
            The newly created annotation.
        """
        new_annotation = Annotation(
            name=annotation_data.name,
            description=annotation_data.description,
            structure=annotation_data.structure,
            user_id=annotation_data.user_id,
        )
        self.session.add(new_annotation)
        self.session.commit()
        self.session.refresh(new_annotation)
        return new_annotation

    def update_annotation(self, annotation_data: AnnotationUpdate) -> Annotation:
        """Update an existing annotation.

        Args:
            annotation_data: The data for the updated annotation.

        Returns:
            The updated annotation.
        """
        existing_annotation = self.session.get(Annotation, annotation_data.id)
        if not existing_annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation '{annotation_data.id}' not found",
            )

        existing_annotation.name = annotation_data.name
        existing_annotation.description = annotation_data.description
        existing_annotation.structure = annotation_data.structure
        self.session.add(existing_annotation)
        self.session.commit()
        self.session.refresh(existing_annotation)
        return existing_annotation

    def delete_annotation(self, annotation_id: int) -> None:
        """Delete an annotation by its ID.

        Args:
            annotation_id: The ID of the annotation to delete.
        """
        annotation = self.session.get(Annotation, annotation_id)
        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation '{annotation_id}' not found",
            )
        self.session.delete(annotation)
        self.session.commit()


class MessageService:
    """Service class for message-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_message_by_id(self, message_id: int) -> Message:
        """Retrieve a message by its ID.

        Args:
            message_id: The ID of the message to retrieve.

        Returns:
            The message with the given ID.
        """
        message = self.session.get(Message, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message '{message_id}' not found",
            )
        return message

    def list_messages_by_thread(
        self, thread_id: str, skip: int = 0, limit: int = 100
    ) -> list[Message]:
        """List all messages in a specific thread.

        Args:
            thread_id: The ID of the thread whose messages to list.
            skip: The number of messages to skip.
            limit: The maximum number of messages to return.

        Returns:
            A list of messages in the thread.
        """
        return self.session.exec(
            select(Message)
            .where(Message.thread_id == thread_id)
            .offset(skip)
            .limit(limit)
        ).all()

    def _is_valid_base64_image(self, b: bytes) -> bool:
        """Check if the given bytes are valid base64-encoded image data.

        Args:
            b: The bytes to check.

        Returns:
            True if the bytes are valid base64-encoded image data, False otherwise.
        """
        try:
            # Try to decode and re-encode to check validity
            base64.b64decode(b, validate=True)
            return True
        except Exception:
            return False

    def _get_thread_history(self, thread_id: str) -> list[Message]:
        """Fetch the message history for a thread. Raise 404 if not found.

        Args:
            thread_id: The ID of the thread to fetch the history for.

        Returns:
            A list of messages in the thread.
        """
        thread = self.session.exec(
            select(Message).where(Message.thread_id == thread_id)
        ).all()
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread '{thread_id}' not found",
            )
        return thread

    def get_threads_by_user(self, user_id: str) -> list[str]:
        """Get all unique thread IDs belonging to a user.

        Args:
            user_id: The ID of the user whose threads to list.

        Returns:
            A list of thread IDs belonging to the user.
        """
        thread_ids = self.session.exec(
            select(Message.thread_id).where(Message.user_id == user_id)
        ).all()
        return list({tid for tid in thread_ids if tid is not None})


class FastformBuildMessageService(MessageService):
    """Service class for FastformBuild message-related operations."""

    def chat(
        self,
        lm: Model,
        message_data: FastformBuildMessageCreate,
        form_pages: list[bytes] | None = None,
    ) -> list[Message]:
        """Create a new FastformBuild chat message.

        Args:
            lm: The language model to use.
            message_data: The data for the new message.
            form_pages: The pages of the form to use.

        Returns:
            A list of messages.
        """
        thread_id = message_data.thread_id

        try:
            thread = self._get_thread_history(thread_id)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                system_message = Message(
                    content=json.dumps(
                        {
                            "role": "system",
                            "content": [{"type": "text", "text": SYSTEM_PROMPT}],
                        }
                    ),
                    thread_id=thread_id,
                    user_id=message_data.user_id,
                )
                self.session.add(system_message)
                self.session.commit()
                thread = [system_message]
            else:
                raise

        thread.sort(key=lambda m: m.timestamp)
        messages = [ContentMessage.model_validate_json(m.content) for m in thread]

        content_items = [{"type": "text", "text": message_data.content}]
        if form_pages is not None:
            for page in form_pages:
                if self._is_valid_base64_image(page):
                    content_items.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{page.decode('utf-8')}"
                            },
                        }
                    )
                else:
                    continue

        user_message = ContentMessage.model_validate_json(
            json.dumps(
                {
                    "role": "user",
                    "content": content_items,
                }
            )
        )
        messages.append(user_message)

        # Add the user message to the session
        user_message_db = Message(
            content=user_message.model_dump_json(),
            thread_id=thread_id,
            user_id=message_data.user_id,
        )
        self.session.add(user_message_db)
        self.session.commit()

        _response = fastformbuild_chat(lm, messages)

        response = []
        created_messages = []
        for msg in _response:
            new_message = Message(
                content=msg.model_dump_json(),
                thread_id=thread_id,
                user_id=message_data.user_id,
            )
            self.session.add(new_message)
            created_messages.append(new_message)

        self.session.commit()

        for msg in created_messages:
            self.session.refresh(msg)
            response.append(msg)

        return response


class FastfillMessageService(MessageService):
    """Service class for FastFill message-related operations."""

    def __init__(self, session: Session):
        super().__init__(session)
        self.annotation_service = AnnotationService(session)

    def chat(
        self,
        lm: Model,
        message_data: FastformBuildMessageCreate,
    ) -> list[Message]:
        """Create a new FastformBuild chat message.

        Args:
            lm: The language model to use.
            message_data: The data for the new message.

        Returns:
            A list of messages.
        """
        thread_id = message_data.thread_id
        annotation = (
            self.annotation_service.get_annotation_by_id(
                message_data.load_annotation_id
            )
            if message_data.load_annotation_id
            else None
        )

        try:
            thread = self._get_thread_history(thread_id)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                system_message = Message(
                    content=json.dumps(
                        {
                            "role": "system",
                            "content": [
                                {
                                    "type": "text",
                                    "text": SYSTEM_PROMPT_FILL.format(
                                        form_structure=annotation.structure
                                        if annotation
                                        else "No structure provided"
                                    ),
                                }
                            ],
                        }
                    ),
                    thread_id=thread_id,
                    user_id=message_data.user_id,
                )
                self.session.add(system_message)
                self.session.commit()
                thread = [system_message]
            else:
                raise

        thread.sort(key=lambda m: m.timestamp)
        messages = [ContentMessage.model_validate_json(m.content) for m in thread]

        content_items = [{"type": "text", "text": message_data.content}]

        user_message = ContentMessage.model_validate_json(
            json.dumps(
                {
                    "role": "user",
                    "content": content_items,
                }
            )
        )
        messages.append(user_message)

        user_message_db = Message(
            content=user_message.model_dump_json(),
            thread_id=thread_id,
            user_id=message_data.user_id,
        )
        self.session.add(user_message_db)
        self.session.commit()

        _response = fastformfill_chat(lm, messages)

        response = []
        created_messages = []
        for msg in _response:
            new_message = Message(
                content=msg.model_dump_json(),
                thread_id=thread_id,
                user_id=message_data.user_id,
            )
            self.session.add(new_message)
            created_messages.append(new_message)

        self.session.commit()

        for msg in created_messages:
            self.session.refresh(msg)
            response.append(msg)

        return response
