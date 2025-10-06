# -*- coding: utf-8 -*-
"""Long-term memory implementation using mem0 library.

This module provides a long-term memory implementation that integrates
with the mem0 library to provide persistent memory storage and retrieval
capabilities for AgentScope agents.
"""
import json
from typing import Any, TYPE_CHECKING
from importlib import metadata
from packaging import version


from pydantic import field_validator

from ..embedding import EmbeddingModelBase
from ._long_term_memory_base import LongTermMemoryBase
from ..message import Msg, TextBlock
from ..model import ChatModelBase
from ..tool import ToolResponse


if TYPE_CHECKING:
    from mem0.configs.base import MemoryConfig
    from mem0.vector_stores.configs import VectorStoreConfig
else:
    MemoryConfig = Any
    VectorStoreConfig = Any


def _create_agentscope_config_classes() -> tuple:
    """Create custom config classes for agentscope providers."""
    from mem0.embeddings.configs import EmbedderConfig
    from mem0.llms.configs import LlmConfig

    class _ASLlmConfig(LlmConfig):
        """Custom LLM config class that updates the validate_config method.

        Attention: in mem0, the validate_config hardcodes the provider, so we
        need to override the validate_config method to support the agentscope
        providers. We will follow up with the mem0 to improve this.
        """

        @field_validator("config")
        @classmethod
        def validate_config(cls, v: Any, values: Any) -> Any:
            """Validate the LLM configuration."""
            from mem0.utils.factory import LlmFactory

            provider = values.data.get("provider")
            if provider in LlmFactory.provider_to_class:
                return v
            raise ValueError(f"Unsupported LLM provider: {provider}")

    class _ASEmbedderConfig(EmbedderConfig):
        """Custom embedder config class that updates the validate_config
        method."""

        @field_validator("config")
        @classmethod
        def validate_config(cls, v: Any, values: Any) -> Any:
            """Validate the embedder configuration."""
            from mem0.utils.factory import EmbedderFactory

            provider = values.data.get("provider")
            if provider in EmbedderFactory.provider_to_class:
                return v
            raise ValueError(f"Unsupported Embedder provider: {provider}")

    return _ASLlmConfig, _ASEmbedderConfig


class Mem0LongTermMemory(LongTermMemoryBase):
    """A class that implements the LongTermMemoryBase interface using mem0."""

    def __init__(
        self,
        agent_name: str | None = None,
        user_name: str | None = None,
        run_name: str | None = None,
        model: ChatModelBase | None = None,
        embedding_model: EmbeddingModelBase | None = None,
        vector_store_config: VectorStoreConfig | None = None,
        mem0_config: MemoryConfig | None = None,
        default_memory_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Mem0LongTermMemory instance

        Args:
            agent_name (`str | None`, optional):
                The name of the agent. Default is None.
            user_name (`str | None`, optional):
                The name of the user. Default is None.
            run_name (`str | None`, optional):
                The name of the run/session. Default is None.

        .. note::
            1. At least one of `agent_name`, `user_name`, or `run_name` is
               required.
            2. During memory recording, these parameters become metadata
               for the stored memories.
            3. During memory retrieval, only memories with matching
               metadata values will be returned.

            model (`ChatModelBase | None`, optional):
                The chat model to use for the long-term memory. If
                mem0_config is provided, this will override the LLM
                configuration. If mem0_config is None, this is required.
            embedding_model (`EmbeddingModelBase | None`, optional):
                The embedding model to use for the long-term memory. If
                mem0_config is provided, this will override the embedder
                configuration. If mem0_config is None, this is required.
            vector_store_config (`VectorStoreConfig | None`, optional):
                The vector store config to use for the long-term memory.
                If mem0_config is provided, this will override the vector store
                configuration. If mem0_config is None and this is not
                provided, defaults to Qdrant with on_disk=True.
            mem0_config (`MemoryConfig | None`, optional):
                The mem0 config to use for the long-term memory.
                If provided, individual
                model/embedding_model/vector_store_config parameters will
                override the corresponding configurations in mem0_config. If
                None, a new MemoryConfig will be created using the provided
                parameters.
            default_memory_type (`str | None`, optional):
                The type of memory to use. Default is None, to create a
                semantic memory.

        Raises:
            `ValueError`:
                If `mem0_config` is None and either `model` or
                `embedding_model` is None.
        """
        super().__init__()

        try:
            import mem0
            from mem0.configs.llms.base import BaseLlmConfig
            from mem0.utils.factory import LlmFactory, EmbedderFactory

            # Check mem0 version
            current_version = metadata.version("mem0ai")
            is_mem0_version_low = version.parse(
                current_version,
            ) <= version.parse("0.1.115")

            # Register the agentscope providers with mem0

            EmbedderFactory.provider_to_class[
                "agentscope"
            ] = "agentscope.memory._mem0_utils.AgentScopeEmbedding"
            if is_mem0_version_low:
                # For mem0 version <= 0.1.115, use the old style
                LlmFactory.provider_to_class[
                    "agentscope"
                ] = "agentscope.memory._mem0_utils.AgentScopeLLM"
            else:
                # For mem0 version > 0.1.115, use the new style
                LlmFactory.provider_to_class["agentscope"] = (
                    "agentscope.memory._mem0_utils.AgentScopeLLM",
                    BaseLlmConfig,
                )

        except ImportError as e:
            raise ImportError(
                "Please install the mem0 library by `pip install mem0ai`",
            ) from e

        # Create the custom config classes for agentscope providers dynamically
        _ASLlmConfig, _ASEmbedderConfig = _create_agentscope_config_classes()

        if agent_name is None and user_name is None and run_name is None:
            raise ValueError(
                "at least one of agent_name, user_name, and run_name is "
                "required",
            )

        # Store agent and user identifiers for memory management
        self.agent_id = agent_name
        self.user_id = user_name
        self.run_id = run_name

        # Configuration logic: Handle mem0_config parameter
        if mem0_config is not None:
            # Case 1: mem0_config is provided - override specific
            # configurations if individual params are given

            # Override LLM configuration if model is provided
            if model is not None:
                mem0_config.llm = _ASLlmConfig(
                    provider="agentscope",
                    config={"model": model},
                )

            # Override embedder configuration if embedding_model is provided
            if embedding_model is not None:
                mem0_config.embedder = _ASEmbedderConfig(
                    provider="agentscope",
                    config={"model": embedding_model},
                )

            # Override vector store configuration if vector_store_config is
            # provided
            if vector_store_config is not None:
                mem0_config.vector_store = vector_store_config

        else:
            # Case 2: mem0_config is not provided - create new configuration
            # from individual parameters

            # Validate that required parameters are provided
            if model is None or embedding_model is None:
                raise ValueError(
                    "model and embedding_model are required if mem0_config "
                    "is not provided",
                )

            # Create new MemoryConfig with provided LLM and embedder
            mem0_config = mem0.configs.base.MemoryConfig(
                llm=_ASLlmConfig(
                    provider="agentscope",
                    config={"model": model},
                ),
                embedder=_ASEmbedderConfig(
                    provider="agentscope",
                    config={"model": embedding_model},
                ),
            )

            # Set vector store configuration
            if vector_store_config is not None:
                # Use provided vector store configuration
                mem0_config.vector_store = vector_store_config
            else:
                # Use default Qdrant configuration with on-disk storage for
                # persistence set on_disk to True to enable persistence,
                # otherwise it will be in memory only
                on_disk = kwargs.get("on_disk", True)
                mem0_config.vector_store = (
                    mem0.vector_stores.configs.VectorStoreConfig(
                        config={"on_disk": on_disk},
                    )
                )

        # Initialize the async memory instance with the configured settings
        self.long_term_working_memory = mem0.AsyncMemory(mem0_config)

        # Store the default memory type for future use
        self.default_memory_type = default_memory_type

    async def record_to_memory(
        self,
        thinking: str,
        content: list[str],
        **kwargs: Any,
    ) -> ToolResponse:
        """Use this function to record important information that you may
        need later. The target content should be specific and concise, e.g.
        who, when, where, do what, why, how, etc.

        Args:
            thinking (`str`):
                Your thinking and reasoning about what to record.
            content (`list[str]`):
                The content to remember, which is a list of strings.
        """
        try:
            if thinking:
                content = [thinking] + content

            results = await self._mem0_record(
                [
                    {
                        "role": "assistant",
                        "content": "\n".join(content),
                        "name": "assistant",
                    },
                ],
                **kwargs,
            )
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"Successfully recorded content to memory "
                        f"{results}",
                    ),
                ],
            )

        except Exception as e:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"Error recording memory: {str(e)}",
                    ),
                ],
            )

    async def retrieve_from_memory(
        self,
        keywords: list[str],
        limit: int = 5,
        **kwargs: Any,
    ) -> ToolResponse:
        """Retrieve the memory based on the given keywords.

        Args:
            keywords (`list[str]`):
                The keywords to search for in the memory, which should be
                specific and concise, e.g. the person's name, the date, the
                location, etc.
            limit (`int`, optional):
                The maximum number of memories to retrieve per search.

        Returns:
            `ToolResponse`:
                A ToolResponse containing the retrieved memories as JSON text.
        """

        try:
            results = []
            for keyword in keywords:
                result = await self.long_term_working_memory.search(
                    query=keyword,
                    agent_id=self.agent_id,
                    user_id=self.user_id,
                    run_id=self.run_id,
                    limit=limit,
                )
                if result:
                    results.extend(
                        [item["memory"] for item in result["results"]],
                    )

            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text="\n".join(results),
                    ),
                ],
            )

        except Exception as e:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"Error retrieving memory: {str(e)}",
                    ),
                ],
            )

    async def record(
        self,
        msgs: list[Msg | None],
        memory_type: str | None = None,
        infer: bool = True,
        **kwargs: Any,
    ) -> None:
        """Record the content to the long-term memory.

        Args:
            msgs (`list[Msg | None]`):
                The messages to record to memory.
            memory_type (`str | None`, optional):
                The type of memory to use. Default is None, to create a
                semantic memory. "procedural_memory" is explicitly used for
                procedural memories.
            infer (`bool`, optional):
                Whether to infer memory from the content. Default is True.
            **kwargs (`Any`):
                Additional keyword arguments for the mem0 recording.
        """
        if isinstance(msgs, Msg):
            msgs = [msgs]

        # Filter out None
        msg_list = [_ for _ in msgs if _]
        if not all(isinstance(_, Msg) for _ in msg_list):
            raise TypeError(
                "The input messages must be a list of Msg objects.",
            )

        messages = [
            {
                "role": "assistant",
                "content": "\n".join([str(_.content) for _ in msg_list]),
                "name": "assistant",
            },
        ]

        await self._mem0_record(
            messages,
            memory_type=memory_type,
            infer=infer,
            **kwargs,
        )

    async def _mem0_record(
        self,
        messages: str | list[dict],
        memory_type: str | None,
        infer: bool = True,
        **kwargs: Any,
    ) -> dict:
        """Record the content to the long-term memory.

        Args:
            messages (`str`):
                The content to remember, which is a string or a list of
                dictionaries representing messages.
            memory_type (`str | None`, optional):
                The type of memory to use. Default is None, to create a
                semantic memory. "procedural_memory" is explicitly used for
                procedural memories.
            infer (`bool`, optional):
                Whether to infer memory from the content. Default is True.
            **kwargs (`Any`):
                Additional keyword arguments.

        Returns:
            `dict`:
                The result from the memory recording operation.
        """
        results = await self.long_term_working_memory.add(
            messages=messages,
            agent_id=self.agent_id,
            user_id=self.user_id,
            run_id=self.run_id,
            memory_type=(
                memory_type
                if memory_type is not None
                else self.default_memory_type
            ),
            infer=infer,
            **kwargs,
        )
        return results

    async def retrieve(
        self,
        msg: Msg | list[Msg] | None,
        limit: int = 5,
        **kwargs: Any,
    ) -> str:
        """Retrieve the content from the long-term memory.

        Args:
            msg (`Msg | list[Msg] | None`):
                The message to search for in the memory, which should be
                specific and concise, e.g. the person's name, the date, the
                location, etc.
            limit (`int`, optional):
                The maximum number of memories to retrieve per search.
            **kwargs (`Any`):
                Additional keyword arguments.

        Returns:
            `str`:
                The retrieved memory
        """
        if isinstance(msg, Msg):
            msg = [msg]

        if not isinstance(msg, list) or not all(
            isinstance(_, Msg) for _ in msg
        ):
            raise TypeError(
                "The input message must be a Msg or a list of Msg objects.",
            )

        msg_strs = [
            json.dumps(_.to_dict()["content"], ensure_ascii=False) for _ in msg
        ]

        results = []
        for item in msg_strs:
            result = await self.long_term_working_memory.search(
                query=item,
                agent_id=self.agent_id,
                user_id=self.user_id,
                run_id=self.run_id,
                limit=limit,
            )
            if result:
                results.extend([item["memory"] for item in result["results"]])

        return "\n".join(results)
