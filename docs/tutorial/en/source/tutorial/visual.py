# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: sphinx
#       format_version: '1.1'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

"""
.. _visual-interface:

Visual Interface
=========================

AgentScope supports various visual interfaces for better user experience,
including Gradio and AgentScope Studio.

Gradio
~~~~~~~~~~~~~~~~~~~~~~

First ensure you have installed the full version of AgentScope, which
includes the Gradio package.

.. code-block:: bash

    # From pypi
    pip install agentscope[full]

    # From source code
    cd agentscope
    pip install .[full]


After that, ensure your application is wrapped by a `main` function.

.. code-block:: python

    from agentscope.agents import DialogAgent, UserAgent
    import agentscope


    def main():
        # Your code here
        agentscope.init(model_configs={
            "config_name": "my-qwen-max",
            "model_type": "dashscope_chat",
            "model_name": "qwen-max"
        })

        agent = DialogAgent(
            name="Alice,
            model_config_name="my-qwen-max",
            sys_prompt="You're a helpful assistant named Alice."
        )
        user = UserAgent(agent)

        msg = None
        while True:
            msg = agent(msg)
            msg = user(msg)
            if msg.content == "exit":
                break


Then execute the following command in the terminal to start the Gradio UI:

.. code-block :: bash

    as_gradio {path_to_your_python_code}

Finally, you can visit the Gradio UI as follows:

.. image:: https://img.alicdn.com/imgextra/i1/O1CN0181KSfH1oNbfzjUAVT_!!6000000005213-0-tps-3022-1530.jpg
   :align: center
   :class: bordered-image

------------------------------

AgentScope Studio
~~~~~~~~~~~~~~~~~~

AgentScope Studio is an open sourced Web UI toolkit for building and
monitoring multi-agent applications. It provides the following features:

* **Dashboard**: A user-friendly interface, where you can monitor your running applications, and look through the running histories.

* **Workstation**: A powerful interface to build your multi-agent applications with Dragging & Dropping.

* **Server Manager**: An easy-to-use monitoring and management tool for managing large-scale distributed applications.

* **Gallery**: Fruitful applications and demos in Workstation. (Coming soon!)

For details about Workstation and Gallery, please refer to :ref:`Low-code
Developments <low-code>`.
For details about Server Manager, please refer to :ref:`Distribution
<distribution>`.


.. _studio:

Start AgentScope Studio
----------------------------

To start a studio, first ensure you have installed the latest version of
AgentScope. Then, you can simply run the following Python code:

.. code-block:: python

    import agentscope
    agentscope.studio.init()

Or you can run the following command in the terminal:

.. code-block :: python

    as_studio

After that, you can visit AgentScope studio at http://127.0.0.1:5000, and
the following page will be displayed:

.. image:: https://img.alicdn.com/imgextra/i3/O1CN01Xic0GQ1ZkJ4M0iD8F_!!6000000003232-0-tps-3452-1610.jpg
   :align: center
   :class: bordered-image

Of course, you can change the host and port, and link to your application
running histories by providing the following arguments:

.. code-block:: python

    import agentscope

    agentscope.studio.init(
        host="127.0.0.1",          # The IP address of AgentScope studio
        port=5000,                 # The port number of AgentScope studio
        run_dirs = [               # The directories of your running histories
            "xxx/xxx/runs",
            "xxx/xxx/runs"
        ]
    )


Dashboard
-----------------

Dashboard is a web interface to monitor your running applications and look
through the running histories.


Note
^^^^^^^^^^^^^^^^^^^^^

Currently, Dashboard has the following limitations, and we are working on
improving it. Any feedback, contribution, or suggestion are welcome!

* The running application and AgentScope Studio must be running on the same
machine for ``URL/path consistency``. If you want to visit AgentScope in the
other machine, you can try to forward the port to the remote machine by
running the following command in the remote machine:

.. code-block :: bash

    # Supposing AgentScope is running on {as_host}:{as_port}, and the port
    # of the remote machine is {remote_machine_port}
    ssh -L {remote_machine_port}:{as_host}:{as_port} [{user_name}@]{as_host}

* For distributed applications, the single-machine & multiprocess mode is
supported, but the multi-machine multiprocess mode is not supported yet.

Register Running Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After starting the AgentScope Studio, you can register your running
applications by specifying ``studio_url`` in ``agentscope.init()``:

.. code-block:: python

    import agentscope

    agentscope.init(
        # ...
        project="xxx",
        name="xxx",
        studio_url="http://127.0.0.1:5000"    # The URL of AgentScope Studio
    )

After registering, you can view the running application in the Dashboard. To
distinguish different applications, you can specify the project and name of
the application.

.. image:: https://img.alicdn.com/imgextra/i2/O1CN01zcUmuJ1I3OUXy1Q35_!!6000000000837-0-tps-3426-1718.jpg
   :align: center
   :class: bordered-image

Click the program with status ``waiting`` to enter the execution
interface. For example, the following picture show a conversation interface.

.. image:: https://img.alicdn.com/imgextra/i3/O1CN01sA3VUc1h7OLKVLfr3_!!6000000004230-0-tps-3448-1736.jpg
   :align: center
   :class: bordered-image


.. note:: Once you register the running application, the input operation
 within the ``agentscope.agents.UserAgent`` class will be transferred to the
 Dashboard in AgentScope Studio, and you can enter the input in the Dashboard.

Import Running Histories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In AgentScope, the running histories are saved in the ``./runs directory`` by
default. If you want to watch these running histories in the Dashboard, you
can specify the ``run_dirs`` in ``agentscope.studio.init()``:


.. code-block:: python

    import agentscope

    agentscope.studio.init(
        run_dirs = ["xxx/runs"]
    )

"""
