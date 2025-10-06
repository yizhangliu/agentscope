# -*- coding: utf-8 -*-
"""The ollama text embedding model class."""
import asyncio
from datetime import datetime
from typing import List, Any

from ._embedding_response import EmbeddingResponse
from ._embedding_usage import EmbeddingUsage
from ._cache_base import EmbeddingCacheBase
from ..embedding import EmbeddingModelBase


class OllamaTextEmbedding(EmbeddingModelBase):
    """The Ollama embedding model."""

    def __init__(
        self,
        model_name: str,
        host: str | None = None,
        embedding_cache: EmbeddingCacheBase | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Ollama text embedding model class.

        Args:
            model_name (`str`):
                The name of the embedding model.
            host (`str | None`, defaults to `None`):
                The host URL for the Ollama API.
            embedding_cache (`EmbeddingCacheBase | None`, defaults to `None`):
                The embedding cache class instance, used to cache the
                embedding results to avoid repeated API calls.
        """
        import ollama

        super().__init__(model_name)

        self.client = ollama.AsyncClient(host=host, **kwargs)
        self.embedding_cache = embedding_cache

    async def __call__(
        self,
        text: List[str],
        **kwargs: Any,
    ) -> EmbeddingResponse:
        """Call the Ollama embedding API.

        Args:
            text (`List[str]`):
                The input text to be embedded. It can be a list of strings.
        """

        if self.embedding_cache:
            cached_embeddings = await self.embedding_cache.retrieve(
                identifier=kwargs,
            )
            if cached_embeddings:
                return EmbeddingResponse(
                    embeddings=cached_embeddings,
                    usage=EmbeddingUsage(
                        tokens=0,
                        time=0,
                    ),
                    source="cache",
                )

        start_time = datetime.now()
        response = await asyncio.gather(
            *[
                self.client.embeddings(self.model_name, _, **kwargs)
                for _ in text
            ],
        )
        time = (datetime.now() - start_time).total_seconds()

        if self.embedding_cache:
            await self.embedding_cache.store(
                identifier=kwargs,
                embeddings=[_.embedding for _ in response],
            )

        return EmbeddingResponse(
            embeddings=[_.embedding for _ in response],
            usage=EmbeddingUsage(
                time=time,
            ),
        )
