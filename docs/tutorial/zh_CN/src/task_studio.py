# -*- coding: utf-8 -*-
"""
.. _studio:

AgentScope Studio
=========================

AgentScope Studio 是一个本地部署的 Web 应用程序，它

- 为智能体应用程序的开发提供 **项目管理**
- 为运行中的应用程序提供 **可视化** 追踪
- 内置一个为 "Friday" 的 **智能体**，支持用户二次开发

.. note:: Studio 正在快速开发中，更多功能即将推出！

.. figure:: ../../_static/images/studio_home.webp
    :width: 100%
    :alt: AgentScope Studio 主页
    :class: bordered-image
    :align: center

    AgentScope Studio 主页

快速开始
~~~~~~~~~~~~~~~~~~~~~~~~

AgentScope Studio 通过 ``npm`` 安装：

.. code-block:: bash

    npm install -g agentscope-studio


使用以下命令启动 Studio：

.. code-block:: bash

    as_studio

要将应用程序连接到 Studio，请在 ``agentscope.init`` 函数中使用 ``studio_url`` 参数：

.. code-block:: python

    import agentscope

    agentscope.init(studio_url="http://localhost:8000")

    # 应用程序代码
    ...

然后可以在 Studio 中看到该应用程序，如下所示：

.. figure:: ../../_static/images/studio_project.webp
    :width: 100%
    :alt: 项目管理
    :class: bordered-image
    :align: center

    AgentScope Studio 中的项目管理

关于应用程序的详细信息，例如 token 使用情况、模型调用和追踪信息，都可以在 Studio 中查看。

.. figure:: ../../_static/images/studio_run.webp
    :width: 100%
    :alt: AgentScope Studio 运行页面
    :class: bordered-image
    :align: center

    AgentScope Studio 中的应用程序可视化


Friday 智能体
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Friday 是由 AgentScope 构建的实验性本地部署智能体，旨在

- 回答关于 AgentScope 开发的问题，
- 为开发者提供便捷的二次开发环境，
- 集成 AgentScope 中所有可用功能以构建更强大的智能体，以及
- 持续测试和集成 AgentScope 中的高级功能。

.. note:: 我们非常欢迎开源社区贡献并改进 Friday！欢迎在我们的 `GitHub 仓库 <https://github.com/agentscope-ai/agentscope>`_ 上提出问题或拉取请求。

我们正在持续改进 Friday，目前它集成了 AgentScope 中的以下功能：

.. list-table::
    :header-rows: 1

    * - 功能
      - 状态
      - 进一步阅读
      - 描述
    * - 元工具
      - ✅
      - :ref:`tool`
      - 分组工具管理，允许智能体自己更改装备的工具。
    * - 智能体钩子
      - ✅
      - :ref:`hook`
      - 使用钩子将打印消息转发到前端。
    * - 智能体中断
      - ✅
      - :ref:`agent`
      - 允许用户通过后处理中断智能体的回复过程。
    * - 截断提示
      - ✅
      - :ref:`prompt`
      - 支持使用预设的最大 token 限制截断提示。
    * - 状态和会话管理
      - ✅
      - :ref:`state`
      - 智能体的自动状态管理和会话管理，在不同运行之间维护状态。
    * - 长期记忆
      - 🚧
      - :ref:`memory`
      - 支持长期记忆管理。


"""
