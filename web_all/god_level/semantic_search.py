"""
Tier 1, Feature 3: Semantic Search Engine

Vector embeddings for all cloned content, semantic search, 
and knowledge graph building.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import hashlib


@dataclass
class SearchResult:
    """A search result item."""
    content_id: str
    text: str
    url: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraphNode:
    """Node in a knowledge graph."""
    id: str
    content: str
    node_type: str
    connections: List[str] = field(default_factory=list)


class SemanticSearchEngine:
    """
    Semantic Search Engine with Vector Embeddings
    
    Provides:
    - Vector embeddings for content
    - Semantic search across cloned sites
    - Similar content detection
    - Knowledge graph construction
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model = embedding_model
        self.index = {}
        self.vectors = {}
        self.knowledge_graph: Dict[str, KnowledgeGraphNode] = {}
        
    async def initialize(self) -> bool:
        """Initialize the semantic search engine."""
        await asyncio.sleep(0.1)
        return True
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create vector embedding for text."""
        # Simulated embedding - in production use sentence-transformers
        hash_val = hashlib.md5(text.encode()).hexdigest()
        return [float(ord(c)) for c in hash_val[:32]]
    
    async def index_content(self, content_id: str, text: str, 
                           url: str, metadata: Dict = None) -> bool:
        """Index content for semantic search."""
        embedding = await self.create_embedding(text)
        
        self.index[content_id] = {
            "text": text,
            "url": url,
            "metadata": metadata or {},
            "embedding": embedding
        }
        
        return True
    
    async def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Perform semantic search."""
        query_embedding = await self.create_embedding(query)
        
        results = []
        for content_id, data in self.index.items():
            # Simplified similarity calculation
            similarity = sum(a * b for a, b in zip(query_embedding, data["embedding"]))
            
            results.append(SearchResult(
                content_id=content_id,
                text=data["text"][:500],
                url=data["url"],
                similarity_score=similarity / 1000000
            ))
        
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
    
    async def find_similar_content(self, content_id: str, 
                                   top_k: int = 5) -> List[SearchResult]:
        """Find content similar to indexed content."""
        if content_id not in self.index:
            return []
        
        source = self.index[content_id]
        results = []
        
        for cid, data in self.index.items():
            if cid == content_id:
                continue
                
            similarity = sum(a * b for a, b in zip(source["embedding"], data["embedding"]))
            
            results.append(SearchResult(
                content_id=cid,
                text=data["text"][:500],
                url=data["url"],
                similarity_score=similarity / 1000000
            ))
        
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
    
    async def build_knowledge_graph(self, content_ids: List[str] = None) -> Dict[str, KnowledgeGraphNode]:
        """Build knowledge graph from indexed content."""
        ids_to_process = content_ids or list(self.index.keys())
        
        for content_id in ids_to_process:
            if content_id not in self.index:
                continue
                
            data = self.index[content_id]
            node = KnowledgeGraphNode(
                id=content_id,
                content=data["text"][:1000],
                node_type="document"
            )
            
            # Find connections
            similar = await self.find_similar_content(content_id, top_k=3)
            node.connections = [s.content_id for s in similar]
            
            self.knowledge_graph[content_id] = node
        
        return self.knowledge_graph
    
    async def query_knowledge_graph(self, query: str) -> Dict[str, Any]:
        """Query the knowledge graph."""
        results = await self.search(query, top_k=5)
        
        graph_subset = {
            r.content_id: self.knowledge_graph.get(r.content_id)
            for r in results
            if r.content_id in self.knowledge_graph
        }
        
        return {
            "results": results,
            "graph_nodes": graph_subset
        }
