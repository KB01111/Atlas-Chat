"""
Graphiti Integration for OpenRouter in AtlasChat
Ensures compatibility between OpenRouter and Graphiti knowledge graph system
"""

import logging
from typing import Dict, Any, List, Optional
from app.core.models.openrouter_models import GraphitiNode, GraphitiRelationship, GraphitiEpisode
from pydantic import BaseModel, Field
import json
import asyncio

logger = logging.getLogger(__name__)

class OpenRouterGraphitiIntegration:
    """
    Integration between OpenRouter and Graphiti knowledge graph system
    Enables episodic memory and knowledge graph capabilities for OpenRouter agents
    """
    
    def __init__(self, graphiti_client=None):
        """
        Initialize the integration
        
        Args:
            graphiti_client: Client for interacting with Graphiti (injected dependency)
        """
        self.graphiti_client = graphiti_client
        
    async def add_conversation_to_graphiti(self, 
                                         conversation_id: str,
                                         messages: List[Dict[str, Any]],
                                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a conversation to Graphiti as an episode
        
        Args:
            conversation_id: ID of the conversation
            messages: List of messages in the conversation
            metadata: Additional metadata for the episode
            
        Returns:
            ID of the created episode
        """
        try:
            if not self.graphiti_client:
                logger.warning("Graphiti client not initialized, skipping add_conversation_to_graphiti")
                return "graphiti_not_initialized"
                
            # Create episode content from messages
            content = self._format_messages_for_episode(messages)
            
            # Create episode
            episode = GraphitiEpisode(
                id=f"conversation:{conversation_id}",
                timestamp=int(asyncio.get_event_loop().time()),
                content=content,
                metadata=metadata or {}
            )
            
            # Convert episode to nodes and relationships
            graph_data = episode.to_nodes_and_relationships()
            
            # Add to Graphiti
            episode_id = await self.graphiti_client.add_episode(episode.dict())
            
            # Add nodes and relationships
            await self.graphiti_client.add_nodes(graph_data["nodes"])
            await self.graphiti_client.add_relationships(graph_data["relationships"])
            
            logger.info(f"Added conversation {conversation_id} to Graphiti as episode {episode_id}")
            return episode_id
            
        except Exception as e:
            logger.error(f"Error adding conversation to Graphiti: {str(e)}")
            return f"error:{str(e)}"
            
    async def search_graphiti_for_context(self,
                                        query: str,
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search Graphiti for relevant context based on a query
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of relevant episodes or nodes
        """
        try:
            if not self.graphiti_client:
                logger.warning("Graphiti client not initialized, skipping search_graphiti_for_context")
                return []
                
            # Search Graphiti
            results = await self.graphiti_client.search(query, limit=limit)
            
            # Format results
            formatted_results = []
            for result in results:
                if "content" in result:
                    # This is an episode
                    formatted_results.append({
                        "type": "episode",
                        "id": result.get("id", ""),
                        "content": result.get("content", ""),
                        "timestamp": result.get("timestamp", 0),
                        "relevance": result.get("relevance", 0.0)
                    })
                else:
                    # This is a node
                    formatted_results.append({
                        "type": "node",
                        "id": result.get("id", ""),
                        "label": result.get("label", ""),
                        "properties": result.get("properties", {}),
                        "relevance": result.get("relevance", 0.0)
                    })
                    
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching Graphiti for context: {str(e)}")
            return []
            
    def _format_messages_for_episode(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format messages for storage in an episode
        
        Args:
            messages: List of messages
            
        Returns:
            Formatted content string
        """
        content = "Conversation:\n\n"
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content_text = msg.get("content", "")
            
            if role == "system":
                content += f"System: {content_text}\n\n"
            elif role == "user":
                content += f"User: {content_text}\n\n"
            elif role == "assistant":
                content += f"Assistant: {content_text}\n\n"
            elif role == "tool":
                content += f"Tool: {content_text}\n\n"
            else:
                content += f"{role.capitalize()}: {content_text}\n\n"
                
        return content
        
    async def enhance_messages_with_graphiti_context(self,
                                                  messages: List[Dict[str, Any]],
                                                  query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Enhance messages with relevant context from Graphiti
        
        Args:
            messages: List of messages
            query: Optional search query (if None, will use the last user message)
            
        Returns:
            Enhanced messages with Graphiti context
        """
        try:
            if not self.graphiti_client:
                logger.warning("Graphiti client not initialized, skipping enhance_messages_with_graphiti_context")
                return messages
                
            # If no query provided, use the last user message
            if not query:
                user_messages = [m for m in messages if m.get("role") == "user"]
                if not user_messages:
                    return messages
                query = user_messages[-1].get("content", "")
                
            # Search Graphiti
            results = await self.search_graphiti_for_context(query)
            
            if not results:
                return messages
                
            # Format context
            context = "Relevant context from previous conversations:\n\n"
            for i, result in enumerate(results):
                if result["type"] == "episode":
                    context += f"{i+1}. {result['content']}\n\n"
                else:
                    context += f"{i+1}. {result['label']}: {json.dumps(result['properties'])}\n\n"
                    
            # Find system message or create one
            system_msg_idx = next((i for i, m in enumerate(messages) if m.get("role") == "system"), None)
            
            if system_msg_idx is not None:
                # Append context to existing system message
                messages[system_msg_idx]["content"] += f"\n\n{context}"
            else:
                # Create new system message with context
                messages.insert(0, {
                    "role": "system",
                    "content": f"Use the following context from previous conversations to inform your responses:\n\n{context}"
                })
                
            return messages
            
        except Exception as e:
            logger.error(f"Error enhancing messages with Graphiti context: {str(e)}")
            return messages
