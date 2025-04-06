"""
Knowledge Graph module for the Tiered Context Management system.

This module implements the long-term memory component that stores
structured knowledge using a graph-based approach.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class KnowledgeNode(BaseModel):
    """Represents a node in the knowledge graph"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    content: str
    node_type: str  # entity, concept, fact
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class KnowledgeRelation(BaseModel):
    """Represents a relation between nodes in the knowledge graph"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class KnowledgeGraph:
    """
    Implements the long-term memory component using a graph-based approach.

    The KnowledgeGraph is responsible for:
    - Storing structured knowledge as nodes and relations
    - Extracting knowledge from conversations
    - Querying the graph for relevant information
    - Maintaining knowledge consistency and relevance
    """

    def __init__(self, openai_client=None):
        """
        Initialize the knowledge graph.

        Args:
            openai_client: Optional OpenAI client for API access
        """
        self.client = openai_client
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: Dict[str, KnowledgeRelation] = {}
        self.node_relations: Dict[str, List[str]] = {}  # node_id -> list of relation_ids
        self.session_nodes: Dict[str, List[str]] = {}  # session_id -> list of node_ids

    def add_node(self, label: str, content: str, node_type: str, 
                session_id: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a node to the knowledge graph.

        Args:
            label: Label of the node
            content: Content of the node
            node_type: Type of the node (entity, concept, fact)
            session_id: Optional ID of the associated session
            metadata: Additional metadata for the node

        Returns:
            ID of the added node
        """
        # Create node
        node = KnowledgeNode(
            label=label,
            content=content,
            node_type=node_type,
            metadata=metadata or {}
        )

        # Store node
        self.nodes[node.id] = node

        # Add to session nodes if session_id is provided
        if session_id:
            if session_id not in self.session_nodes:
                self.session_nodes[session_id] = []
            self.session_nodes[session_id].append(node.id)

        return node.id

    def add_relation(self, source_id: str, target_id: str, relation_type: str, 
                    weight: float = 1.0,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a relation between nodes.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relation_type: Type of the relation
            weight: Weight of the relation
            metadata: Additional metadata for the relation

        Returns:
            ID of the added relation
        """
        # Check if nodes exist
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node not found")

        # Create relation
        relation = KnowledgeRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            metadata=metadata or {}
        )

        # Store relation
        self.relations[relation.id] = relation

        # Add to node relations
        if source_id not in self.node_relations:
            self.node_relations[source_id] = []
        self.node_relations[source_id].append(relation.id)

        if target_id not in self.node_relations:
            self.node_relations[target_id] = []
        self.node_relations[target_id].append(relation.id)

        return relation.id

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """
        Get a node by ID.

        Args:
            node_id: ID of the node to retrieve

        Returns:
            The node or None if not found
        """
        return self.nodes.get(node_id)

    def get_relation(self, relation_id: str) -> Optional[KnowledgeRelation]:
        """
        Get a relation by ID.

        Args:
            relation_id: ID of the relation to retrieve

        Returns:
            The relation or None if not found
        """
        return self.relations.get(relation_id)

    def get_node_relations(self, node_id: str) -> List[KnowledgeRelation]:
        """
        Get relations for a node.

        Args:
            node_id: ID of the node

        Returns:
            List of relations
        """
        relation_ids = self.node_relations.get(node_id, [])

        relations = []
        for relation_id in relation_ids:
            relation = self.get_relation(relation_id)
            if relation:
                relations.append(relation)

        return relations

    def get_connected_nodes(self, node_id: str, relation_types: Optional[List[str]] = None) -> List[KnowledgeNode]:
        """
        Get nodes connected to a node.

        Args:
            node_id: ID of the node
            relation_types: Optional list of relation types to filter by

        Returns:
            List of connected nodes
        """
        relations = self.get_node_relations(node_id)

        # Filter by relation types if specified
        if relation_types:
            relations = [r for r in relations if r.relation_type in relation_types]

        # Get connected nodes
        connected_nodes = []
        for relation in relations:
            if relation.source_id == node_id:
                connected_node = self.get_node(relation.target_id)
            else:
                connected_node = self.get_node(relation.source_id)

            if connected_node:
                connected_nodes.append(connected_node)

        return connected_nodes

    def search_nodes(self, query: str, node_types: Optional[List[str]] = None, 
                   limit: int = 10) -> List[KnowledgeNode]:
        """
        Search for nodes matching the query.

        Args:
            query: Query to match against nodes
            node_types: Optional list of node types to filter by
            limit: Maximum number of nodes to return

        Returns:
            List of matching nodes
        """
        # In a real implementation, this would use more sophisticated
        # techniques to search for nodes

        # Simple search
        query_lower = query.lower()
        matching_nodes = []

        for node in self.nodes.values():
            # Filter by node type if specified
            if node_types and node.node_type not in node_types:
                continue

            # Check if query matches label or content
            if query_lower in node.label.lower() or query_lower in node.content.lower():
                matching_nodes.append(node)

        # Sort by relevance (simple implementation)
        matching_nodes.sort(key=lambda n: n.label.lower().count(query_lower) + n.content.lower().count(query_lower), reverse=True)

        # Apply limit
        return matching_nodes[:limit]

    async def extract_knowledge(self, content: str, session_id: Optional[str] = None) -> List[str]:
        """
        Extract knowledge from content and add to the graph.

        Args:
            content: Content to extract knowledge from
            session_id: Optional ID of the associated session

        Returns:
            List of added node IDs
        """
        # In a real implementation, this would use the OpenAI client
        # to extract entities, concepts, and facts from the content

        # Simulate knowledge extraction
        # This is a placeholder implementation
        added_nodes = []

        # Extract a simple fact
        if len(content) > 20:
            fact_node_id = self.add_node(
                label=f"Fact from session {session_id}",
                content=f"Extracted fact: {content[:50]}...",
                node_type="fact",
                session_id=session_id
            )
            added_nodes.append(fact_node_id)

        return added_nodes

    def get_session_knowledge(self, session_id: str) -> List[KnowledgeNode]:
        """
        Get knowledge nodes for a session.

        Args:
            session_id: ID of the session

        Returns:
            List of knowledge nodes
        """
        node_ids = self.session_nodes.get(session_id, [])

        nodes = []
        for node_id in node_ids:
            node = self.get_node(node_id)
            if node:
                nodes.append(node)

        return nodes

    def clear_session(self, session_id: str) -> None:
        """
        Clear all knowledge nodes for a session.

        Args:
            session_id: ID of the session to clear
        """
        # Get node IDs for the session
        node_ids = self.session_nodes.get(session_id, [])

        # Remove nodes and their relations
        for node_id in node_ids:
            self._remove_node(node_id)

        # Clear session nodes
        self.session_nodes[session_id] = []

    def _remove_node(self, node_id: str) -> None:
        """
        Remove a node and its relations.

        Args:
            node_id: ID of the node to remove
        """
        if node_id in self.nodes:
            # Get relations for the node
            relation_ids = self.node_relations.get(node_id, [])

            # Remove relations
            for relation_id in relation_ids:
                if relation_id in self.relations:
                    relation = self.relations[relation_id]

                    # Remove from node relations
                    other_node_id = relation.target_id if relation.source_id == node_id else relation.source_id
                    if other_node_id in self.node_relations and relation_id in self.node_relations[other_node_id]:
                        self.node_relations[other_node_id].remove(relation_id)

                    # Remove relation
                    del self.relations[relation_id]

            # Remove from node relations
            if node_id in self.node_relations:
                del self.node_relations[node_id]

            # Remove node
            del self.nodes[node_id]
