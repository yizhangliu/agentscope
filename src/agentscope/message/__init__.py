# -*- coding: utf-8 -*-
<<<<<<< HEAD
"""The message module of AgentScope."""

from .msg import (
    Msg,
)

from .block import (
    ToolUseBlock,
    ToolResultBlock,
    TextBlock,
    ImageBlock,
    AudioBlock,
    VideoBlock,
    FileBlock,
    ContentBlock,
)

__all__ = [
    "Msg",
    "ToolUseBlock",
    "ToolResultBlock",
    "TextBlock",
    "ImageBlock",
    "AudioBlock",
    "VideoBlock",
    "FileBlock",
    "ContentBlock",
=======
"""The message module in agentscope."""

from ._message_block import (
    ContentBlock,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
    ImageBlock,
    AudioBlock,
    VideoBlock,
    Base64Source,
    URLSource,
)
from ._message_base import Msg


__all__ = [
    "TextBlock",
    "ThinkingBlock",
    "Base64Source",
    "URLSource",
    "ImageBlock",
    "AudioBlock",
    "VideoBlock",
    "ToolUseBlock",
    "ToolResultBlock",
    "ContentBlock",
    "Msg",
>>>>>>> 6ee8fa352bcaf888adf82124e0e0a5c394454506
]
