# -*- coding: utf-8 -*-
"""
.. _react-agent:

Create ReAct Agent
====================

AgentScope provides out-of-the-box ReAct agent ``ReActAgent`` under ``agentscope.agent`` that can be used directly.

It supports the following features at the same time:

- ✨ Basic features
    - Support **hooks** around ``reply``, ``observe``, ``print``, ``_reasoning`` and ``_acting`` functions
    - Support structured output
- ✋ Realtime Steering
    - Support user **interrupt**
    - Support customized **interruption handling**
- 🛠️ Tools
    - Support both **sync/async** tool functions
    - Support **streaming** tool response
    - Support **stateful** tools management
    - Support **parallel** tool calls
    - Support **MCP** server
- 💾 Memory
    - Support **agent-controlled** long-term memory management
    - Support static long-term memory management

.. tip:: Refer to the :ref:`agent` section for more details about these
 features. In quickstart, we focus on how to create a ReAct agent and run it.

"""

from agentscope.agent import ReActAgent, AgentBase
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
import asyncio
import os

from agentscope.tool import Toolkit, execute_python_code


# %%
# Creating ReAct Agent
# ------------------------------
# To improve the flexibility, the ``ReActAgent`` class exposes the following parameters in its constructor:
#
# .. list-table:: Initialization parameters of ``ReActAgent`` class
#   :header-rows: 1
#
#   * - Parameter
#     - Further Reading
#     - Description
#   * - ``name`` (required)
#     -
#     - The name of the agent
#   * - ``sys_prompt`` (required)
#     -
#     - The system prompt of the agent
#   * - ``model`` (required)
#     - :ref:`model`
#     - The model used by the agent to generate responses
#   * - ``formatter`` (required)
#     - :ref:`prompt`
#     - The prompt construction strategy, should be consisted with the model
#   * - ``toolkit``
#     - :ref:`tool`
#     - The toolkit to register/call tool functions.
#   * - ``memory``
#     - :ref:`memory`
#     - The short-term memory used to store the conversation history
#   * - ``long_term_memory``
#     - :ref:`long-term-memory`
#     - The long-term memory
#   * - ``long_term_memory_mode``
#     - :ref:`long-term-memory`
#     - The mode of the long-term memory:
#
#       - ``agent_control``: allow agent to control the long-term memory by itself
#       - ``static_control``: retrieving and recording from/to long-term memory will happen in the beginning/end of each reply.
#       - ``both``: active the above two modes at the same time
#   * - ``enable_meta_tool``
#     - :ref:`tool`
#     - Whether to enable the meta tool, which allows the agent to manage tools by itself
#   * - ``parallel_tool_calls``
#     - :ref:`agent`
#     - Whether to allow parallel tool calls
#   * - ``max_iters``
#     -
#     - The maximum number of iterations for the agent to generate a response
#
# Taking DashScope API as example, we create an agent object as follows:


async def creating_react_agent() -> None:
    """Create a ReAct agent and run a simple task."""
    # Prepare tools
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_python_code)

    jarvis = ReActAgent(
        name="Jarvis",
        sys_prompt="You're a helpful assistant named Jarvis",
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ["DASHSCOPE_API_KEY"],
            stream=True,
            enable_thinking=False,
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
    )

    msg = Msg(
        name="user",
        content="Hi! Jarvis, run Hello World in Python.",
        role="user",
    )

    await jarvis(msg)


asyncio.run(creating_react_agent())

# %%
# Creating From Scratch
# --------------------------------
# You may want to create an agent from scratch, AgentScope provides two base classes for you to inherit from:
#
# .. list-table::
#   :header-rows: 1
#
#   * - Class
#     - Abstract Methods
#     - Description
#   * - ``AgentBase``
#     - | ``reply``
#       | ``observe``
#       | ``handle_interrupt``
#     - - The base class for all agents, supporting pre- and post- hooks around ``reply``, ``observe`` and ``print`` functions.
#       - Implement the realtime steering within the ``__call__`` method.
#   * - ``ReActAgentBase``
#     - | ``reply``
#       | ``observe``
#       | ``handle_interrupt``
#       | ``_reasoning``
#       | ``_acting``
#     - Add two abstract functions ``_reasoning`` and ``_acting`` on the basis of ``AgentBase``, as well as their hooks.
#
# Please refer to the :ref:`agent` section for more details about the agent class.
#
# Taking the ``AgentBase`` class as an example, we can create a custom agent
# class by inheriting from it and implementing the ``reply`` method.


class MyAgent(AgentBase):
    """A custom agent class"""

    def __init__(self) -> None:
        """Initialize the agent"""
        super().__init__()

        self.name = "Friday"
        self.sys_prompt = "You're a helpful assistant named Friday."
        self.model = DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ["DASHSCOPE_API_KEY"],
            stream=False,
        )
        self.formatter = DashScopeChatFormatter()
        self.memory = InMemoryMemory()

    async def reply(self, msg: Msg | list[Msg] | None) -> Msg:
        """Reply to the message."""
        await self.memory.add(msg)

        # Prepare the prompt
        prompt = await self.formatter.format(
            [
                Msg("system", self.sys_prompt, "system"),
                *await self.memory.get_memory(),
            ],
        )

        # Call the model
        response = await self.model(prompt)

        msg = Msg(
            name=self.name,
            content=response.content,
            role="assistant",
        )

        # Record the response in memory
        await self.memory.add(msg)

        # Print the message
        await self.print(msg)
        return msg

    async def observe(self, msg: Msg | list[Msg] | None) -> None:
        """Observe the message."""
        # Store the message in memory
        await self.memory.add(msg)

    async def handle_interrupt(self) -> Msg:
        """Postprocess the interrupt."""
        # Taking a fixed response as example
        return Msg(
            name=self.name,
            content="I noticed you interrupted me, how can I help you?",
            role="assistant",
        )


async def run_custom_agent() -> None:
    """Run the custom agent."""
    agent = MyAgent()
    msg = Msg(
        name="user",
        content="Who are you?",
        role="user",
    )
    await agent(msg)


asyncio.run(run_custom_agent())

# %%
#
# Further Reading
# ---------------------
# - :ref:`agent`
# - :ref:`model`
# - :ref:`prompt`
# - :ref:`tool`
#
