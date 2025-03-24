# -*- coding: utf-8 -*-
"""
.. _hook:
钩子函数
===========================

钩子函数（Hooks）允许开发人员在特定执行点自定义智能体行为。它们提供了一种灵活的方式来修改或扩展智能体的功能，而无需更改其核心实现。

核心函数
-------------
AgentScope 围绕三个核心智能体函数实现了钩子函数：

- `reply`：根据智能体的当前状态生成响应消息
- `speak`：在终端显示和记录消息
- `observe`：记录传入的消息

可用钩子函数
-------------
每个核心函数都有对应的前后执行钩子：

- `pre_reply_hook` / `post_reply_hook`
- `pre_speak_hook` / `post_speak_hook`
- `pre_observe_hook` / `post_observe_hook`

例如，您可以使用 `pre_speak_hook` 将消息重定向到不同的输出，如 Web 界面或外部应用程序。

当使用钩子函数时，请记住以下重要规则：

1. **钩子函数签名**
 - 第一个参数必须是 `AgentBase` 对象，即 `self`
 - 后续参数是原始函数参数的副本

2. **执行顺序**
 - 钩子按注册顺序执行
 - 多个钩子函数可以链接在一起

3. **返回值处理**
 - 对于前置钩子：非 None 返回值会传递给下一个钩子或目标函数
  - 当钩子返回 None 时，下一个钩子将使用前面钩子的最近非 None 返回值
  - 如果所有前面的钩子返回 None，则下一个钩子将接收原始参数的副本
  - 最终的非 None 返回值（或者如果所有钩子返回 None，则原始参数）将传递给目标函数
 - 对于后置钩子： 只有 `post-reply` 钩子拥有返回值，工作方式与前置钩子相同

4. **重要提示**：永远不要在钩子函数中调用目标函数（reply/speak/observe）以避免无限循环

钩子函数模版
-----------------------

我们在下面为每个钩子函数提供了模板，以显示其参数签名。开发者可以将这些模板复制粘贴到您的代码中，
并根据需要进行自定义。
"""

from typing import Union, Optional

from agentscope.agents import AgentBase
from agentscope.message import Msg


def pre_reply_hook_template(
    self: AgentBase,
    x: Optional[Union[Msg, list[Msg]]] = None,
) -> Union[None, Msg, list[Msg]]:
    """reply 函数前置钩子函数模版"""
    pass


def post_reply_hook_template(self: AgentBase, x: Msg) -> Msg:
    """reply 函数后置钩子函数模版"""
    pass


def pre_speak_hook_template(
    self: AgentBase,
    x: Msg,
    stream: bool,
    last: bool,
) -> Union[Msg, None]:
    """speak 函数前置钩子函数模版"""
    pass


def post_speak_hook_template(self: AgentBase) -> None:
    """speak 函数后置钩子函数模版"""
    pass


def pre_observe_hook_template(
    self: AgentBase,
    x: Union[Msg, list[Msg]],
) -> Union[Msg, list[Msg]]:
    """observe 函数前置钩子函数模版"""
    pass


def post_observe_hook_template(self: AgentBase) -> None:
    """observe 函数后置钩子函数模版"""
    pass


# %%
# 使用样例
# -------------------
# AgentScope 允许通过调用相应的方法注册、移除和清除钩子函数。
#
# 我们首先创建一个简单的智能体，用于回显传入的消息：

from typing import Optional, Union

from agentscope.agents import AgentBase
from agentscope.message import Msg


class TestAgent(AgentBase):
    def __init__(self):
        super().__init__(name="TestAgent")

    def reply(self, x: Optional[Union[Msg, list[Msg]]] = None) -> Msg:
        self.speak(x)
        return x


# %%
# Reply 钩子函数
# ^^^^^^^^^^^^^^^^^^^^^^^
# 接下来，我们定义两个前置钩子函数，它们都修改输入的消息，但一个返回修改后的消息，另一个不返回：


def pre_reply_hook_1(
    self,
    x=None,
) -> Union[None, Msg, list[Msg]]:
    """第一个前置回复钩子，修改消息内容，但是不进行返回。"""
    if isinstance(x, Msg):
        x.content = "[Pre-hook-1] " + x.content
    elif isinstance(x, list):
        for msg in x:
            msg.content = "[Pre-hook-1] " + msg.content


def pre_reply_hook_2(
    self,
    x=None,
) -> Union[None, Msg, list[Msg]]:
    """第二个前置回复钩子，用于更改消息内容。"""
    if isinstance(x, Msg):
        x.content = "[Pre-hook-2] " + x.content
    elif isinstance(x, list):
        for msg in x:
            msg.content = "[Pre-hook-2] " + msg.content
    return x


# %%
# 然后，我们创建一个后置钩子，用于将后缀附加到消息内容：


def post_reply_hook(self, x) -> Msg:
    """后置回复钩子，用于将后缀附加到消息内容。"""
    x.content += " [Post-hook]"
    return x


# %%
# 最后，我们注册钩子并测试智能体：

agent = TestAgent()

agent.register_pre_reply_hook("pre_hook_1", pre_reply_hook_1)
agent.register_pre_reply_hook("pre_hook_2", pre_reply_hook_2)
agent.register_post_reply_hook("post_hook", post_reply_hook)

msg = Msg("user", "[原始消息]", "user")

msg_response = agent(msg)

print("回复消息的content域:\n", msg_response.content)

# %%
# 可以看到，响应消息有一个 "[Pre-hook-2]" 前缀和一个 "[Post-hook]" 后缀。
# "[Pre-hook-1]" 前缀缺失，因为第一个前置钩子没有返回修改后的消息。
#
# Speak 钩子函数
# ^^^^^^^^^^^^^^^^^^^^^^^
# 为了兼容流式输出，pre-speak 钩子函数接受两个额外的参数：
#
# - `stream`: 一个布尔标志，指示是否处于流式输出
# - `last`: 一个布尔标志，指示当前输入消息是否是流中的最后一个 Chunk
#
# .. tip:: 当处理流式输出时，可以使用消息 id 来确定两个消息是否来自同一个流式输出。
#
# 我们在下面展示如何使用 pre/post-speak 钩子：

from agentscope.agents import DialogAgent
import agentscope

agentscope.init(
    model_configs=[
        {
            "config_name": "streaming_config",
            "model_type": "dashscope_chat",
            "model_name": "qwen-max",
            "stream": True,
        },
    ],
)

streaming_agent = DialogAgent(
    name="TestAgent",
    model_config_name="streaming_config",
    sys_prompt="You're a helpful assistant.",
)


# 创建一个 pre-speak 钩子，用于显示消息内容
def pre_speak_hook(self, x: Msg, stream: bool, last: bool) -> None:
    """speak 函数前置钩子函数"""
    # 你可以在这里更改或重定向消息
    print(
        "id: ",
        x.id,
        "content: ",
        x.content,
        "stream: ",
        stream,
        "last: ",
        last,
    )


def post_speak_hook(self) -> None:
    """speak 函数后置钩子函数"""
    # 在这里计算调用 speak 函数的次数
    if not hasattr(self, "cnt"):
        self.cnt = 0
    self.cnt += 1


# Register the hooks
streaming_agent.register_pre_speak_hook("pre_speak_hook", pre_speak_hook)
streaming_agent.register_post_speak_hook("post_speak_hook", post_speak_hook)

msg = Msg(
    "user",
    "现在，从 1 到 15，步长为 1，用逗号分隔每个数字。",
    "user",
)

msg_response = streaming_agent(msg)

print("Speak 函数的调用次数：", streaming_agent.cnt)


# %%
# Observe 钩子函数
# ^^^^^^^^^^^^^^^^^^^^^^^
# 与 speak 钩子函数类似，我们在下面展示如何使用 pre/post-observe 钩子：

import json


def pre_observe_hook(self, x: Union[Msg, list[Msg]]) -> Union[Msg, list[Msg]]:
    """显示消息内容的前置观察钩子。"""
    if isinstance(x, Msg):
        x.content = "观察: " + x.content
    elif isinstance(x, list):
        for msg in x:
            msg.content = "观察: " + msg.content
    return x


def post_observe_hook(self) -> None:
    """显示消息内容的后置观察钩子。"""
    if not hasattr(self, "cnt"):
        setattr(self, "cnt", 0)
    self.cnt += 1


# 首先清除智能体记忆
agent.memory.clear()

agent.register_pre_observe_hook("pre_observe_hook", pre_observe_hook)
agent.register_post_observe_hook("post_observe_hook", post_observe_hook)

agent.observe(
    Msg(
        "user",
        "太阳升起来了。",
        "user",
    ),
)

print(
    "智能体的记忆：\n",
    json.dumps([_.to_dict() for _ in agent.memory.get_memory()], indent=4),
)
print("调用 Observe 函数的次数：", agent.cnt)
