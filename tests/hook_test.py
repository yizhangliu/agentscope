# -*- coding: utf-8 -*-
<<<<<<< HEAD
# pylint: disable=unused-argument, protected-access
"""Unittests for agent hooks."""
import unittest
from typing import Optional, Union, Tuple, Any, Dict
from unittest.mock import patch, MagicMock

from agentscope.agents import AgentBase
from agentscope.message import Msg


class _TestAgent(AgentBase):
    """A test agent."""

    def __init__(self) -> None:
        """Initialize the test agent."""
        super().__init__(
            name="Friday",
            use_memory=True,
        )

    def reply(self, x: Optional[Union[Msg, list[Msg]]] = None) -> Msg:
        """Reply function."""
        if x is not None:
            self.speak(x)
        return x


cnt_post = 0


class AgentHooksTest(unittest.TestCase):
    """Unittests for agent hooks."""

    def setUp(self) -> None:
        """Set up the test."""
        self.agent = _TestAgent()
        self.agent2 = _TestAgent()

    def test_reply_hook(self) -> None:
        """Test the reply hook."""

        def pre_reply_hook(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
        ) -> Union[Tuple[Tuple[Msg, ...], Dict[str, Any]], None]:
            """Pre-reply hook."""
            if len(args) > 0 and isinstance(args[0], Msg):
                args[0].content = "-1, " + args[0].content
                return args, kwargs
            return None

        def pre_reply_hook_without_change(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
        ) -> None:
            """Pre-reply hook without returning, so that the message is not
            changed."""
            if len(args) > 0 and isinstance(args[0], Msg):
                args[0].content = "-2, " + x.content

        def post_reply_hook(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
            x: Msg,
        ) -> Msg:
            """Post-reply hook."""
            return Msg(
                "assistant",
                x.content + ", 1",
                "assistant",
            )

        msg_test = Msg("user", "0", "user")

        # Test without hooks
        x = self.agent(msg_test)
        self.assertEqual("0", x.content)

        # Test with one pre hook
        self.agent.register_hook("pre_reply", "first_pre_hook", pre_reply_hook)
        x = self.agent(msg_test)
        self.assertEqual("-1, 0", x.content)

        # Test with one pre and one post hook
        self.agent.register_hook(
            "post_reply",
            "first_post_hook",
            post_reply_hook,
        )
        x = self.agent(msg_test)
        self.assertEqual("-1, 0, 1", x.content)

        # Test with two pre hooks and one post hook
        self.agent.register_hook(
            "pre_reply",
            "second_pre_hook",
            pre_reply_hook,
        )
        x = self.agent(msg_test)
        self.assertEqual("-1, -1, 0, 1", x.content)

        # Test removing one pre hook
        self.agent.remove_hook("pre_reply", "first_pre_hook")
        x = self.agent(msg_test)
        self.assertEqual("-1, 0, 1", x.content)

        # Test removing one post hook
        self.agent.remove_hook("post_reply", "first_post_hook")
        x = self.agent(msg_test)
        self.assertEqual("-1, 0", x.content)

        # Test clearing all pre hooks
        self.agent.clear_hooks("pre_reply")
        x = self.agent(msg_test)
        self.assertEqual("0", x.content)

        # Test with three pre hooks, change -> not change -> change
        self.agent.register_hook("pre_reply", "first_pre_hook", pre_reply_hook)
        self.agent.register_hook(
            "pre_reply",
            "second_pre_hook",
            pre_reply_hook_without_change,
        )
        self.agent.register_hook("pre_reply", "third_pre_hook", pre_reply_hook)
        x = self.agent(msg_test)
        self.assertEqual("-1, -1, 0", x.content)

        # Test with no input
        self.agent()

    @patch("agentscope.agents._agent.log_msg")
    def test_speak_hook(self, mock_log_msg: MagicMock) -> None:
        """Test the speak hook."""

        def pre_speak_hook_change(
            self: AgentBase,
            msg: Msg,
            stream: bool,
            last: bool,
        ) -> Msg:
            """Pre-speak hook."""
            msg.content = "-1, " + msg.content
            return msg

        def pre_speak_hook_change2(
            self: AgentBase,
            msg: Msg,
            stream: bool,
            last: bool,
        ) -> Msg:
            """Pre-speak hook."""
            msg.content = "-2, " + msg.content
            return msg

        def pre_speak_hook_without_change(
            self: AgentBase,
            msg: Msg,
            stream: bool,
            last: bool,
        ) -> None:
            """Pre-speak hook."""
            return None

        def post_speak_hook(self: AgentBase) -> None:
            """Post-speak hook."""
            if not hasattr(self, "cnt"):
                self.cnt = 0
            self.cnt += 1

        self.agent.register_hook(
            "pre_speak",
            "first_pre_hook",
            pre_speak_hook_change,
        )
        self.agent.register_hook(
            "pre_speak",
            "second_pre_hook",
            pre_speak_hook_change2,
        )
        self.agent.register_hook(
            "pre_speak",
            "third_pre_hook",
            pre_speak_hook_without_change,
        )
        self.agent.register_hook(
            "post_speak",
            "first_post_hook",
            post_speak_hook,
        )
        self.agent.register_hook(
            "post_speak",
            "second_post_hook",
            post_speak_hook,
        )

        test_msg = Msg("user", "0", "user")

        x = self.agent(test_msg)
        # The speak function shouldn't affect the reply message
        self.assertEqual(x.content, "0")

        self.assertEqual("-2, -1, 0", mock_log_msg.call_args[0][0].content)
        self.assertEqual(2, self.agent.cnt)

    def test_observe_hook(self) -> None:
        """Test the observe hook."""

        def pre_observe_hook_change(self: AgentBase, msg: Msg) -> Msg:
            """Pre-observe hook with returning, where the message will be
            changed."""
            msg.content = "-1, " + msg.content
            return msg

        def pre_observe_hook_not_change(self: AgentBase, msg: Msg) -> None:
            """Pre-observe hook without returning, so that the message is not
            changed."""
            msg.content = "-2, " + msg.content

        global cnt_post
        cnt_post = 0

        def post_observe_hook(self: AgentBase) -> None:
            """Post-observe hook."""
            global cnt_post
            cnt_post += 1

        msg_test = Msg("user", "0", "user")
        msg_test2 = Msg("user", "0", "user")

        self.agent.observe(msg_test)
        self.assertEqual("0", self.agent.memory.get_memory()[0].content)

        self.agent.register_hook(
            "pre_observe",
            "first_pre_hook",
            pre_observe_hook_change,
        )
        self.agent.register_hook(
            "pre_observe",
            "second_pre_hook",
            pre_observe_hook_not_change,
        )
        self.agent.register_hook(
            "post_observe",
            "first_post_hook",
            post_observe_hook,
        )

        self.agent.observe(msg_test2)
        # The reply should not be affected due to deep copy
        # The memory should be affected
        print(self.agent.memory.get_memory())
        self.assertEqual(
            "-1, 0",
            self.agent.memory.get_memory()[1].content,
        )
        self.assertEqual(1, cnt_post)

    def test_class_and_object_pre_reply_hook(self) -> None:
        """Test the class and object hook."""

        def pre_reply_hook_1(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
        ) -> Union[Tuple[Tuple[Msg, ...], Dict[str, Any]], None]:
            """Pre-reply hook."""
            args[0].content = "-1, " + args[0].content
            return args, kwargs

        def pre_reply_hook_2(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
        ) -> Union[Tuple[Tuple[Msg, ...], Dict[str, Any]], None]:
            """Pre-reply hook."""
            args[0].content = "-2, " + args[0].content
            return args, kwargs

        AgentBase.register_class_hook(
            "pre_reply",
            "first_hook",
            pre_reply_hook_1,
        )

        self.assertListEqual(
            list(self.agent._class_hooks_pre_reply.keys()),
            ["first_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_pre_reply.keys()),
            ["first_hook"],
        )
        AgentBase.clear_all_class_hooks()

        self.agent.register_hook(
            "pre_reply",
            "second_hook",
            pre_reply_hook_1,
        )
        self.assertListEqual(
            list(self.agent._hooks_pre_reply.keys()),
            ["second_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_pre_reply.keys()),
            [],
        )

        AgentBase.register_class_hook(
            "pre_reply",
            "third_hook",
            pre_reply_hook_2,
        )

        msg_test = Msg("user", "0", "user")

        res = self.agent(msg_test)
        self.assertEqual(res.content, "-2, -1, 0")

        res = self.agent2(msg_test)
        self.assertEqual(res.content, "-2, 0")

    def test_class_and_object_post_reply_hook(self) -> None:
        """Test the class and object hook."""

        def post_reply_hook_1(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
            output: Msg,
        ) -> Union[None, Msg]:
            """Post-reply hook."""
            return Msg("assistant", output.content + ", 1", "assistant")

        def post_reply_hook_2(
            self: AgentBase,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
            output: Msg,
        ) -> Union[None, Msg]:
            """Post-reply hook."""
            return Msg("assistant", output.content + ", 2", "assistant")

        AgentBase.register_class_hook(
            "post_reply",
            "first_hook",
            post_reply_hook_1,
        )

        self.assertListEqual(
            list(self.agent._class_hooks_post_reply.keys()),
            ["first_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_post_reply.keys()),
            ["first_hook"],
        )
        AgentBase.clear_all_class_hooks()

        self.agent.register_hook(
            "post_reply",
            "second_hook",
            post_reply_hook_1,
        )
        self.assertListEqual(
            list(self.agent._hooks_post_reply.keys()),
            ["second_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_post_reply.keys()),
            [],
        )

        AgentBase.register_class_hook(
            "post_reply",
            "third_hook",
            post_reply_hook_2,
        )

        msg_test = Msg("user", "0", "user")

        res = self.agent(msg_test)
        self.assertEqual(res.content, "0, 1, 2")

        res = self.agent2(msg_test)
        self.assertEqual(res.content, "0, 2")

    def test_class_and_object_pre_observe_hook(self) -> None:
        """Test the class and object hook."""

        def pre_observe_hook_1(self: AgentBase, x: Msg) -> Msg:
            """Pre-observe hook."""
            return Msg("assistant", "-1, " + x.content, "assistant")

        def pre_observe_hook_2(self: AgentBase, x: Msg) -> Msg:
            """Pre-observe hook."""
            return Msg("assistant", "-2, " + x.content, "assistant")

        AgentBase.register_class_hook(
            "pre_observe",
            "first_hook",
            pre_observe_hook_1,
        )

        self.assertListEqual(
            list(self.agent._class_hooks_pre_observe.keys()),
            ["first_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_pre_observe.keys()),
            ["first_hook"],
        )
        AgentBase.clear_all_class_hooks()

        self.agent.register_hook(
            "pre_observe",
            "second_hook",
            pre_observe_hook_1,
        )
        self.assertListEqual(
            list(self.agent._hooks_pre_observe.keys()),
            ["second_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_pre_observe.keys()),
            [],
        )

        AgentBase.register_class_hook(
            "pre_observe",
            "third_hook",
            pre_observe_hook_2,
        )

        msg_test = Msg("user", "0", "user")

        self.agent.observe(msg_test)
        self.assertEqual(
            "-2, -1, 0",
            self.agent.memory.get_memory()[0].content,
        )

        self.agent2.observe(msg_test)
        self.assertEqual(
            "-2, 0",
            self.agent2.memory.get_memory()[0].content,
        )

    @patch("agentscope.agents._agent.log_msg")
    def test_class_and_object_pre_speak_hook(
        self,
        mock_log_msg: MagicMock,
    ) -> None:
        """Test the class and object hook."""

        def pre_speak_hook_change(
            self: AgentBase,
            msg: Msg,
            stream: bool,
            last: bool,
        ) -> Msg:
            """Pre-speak hook."""
            msg.content = "-1, " + msg.content
            return msg

        def pre_speak_hook_change2(
            self: AgentBase,
            msg: Msg,
            stream: bool,
            last: bool,
        ) -> Msg:
            """Pre-speak hook."""
            msg.content = "-2, " + msg.content
            return msg

        AgentBase.register_class_hook(
            "pre_speak",
            "first_hook",
            pre_speak_hook_change,
        )

        self.assertListEqual(
            list(self.agent._class_hooks_pre_speak.keys()),
            ["first_hook"],
        )
        self.assertListEqual(
            list(self.agent2._class_hooks_pre_speak.keys()),
            ["first_hook"],
        )

        self.agent.register_hook(
            "pre_speak",
            "first_obj_hook",
            pre_speak_hook_change2,
        )

        msg_test = Msg("user", "0", "user")

        self.agent(msg_test)
        self.assertEqual("-1, -2, 0", mock_log_msg.call_args[0][0].content)

        self.agent2(msg_test)
        self.assertEqual("-1, 0", mock_log_msg.call_args[0][0].content)

    def tearDown(self) -> None:
        """Tear down the test."""
        self.agent.clear_all_obj_hooks()
        self.agent2.clear_all_obj_hooks()

        AgentBase.clear_all_class_hooks()
        self.agent.memory.clear()
=======
"""Hook related tests in agentscope."""
from typing import Any
from unittest.async_case import IsolatedAsyncioTestCase

from agentscope.agent import AgentBase
from agentscope.message import Msg, TextBlock


class MyAgent(AgentBase):
    """Test agent class for testing hooks."""

    def __init__(self) -> None:
        """Initialize the test agent."""
        super().__init__()
        self.records: list[str] = []
        self.memory: list[Msg] = []

    async def reply(self, msg: Msg) -> Msg:
        """Reply to the message."""
        await self.print(msg)
        if isinstance(msg.content, list):
            msg.content.append(
                TextBlock(
                    type="text",
                    text="mark",
                ),
            )
        return msg

    async def observe(self, msg: Msg) -> None:
        """Observe the message without generating a reply."""
        self.memory.append(msg)

    async def handle_interrupt(self, *args: Any, **kwargs: Any) -> Msg:
        """Handle the interrupt signal."""
        # This is a placeholder for handling interrupts.
        return Msg("test", "Interrupt handled", "assistant")


class ChildAgent(MyAgent):
    """Child agent for testing hook isolation."""


class GrandChildAgent(ChildAgent):
    """Grandchild agent for testing deeper inheritance."""


class AgentA(MyAgent):
    """First parent class."""


class AgentB(MyAgent):
    """Second parent class."""


class AgentC(AgentA, AgentB):
    """Multiple inheritance class."""


async def async_pre_func_w_modifying(
    self: MyAgent,
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """A pre-hook function that modifies the keyword arguments."""

    if isinstance(kwargs.get("msg"), Msg):
        kwargs["msg"].content.append(
            TextBlock(
                type="text",
                text="pre_1",
            ),
        )
    self.records.append("pre_1")
    return kwargs


async def async_pre_func_wo_modifying(
    self: MyAgent,
    kwargs: dict[str, Any],
) -> None:
    """A pre-hook function that does not modify the keyword arguments."""
    if isinstance(kwargs.get("msg"), Msg):
        kwargs["msg"].content.append(
            TextBlock(
                type="text",
                text="pre_2",
            ),
        )
    self.records.append("pre_2")


def sync_pre_func_w_modifying(
    self: MyAgent,
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """A synchronous pre-hook function that does not modify the keyword
    arguments."""
    if isinstance(kwargs.get("msg"), Msg):
        kwargs["msg"].content.append(
            TextBlock(
                type="text",
                text="pre_3",
            ),
        )
    self.records.append("pre_3")
    return kwargs


def sync_pre_func_wo_modifying(
    self: MyAgent,
    kwargs: dict[str, Any],
) -> None:
    """A synchronous pre-hook function that does not modify the keyword
    arguments."""
    if isinstance(kwargs.get("msg"), Msg):
        kwargs["msg"].content.append(
            TextBlock(
                type="text",
                text="pre_4",
            ),
        )
    self.records.append("pre_4")


async def async_post_func_w_modifying(
    self: MyAgent,
    _kwargs: dict[str, Any],
    output: Any,
) -> Any:
    """A post-hook function that modifies the output."""
    if isinstance(output, Msg):
        output.content.append(
            TextBlock(
                type="text",
                text="post_1",
            ),
        )
    self.records.append("post_1")
    return output


async def async_post_func_wo_modifying(
    self: MyAgent,
    _kwargs: dict[str, Any],
    output: Any,
) -> None:
    """A post-hook function that does not modify the output."""
    if isinstance(output, Msg):
        output.content.append(
            TextBlock(
                type="text",
                text="post_2",
            ),
        )
    self.records.append("post_2")


def sync_post_func_w_modifying(
    self: MyAgent,
    _kwargs: dict[str, Any],
    output: Any,
) -> Any:
    """A synchronous post-hook function that modifies the output."""
    if isinstance(output, Msg):
        output.content.append(
            TextBlock(
                type="text",
                text="post_3",
            ),
        )
    self.records.append("post_3")
    return output


def sync_post_func_wo_modifying(
    self: MyAgent,
    _kwargs: dict[str, Any],
    output: Any,
) -> None:
    """A synchronous post-hook function that does not modify the output."""
    if isinstance(output, Msg):
        output.content.append(
            TextBlock(
                type="text",
                text="post_4",
            ),
        )
    self.records.append("post_4")


class HookTest(IsolatedAsyncioTestCase):
    """The hook test class."""

    async def asyncSetUp(self) -> None:
        """Set up the test environment."""
        self.agent = MyAgent()

    @property
    def msg(self) -> Msg:
        """Get the test message."""
        return Msg(
            "user",
            [TextBlock(type="text", text="0")],
            "user",
        )

    async def test_reply_hooks(self) -> None:
        """Test the reply hooks."""
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="mark"),
            ],
        )

        # Add pre 1
        self.agent.register_instance_hook(
            "pre_reply",
            "pre_1",
            async_pre_func_w_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="mark"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            ["pre_1"],
        )

        # Add pre 2
        self.agent.register_instance_hook(
            "pre_reply",
            "pre_2",
            async_pre_func_wo_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="mark"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            ["pre_1", "pre_1", "pre_2"],
        )

        # Add sync pre 3
        self.agent.register_instance_hook(
            "pre_reply",
            "pre_3",
            sync_pre_func_w_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="pre_3"),
                TextBlock(type="text", text="mark"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_1",
                "pre_2",
                "pre_1",
                "pre_2",
                "pre_3",
            ],
        )

        # Add sync pre 4
        self.agent.register_instance_hook(
            "pre_reply",
            "pre_4",
            sync_pre_func_wo_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="pre_3"),
                TextBlock(type="text", text="mark"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_1",
                "pre_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
            ],
        )

        # Add post 1
        self.agent.register_instance_hook(
            "post_reply",
            "post_1",
            async_post_func_w_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="pre_3"),
                TextBlock(type="text", text="mark"),
                TextBlock(type="text", text="post_1"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_1",
                "pre_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
            ],
        )

        # Add post 2
        self.agent.register_instance_hook(
            "post_reply",
            "post_2",
            async_post_func_wo_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="pre_3"),
                TextBlock(type="text", text="mark"),
                TextBlock(type="text", text="post_1"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_1",
                "pre_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "post_2",
            ],
        )

        # Add sync post 3
        self.agent.register_instance_hook(
            "post_reply",
            "post_3",
            sync_post_func_w_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="pre_3"),
                TextBlock(type="text", text="mark"),
                TextBlock(type="text", text="post_1"),
                TextBlock(type="text", text="post_3"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_1",
                "pre_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "post_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "post_2",
                "post_3",
            ],
        )

        # Add sync post 4
        self.agent.register_instance_hook(
            "post_reply",
            "post_4",
            sync_post_func_wo_modifying,
        )
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
                TextBlock(type="text", text="pre_3"),
                TextBlock(type="text", text="mark"),
                TextBlock(type="text", text="post_1"),
                TextBlock(type="text", text="post_3"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_1",
                "pre_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "post_2",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "post_2",
                "post_3",
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
                "post_1",
                "post_2",
                "post_3",
                "post_4",
            ],
        )

        self.agent.clear_instance_hooks()
        self.agent.records.clear()
        res = await self.agent(self.msg)
        self.assertListEqual(
            res.content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="mark"),
            ],
        )
        self.assertListEqual(
            self.agent.records,
            [],
        )

    async def test_print_hooks(self) -> None:
        """Test the print hooks."""
        self.agent.register_instance_hook(
            "pre_print",
            "pre_1",
            async_pre_func_w_modifying,
        )
        self.agent.register_instance_hook(
            "pre_print",
            "pre_2",
            async_pre_func_wo_modifying,
        )
        self.agent.register_instance_hook(
            "pre_print",
            "pre_3",
            sync_pre_func_w_modifying,
        )
        self.agent.register_instance_hook(
            "pre_print",
            "pre_4",
            sync_pre_func_wo_modifying,
        )
        await self.agent(self.msg)
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_2",
                "pre_3",
                "pre_4",
            ],
        )

    async def test_observe_hooks(self) -> None:
        """Test the observe hooks."""
        self.agent.register_instance_hook(
            "pre_observe",
            "pre_1",
            async_pre_func_w_modifying,
        )
        self.agent.register_instance_hook(
            "pre_observe",
            "pre_2",
            async_pre_func_wo_modifying,
        )
        await self.agent.observe(self.msg)
        self.assertEqual(len(self.agent.memory), 1)
        self.assertListEqual(
            self.agent.records,
            [
                "pre_1",
                "pre_2",
            ],
        )
        self.assertListEqual(
            self.agent.memory[0].content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
            ],
        )

        self.agent.register_instance_hook(
            "post_observe",
            "post_1",
            async_post_func_w_modifying,
        )
        self.agent.register_instance_hook(
            "post_observe",
            "post_2",
            async_post_func_wo_modifying,
        )
        await self.agent.observe(self.msg)
        self.assertEqual(
            len(self.agent.memory),
            2,
        )
        self.assertListEqual(
            self.agent.records,
            ["pre_1", "pre_2", "pre_1", "pre_2", "post_1", "post_2"],
        )
        self.assertListEqual(
            self.agent.memory[1].content,
            [
                TextBlock(type="text", text="0"),
                TextBlock(type="text", text="pre_1"),
            ],
        )

    # TODO: The studio requires the hook inherited from AgentBase, we will
    #  solving this problem later.
    # async def test_instance_and_class_hooks(self) -> None:
    #     """Test instance and class hooks."""
    #     AgentBase.register_class_hook(
    #         "pre_reply",
    #         "pre_3",
    #         sync_pre_func_w_modifying,
    #     )
    #     self.agent.register_instance_hook(
    #         "pre_reply",
    #         "pre_1",
    #         async_pre_func_w_modifying,
    #     )
    #     res = await self.agent(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="pre_1"),
    #             TextBlock(type="text", text="mark"),
    #         ],
    #     )
    #
    #     # remove hook
    #     AgentBase.remove_class_hook("pre_reply", "pre_3")
    #     res = await self.agent(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="pre_1"),
    #             TextBlock(type="text", text="mark"),
    #         ],
    #     )
    #
    # async def test_class_hook_inheritance_isolation(self) -> None:
    #     """Test that class hooks are isolated between parent and child
    #     classes."""
    #
    #     # Register different hooks on different classes
    #     MyAgent.register_class_hook(
    #         "pre_reply",
    #         "parent_hook",
    #         sync_pre_func_w_modifying,  # adds "pre_3" to content
    #     )
    #
    #     ChildAgent.register_class_hook(
    #         "pre_reply",
    #         "child_hook",
    #         async_pre_func_w_modifying,  # adds "pre_1" to content
    #     )
    #
    #     GrandChildAgent.register_class_hook(
    #         "pre_reply",
    #         "grandchild_hook",
    #         sync_pre_func_wo_modifying,  # adds "pre_4" to content
    #     )
    #
    #     # Create instances of each class
    #     parent_agent = MyAgent()
    #     child_agent = ChildAgent()
    #     grandchild_agent = GrandChildAgent()
    #
    #     # Test parent agent - should only execute parent hook
    #     res = await parent_agent(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="pre_3"),  # only parent hook
    #             TextBlock(type="text", text="mark"),
    #         ],
    #     )
    #     self.assertListEqual(parent_agent.records, ["pre_3"])
    #
    #     # Test child agent - should only execute child hook
    #     res = await child_agent(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="pre_1"),  # only child hook
    #             TextBlock(type="text", text="mark"),
    #         ],
    #     )
    #     self.assertListEqual(child_agent.records, ["pre_1"])
    #
    #     # Test grandchild agent - should only execute grandchild hook
    #     res = await grandchild_agent(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="mark"),
    #             # pre_4 doesn't modify content
    #         ],
    #     )
    #     self.assertListEqual(grandchild_agent.records, ["pre_4"])
    #
    # async def test_multiple_inheritance_hook_isolation(self) -> None:
    #     """Test hook isolation in multiple inheritance scenarios."""
    #
    #     # Register hooks on different classes
    #     AgentA.register_class_hook(
    #         "pre_reply",
    #         "hook_a",
    #         sync_pre_func_w_modifying,  # adds "pre_3"
    #     )
    #
    #     AgentB.register_class_hook(
    #         "pre_reply",
    #         "hook_b",
    #         async_pre_func_w_modifying,  # adds "pre_1"
    #     )
    #
    #     AgentC.register_class_hook(
    #         "pre_reply",
    #         "hook_c",
    #         sync_pre_func_wo_modifying,  # adds "pre_4" (no content change)
    #     )  # Create instances
    #     agent_a = AgentA()
    #     agent_b = AgentB()
    #     agent_c = AgentC()
    #
    #     # Test AgentA - should only execute hook_a
    #     res = await agent_a(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="pre_3"),
    #             TextBlock(type="text", text="mark"),
    #         ],
    #     )
    #     self.assertListEqual(agent_a.records, ["pre_3"])
    #
    #     # Test AgentB - should only execute hook_b
    #     res = await agent_b(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="pre_1"),
    #             TextBlock(type="text", text="mark"),
    #         ],
    #     )
    #     self.assertListEqual(agent_b.records, ["pre_1"])
    #
    #     # Test AgentC - should only execute hook_c
    #     res = await agent_c(self.msg)
    #     self.assertListEqual(
    #         res.content,
    #         [
    #             TextBlock(type="text", text="0"),
    #             TextBlock(type="text", text="mark"),
    #             # pre_4 doesn't modify content
    #         ],
    #     )
    #     self.assertListEqual(agent_c.records, ["pre_4"])

    async def asyncTearDown(self) -> None:
        """Tear down the test environment."""
        self.agent.clear_instance_hooks()
        MyAgent.clear_class_hooks()

        ChildAgent.clear_class_hooks()
        GrandChildAgent.clear_class_hooks()

        AgentA.clear_class_hooks()
        AgentB.clear_class_hooks()
        AgentC.clear_class_hooks()
>>>>>>> 6ee8fa352bcaf888adf82124e0e0a5c394454506
