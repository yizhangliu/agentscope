# MultiAgent Conversation

This example demonstrates how to build a multi-agent conversation workflow using ``MsgHub`` in AgentScope,
where multiple agents broadcast messages to each other in a shared conversation space.

## Setup

The example is built upon the DashScope LLM API in [main.py](https://github.com/agentscope-ai/agentscope/blob/main/examples/workflows/multiagent_conversation/main.py). You can switch to other LLMs by modifying the ``model`` and ``formatter`` parameters in the code.

To run the example, first install the latest version of AgentScope, then run:

```bash
python examples/workflows/multiagent_conversation/main.py
```

## Main Workflow

- Create multiple participant agents with different attributes (e.g., Alice, Bob, Charlie).
- Agents introduce themselves and interact in the message hub.
- Supports dynamic addition and removal of agents, as well as broadcasting messages.
