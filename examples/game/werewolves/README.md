# 🐺⚔️👨‍🌾 Nine-Player Werewolves Game

This is a nine-players werewolves game example built using AgentScope, showcasing **multi-agent interactions**,
**role-based gameplay**, and **structured output handling**.
Specifically, this game is consisted of

- three villagers 👨‍🌾,
- three werewolves 🐺,
- one seer 🔮,
- one witch 🧙‍♀️ and
- one hunter 🏹.

## QuickStart

Run the following command to start the game, ensuring you have set up your DashScope API key as an environment variable.

```bash
python main.py
```

> Note:
> - You can adjust the language, model and other parameters in `main.py`.
> - Different models may yield different game experiences.

Running the example with AgentScope Studio provides a more interactive experience.

- Demo Video in Chinese (click to play):

[![Werewolf Game in Chinese](https://img.alicdn.com/imgextra/i3/6000000007235/O1CN011pK6Be23JgcdLWmLX_!!6000000007235-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/KxyR66_CWaWwu76OPTvOV2Ye1Gas3i5p4molJtzhn_s.mp4)

- Demo Video in English (click to play):

[![Werewolf Game in English](https://img.alicdn.com/imgextra/i3/6000000007389/O1CN011alyGK24SDcFBzHea_!!6000000007389-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/bMiRTfxPg2vm76wEoaIP2eJfkCi8CUExHRas-1LyK1I.mp4)

## Details

The game is built with the ``ReActAgent`` in AgentScope, utilizing its ability to generate structured outputs to
control the game flow and interactions.
We also use the ``MsgHub`` and pipelines in AgentScope to manage the complex interactions like discussion and voting.
It's very interesting to see how agents play the werewolf game with different roles and objectives.

Additionally, you can use the ``UserAgent`` to replace one of the agents to play with AI agents!


## Further Reading

- [Structured Output](https://doc.agentscope.io/tutorial/task_agent.html#structured-output)
- [MsgHub and Pipelines](https://doc.agentscope.io/tutorial/task_pipeline.html)
- [Prompt Formatter](https://doc.agentscope.io/tutorial/task_prompt.html)
- [AgentScope Studio](https://doc.agentscope.io/tutorial/task_studio.html)
