"""FAISS index management for RAG."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np

from ..models import Chunk, Conversation
from .embedder import Embedder


class RAGIndex:
    """FAISS-based vector index for RAG retrieval.

    Manages:
    - FAISS index (index.faiss)
    - Chunk metadata (chunks.jsonl)
    - Index metadata (metadata.json)
    """

    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        embedding_dim: Optional[int] = None,
    ):
        """Initialize RAG index.

        Args:
            embedder: Embedder to use for queries. If None, uses default.
            embedding_dim: Dimension of embeddings. Auto-detected from embedder.
        """
        self.embedder = embedder or Embedder()
        self._embedding_dim = embedding_dim or self.embedder.embedding_dim
        self._index = None
        self._chunks: List[Chunk] = []
        self._conversations: Dict[str, Conversation] = {}
        self._metadata: Dict[str, Any] = {}

    @property
    def index(self) -> Any:
        """Lazy-initialize FAISS index."""
        if self._index is None:
            import faiss

            self._index = faiss.IndexFlatIP(self._embedding_dim)  # Inner product
        return self._index

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to the index.

        Chunks should already have embeddings populated.
        """
        if not chunks:
            return

        # Normalize embeddings for cosine similarity via inner product
        embeddings = np.array([c.embedding for c in chunks if c.embedding is not None])

        if len(embeddings) == 0:
            return

        # Normalize to unit vectors
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / norms

        self.index.add(normalized.astype(np.float32))
        self._chunks.extend(chunks)

    def add_conversations(self, conversations: List[Conversation]) -> None:
        """Store conversations for context expansion.

        Call this after adding chunks to enable retrieval of full context.
        """
        for conv in conversations:
            self._conversations[conv.id] = conv

    def search(
        self,
        query: str,
        k: int = 10,
        expand_context: bool = True,
        context_turns: int = 3,
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks.

        Args:
            query: Query text
            k: Number of results to return
            expand_context: Whether to expand conversation context
            context_turns: Number of turns before/after to include

        Returns:
            List of results with chunk, score, and optional context
        """
        # Embed query
        query_embedding = self.embedder.embed(query)

        # Normalize
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm

        # Search
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        scores, indices = self.index.search(query_embedding, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._chunks):
                continue

            chunk = self._chunks[idx]
            result: Dict[str, Any] = {
                "chunk": chunk,
                "score": float(score),
            }

            # Expand context for conversation chunks
            if expand_context and chunk.source == "conversation":
                context = self._expand_context(chunk, context_turns)
                if context:
                    result["context"] = context

            results.append(result)

        return results

    def _expand_context(
        self, chunk: Chunk, context_turns: int
    ) -> Optional[List[Dict[str, str]]]:
        """Expand conversation context around a chunk.

        Returns the surrounding messages in the conversation.
        """
        if not chunk.conversation_id:
            return None

        conv = self._conversations.get(chunk.conversation_id)
        if not conv:
            return None

        # Find the message index
        msg_index = chunk.metadata.get("message_index", 0)

        # Calculate range
        start = max(0, msg_index - context_turns)
        end = min(len(conv.messages), msg_index + context_turns + 1)

        context = []
        for i in range(start, end):
            msg = conv.messages[i]
            context.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                    "is_match": i == msg_index,
                }
            )

        return context

    def save(self, path: Path) -> None:
        """Save index to disk.

        Creates:
        - index.faiss: FAISS vector index
        - chunks.jsonl: Chunk data with embeddings
        - metadata.json: Index metadata
        """
        import faiss

        path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, str(path / "index.faiss"))

        # Save chunks
        with open(path / "chunks.jsonl", "w", encoding="utf-8") as f:
            for chunk in self._chunks:
                data = {
                    "id": chunk.id,
                    "text": chunk.text,
                    "source": chunk.source,
                    "embedding": (
                        chunk.embedding.tolist()
                        if chunk.embedding is not None
                        else None
                    ),
                    "metadata": chunk.metadata,
                    "conversation_id": chunk.conversation_id,
                    "turn_index": chunk.turn_index,
                    "total_turns": chunk.total_turns,
                    "timestamp": (
                        chunk.timestamp.isoformat() if chunk.timestamp else None
                    ),
                }
                f.write(json.dumps(data) + "\n")

        # Save metadata
        metadata = {
            "version": "1.0",
            "embedding_model": self.embedder.model_name,
            "embedding_dim": self._embedding_dim,
            "total_chunks": len(self._chunks),
            "conversations": {
                conv_id: {
                    "title": conv.title,
                    "turns": conv.turn_count,
                    "source": conv.source,
                }
                for conv_id, conv in self._conversations.items()
            },
            "expansion": {
                "default_context_turns": 3,
                "max_context_turns": 10,
                "include_full_if_under": 20,
            },
            "created": datetime.now().isoformat(),
        }

        with open(path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load(cls, path: Path, embedder: Optional[Embedder] = None) -> "RAGIndex":
        """Load index from disk.

        Args:
            path: Path to index directory
            embedder: Optional embedder to use for queries

        Returns:
            Loaded RAGIndex
        """
        import faiss

        # Load metadata first
        with open(path / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Create embedder if not provided
        if embedder is None:
            model_name = metadata.get(
                "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
            )
            embedder = Embedder(model_name)

        # Create index
        index = cls(
            embedder=embedder,
            embedding_dim=metadata.get("embedding_dim"),
        )
        index._metadata = metadata

        # Load FAISS index
        index._index = faiss.read_index(str(path / "index.faiss"))

        # Load chunks
        with open(path / "chunks.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                chunk = Chunk(
                    id=data["id"],
                    text=data["text"],
                    source=data["source"],
                    embedding=(
                        np.array(data["embedding"]) if data["embedding"] else None
                    ),
                    metadata=data.get("metadata", {}),
                    conversation_id=data.get("conversation_id"),
                    turn_index=data.get("turn_index"),
                    total_turns=data.get("total_turns"),
                    timestamp=(
                        datetime.fromisoformat(data["timestamp"])
                        if data.get("timestamp")
                        else None
                    ),
                )
                index._chunks.append(chunk)

        return index

    def __len__(self) -> int:
        return len(self._chunks)
