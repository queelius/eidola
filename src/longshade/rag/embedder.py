"""Embedding wrapper for sentence-transformers."""

from typing import Any, List, Optional, Union
import numpy as np

from ..models import Chunk


class Embedder:
    """Wrapper around sentence-transformers for generating embeddings.

    Lazy-loads the model on first use to avoid slow imports.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: Optional[str] = None,
    ):
        """Initialize embedder.

        Args:
            model_name: HuggingFace model name or path
            device: Device to use ("cpu", "cuda", etc.). Auto-detected if None.
        """
        self.model_name = model_name
        self.device = device
        self._model: Optional[Any] = None

    @property
    def model(self) -> Any:
        """Lazy-load the model on first access."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    @property
    def embedding_dim(self) -> int:
        """Dimension of the embeddings."""
        return int(self.model.get_sentence_embedding_dimension())

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts

        Returns:
            Embeddings as numpy array. Shape is (embedding_dim,) for single
            text, (n_texts, embedding_dim) for list.
        """
        if isinstance(texts, str):
            texts = [texts]
            result: np.ndarray = self.model.encode(texts, convert_to_numpy=True)[0]
            return result

        result = np.asarray(self.model.encode(texts, convert_to_numpy=True))
        return result

    def embed_chunks(
        self,
        chunks: List[Chunk],
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> List[Chunk]:
        """Embed a list of chunks in place.

        Args:
            chunks: List of Chunk objects
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            The same chunks with embeddings populated
        """
        if not chunks:
            return chunks

        texts = [c.text for c in chunks]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        return chunks

    def similarity(self, query: str, texts: List[str]) -> np.ndarray:
        """Compute cosine similarity between query and texts.

        Args:
            query: Query text
            texts: List of texts to compare against

        Returns:
            Array of similarity scores
        """
        from sentence_transformers import util

        query_embedding = self.embed(query)
        text_embeddings = self.embed(texts)

        similarities = util.cos_sim(query_embedding, text_embeddings)
        return similarities.numpy().flatten()
