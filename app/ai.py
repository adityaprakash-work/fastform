"""AI Logic."""

from enum import Enum
import json as j

import guidance
from guidance import assistant, gen, image, json, system, user
from guidance.models import Model
from guidance.models._openai_base import ContentMessage
from pydantic import BaseModel, ConfigDict

from .fastform import Form

SYSTEM_PROMPT = """You are a helpful assistant for the FastForm application.
Your task is to assist users in creating and modifying forms based on their requests.

You are not supposed to provide any values for any of the bbox fields in the form. If 
the frontend system provides values for the bbox fields, you must not change them. 
Analyze the user's request and provide the necessary changes to the form structure. Try 
to cover all possible fields that the page might have.
"""

SYSTEM_PROMPT_FILL = """You are a helpful assistant for the FastForm application.
Your task is to assist users in filling out forms based on their requests. Here is the
form structure:

{form_structure}

You must not deviate from the provided structure expect for values filled in by the
frontend system.

The frontend system might change values of the fields but NEVER change the structure
of the form and you must not do the same. Your task is to just fill in the fields based 
on the conversation with the user.
"""


class Response(Enum):
    """Enumeration for AI responses."""

    yes = "yes"
    no = "no"


class YesNo(BaseModel):
    """Simple Yes/No model for JSON responses."""

    model_config = ConfigDict(extra="forbid")
    selection: Response


def fastformbuild_chat(
    lm: Model, messages: list[ContentMessage]
) -> list[ContentMessage]:
    """Generate a new form based on the user's request.

    Args:
        lm: The language model to use.
        messages: The messages to use.

    Returns:
        A list of messages.
    """
    lm = lm.copy()
    lm._interpreter.state.messages = messages

    with assistant():
        lm += """\
        Now I will analyze the user's request to determine if they are asking to create 
        a new form or modify an existing one.
        If any of the above is true, I will respond with a JSON object containing
        the form structure.
        If not, I will continue with the conversation as usual.

        So, Is the user asking to create a new form or modify an existing one?
        """
    with assistant():
        lm += json(name="yes_no", schema=YesNo)

    selection = j.loads(lm["yes_no"])["selection"]
    # selection = "yes"

    new_messages = []

    if selection == Response.yes.value:
        with assistant():
            lm += "Now I will generate a new form based on the user's request."
        with assistant():
            lm += json(name="new_form", schema=Form)
        with assistant():
            lm += """\
        Now I will provide additional commentary/end of message comment on the above 
        form structure but not repeat the structure itself.
        """
        with assistant():
            lm += gen("message")

        new_messages = [lm._interpreter.state.messages[-2]] + [
            lm._interpreter.state.get_active_message()
        ]

    elif selection == Response.no.value:
        with assistant():
            lm += """\
        The user is not asking to create a new form or modify an existing one.
        I will continue with the conversation as usual.
        """
        with assistant():
            lm += gen("message")

        new_messages = [lm._interpreter.state.get_active_message()]

    return new_messages


def fastformfill_chat(
    lm: Model, messages: list[ContentMessage]
) -> list[ContentMessage]:
    """Fill out a form based on the user's request.

    Args:
        lm: The language model to use.
        messages: The messages to use.

    Returns:
        A list of messages.
    """
    lm = lm.copy()
    lm._interpreter.state.messages = messages

    with assistant():
        lm += """\
        Now I will analyze the user's request to determine if they are asking to fill out
        a form based on the provided form structure.
        If yes I will respond with a JSON object containing the filled form.
        If not, I will continue with the conversation as usual.
        """
    with assistant():
        lm += json(name="yes_no", schema=YesNo)

    selection = j.loads(lm["yes_no"])["selection"]
    # selection = "yes"

    new_messages = []

    if selection == Response.yes.value:
        with assistant():
            lm += "Now I will generate a filled form based on the user's request."
        with assistant():
            lm += json(name="filled_form", schema=Form)
        with assistant():
            lm += """\
        Now I will provide additional commentary/end of message comment on the above 
        filled form but not repeat the form itself.
        """
        with assistant():
            lm += gen("message")

        new_messages = [lm._interpreter.state.messages[-2]] + [
            lm._interpreter.state.get_active_message()
        ]

    elif selection == Response.no.value:
        with assistant():
            lm += """\
        The user is not asking to fill out a form based on the provided form structure.
        I will continue with the conversation as usual.
        """
        with assistant():
            lm += gen("message")

        new_messages = [lm._interpreter.state.get_active_message()]

    return new_messages
