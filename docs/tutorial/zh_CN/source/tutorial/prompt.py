# -*- coding: utf-8 -*-
"""
.. _prompt-engineering:

提示工程
================================

提示工程是构建大语言模型应用的关键步骤，尤其是针对多智能体的应用。
然而，目前市面上大多数 API 服务只专注于 Chat 场景，即对话只有两个参与者：用户（user）和
助手（assistant），并且两者必须交替发送消息。

为了支持多智能体应用，AgentScope 构建了不同的提示策略，从而将一组 `Msg` 对象转换为模型
API 需要的格式。

.. note:: 目前还没有一种提示工程可以做到一劳永逸。AgentScope 内置提示构建策略的目标
 是让初学者可以顺利调用模型 API,而不是达到最佳性能。
 对于高级用户，我们建议开发人员根据需求和模型 API 要求来自定义提示构建策略。

提示构建策略
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

内置提示策略在模型类的 `format` 方法中实现。以 DashScope Chat API 为例:

"""

from agentscope.models import DashScopeChatWrapper
from agentscope.message import Msg
import json


model = DashScopeChatWrapper(
    config_name="_",
    model_name="qwen-max",
)

# 可以将 `Msg` 对象或 `Msg` 对象列表传递给 `format` 方法
prompt = model.format(
    Msg("system", "You're a helpful assistant.", "system"),
    [
        Msg("assistant", "Hi!", "assistant"),
        Msg("user", "Nice to meet you!", "user"),
    ],
)

print(json.dumps(prompt, indent=4, ensure_ascii=False))

# %%
# 格式化输入消息后，我们可以将其传给 `model` 对象，进行实际的 API 调用。
#

response = model(prompt)

print(response.text)

# %%
# 非视觉模型
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# 在下表中，我们列出了内置的提示策略，以及支持的大语言模型的前缀。
#
# 以下面的消息为例:
#
# .. code-block:: python
#
#     Msg("system", "You're a helpful assistant named Alice.", "system"),
#     Msg("Alice", "Hi!", "assistant"),
#     Msg("Bob", "Nice to meet you!", "user")
#
#
# .. list-table::
#     :header-rows: 1
#
#     * - LLMs
#       - `model_name`
#       - Constructed Prompt
#     * - OpenAI LLMs
#       - `gpt-`
#       - .. code-block:: python
#
#             [
#                 {
#                     "role": "system",
#                     "name": "system",
#                     "content": "You're a helpful assistant named Alice."
#                 },
#                 {
#                     "role": "user",
#                     "name": "Alice",
#                     "content": "Hi!"
#                 },
#                 {
#                     "role": "user",
#                     "name": "Bob",
#                     "content": "Nice to meet you!"
#                 }
#             ]
#     * - Gemini LLMs
#       - `gemini-`
#       - .. code-block:: python
#
#             [
#                 {
#                     "role": "user",
#                     "parts": [
#                         "You're a helpful assistant named Alice.\\n## Conversation History\\nAlice: Hi!\\nBob: Nice to meet you!"
#                     ]
#                 }
#             ]
#     * - All other LLMs
#
#         (e.g. DashScope, ZhipuAI ...)
#       -
#       - .. code-block:: python
#
#             [
#                 {
#                     "role": "system",
#                     "content": "You're a helpful assistant named Alice."
#                 },
#                 {
#                     "role": "user",
#                     "content": "## Conversation History\\nAlice: Hi!\\nBob: Nice to meet you!"
#                 }
#             ]
#
# .. tip:: 考虑到一些 API 兼容不同的大语言模型（例如 OpenAI Python 库），AgentScope 使用 `model_name` 字段来区分不同的模型并决定最终使用的策略。
#
# 视觉模型
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# 对于视觉模型，AgentScope 目前支持 OpenAI 视觉模型和 Dashscope 多模态 API。
# 未来将假如更多的视觉模型的支持。
#
