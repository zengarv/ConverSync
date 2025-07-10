"""
Conversation Memory Service using LangChain's ConversationBufferMemory.
Manages conversation history and context for chat sessions.
"""

from typing import Dict, Optional, List, Any
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from datetime import datetime
import json


class ConversationMemoryService:
    """
    Service to manage conversation memory for chat sessions using LangChain.
    Each session maintains its own conversation buffer memory.
    """
    
    def __init__(self):
        """Initialize the conversation memory service."""
        # Dictionary to store memory for each session
        self._session_memories: Dict[str, ConversationBufferMemory] = {}
        self._session_metadata: Dict[str, Dict[str, Any]] = {}
    
    def create_session_memory(self, session_id: str, transcript: str = None) -> ConversationBufferMemory:
        """
        Create a new conversation memory for a session.
        
        Args:
            session_id (str): Unique session identifier
            transcript (str, optional): Meeting transcript to use as context
            
        Returns:
            ConversationBufferMemory: The created memory instance
        """
        # Create new memory with return_messages=True to get structured messages
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            human_prefix="User",
            ai_prefix="Assistant"
        )
        
        # Store the memory
        self._session_memories[session_id] = memory
        
        # Store metadata
        self._session_metadata[session_id] = {
            'created_at': datetime.now().isoformat(),
            'transcript': transcript,
            'message_count': 0
        }
        
        # If there's a transcript, add it as system context
        if transcript:
            system_context = f"""You are a helpful AI assistant for a meeting analysis system. 
You have access to the following meeting transcript for reference:

MEETING TRANSCRIPT:
{transcript}

You can answer questions about this meeting, provide summaries, extract key points, 
or have general conversations. Always be helpful and provide detailed responses when 
discussing meeting content."""
            
            # Add initial system context as an AI message
            memory.chat_memory.add_ai_message(system_context)
        
        print(f"✅ Created conversation memory for session: {session_id}")
        if transcript:
            print(f"📝 Added transcript context ({len(transcript)} characters)")
        
        return memory
    
    def get_session_memory(self, session_id: str) -> Optional[ConversationBufferMemory]:
        """
        Get the conversation memory for a session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            ConversationBufferMemory or None: The memory instance if exists
        """
        return self._session_memories.get(session_id)
    
    def add_message_pair(self, session_id: str, human_message: str, ai_message: str) -> bool:
        """
        Add a human-AI message pair to the conversation memory.
        
        Args:
            session_id (str): Session identifier
            human_message (str): Human/user message
            ai_message (str): AI response message
            
        Returns:
            bool: True if added successfully, False if session not found
        """
        memory = self.get_session_memory(session_id)
        if not memory:
            print(f"❌ Session {session_id} not found in memory")
            return False
        
        # Add messages to memory
        memory.chat_memory.add_user_message(human_message)
        memory.chat_memory.add_ai_message(ai_message)
        
        # Update metadata
        if session_id in self._session_metadata:
            self._session_metadata[session_id]['message_count'] += 1
        
        print(f"💬 Added message pair to session {session_id}")
        return True
    
    def get_conversation_context(self, session_id: str, include_transcript: bool = True) -> str:
        """
        Get the full conversation context as a formatted string.
        
        Args:
            session_id (str): Session identifier
            include_transcript (bool): Whether to include transcript context
            
        Returns:
            str: Formatted conversation context
        """
        memory = self.get_session_memory(session_id)
        if not memory:
            return ""
        
        # Get the conversation buffer
        conversation_buffer = memory.buffer
        
        # Add transcript context if requested and available
        context_parts = []
        
        if include_transcript and session_id in self._session_metadata:
            transcript = self._session_metadata[session_id].get('transcript')
            if transcript:
                context_parts.append(f"MEETING TRANSCRIPT:\n{transcript}\n")
        
        if conversation_buffer:
            context_parts.append(f"CONVERSATION HISTORY:\n{conversation_buffer}")
        
        return "\n".join(context_parts)
    
    def get_conversation_messages(self, session_id: str) -> List[BaseMessage]:
        """
        Get the conversation messages as a list of BaseMessage objects.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            List[BaseMessage]: List of conversation messages
        """
        memory = self.get_session_memory(session_id)
        if not memory:
            return []
        
        return memory.chat_memory.messages
    
    def clear_session_memory(self, session_id: str) -> bool:
        """
        Clear the conversation memory for a session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            bool: True if cleared successfully, False if session not found
        """
        if session_id in self._session_memories:
            self._session_memories[session_id].clear()
            print(f"🧹 Cleared memory for session: {session_id}")
            return True
        return False
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session completely from memory.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            bool: True if removed successfully, False if session not found
        """
        removed = False
        if session_id in self._session_memories:
            del self._session_memories[session_id]
            removed = True
        
        if session_id in self._session_metadata:
            del self._session_metadata[session_id]
            removed = True
        
        if removed:
            print(f"🗑️ Removed session: {session_id}")
        
        return removed
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            Dict[str, Any] or None: Session information if exists
        """
        if session_id not in self._session_memories:
            return None
        
        memory = self._session_memories[session_id]
        metadata = self._session_metadata.get(session_id, {})
        
        return {
            'session_id': session_id,
            'created_at': metadata.get('created_at'),
            'message_count': metadata.get('message_count', 0),
            'has_transcript': bool(metadata.get('transcript')),
            'transcript_length': len(metadata.get('transcript', '')),
            'memory_buffer_length': len(memory.buffer) if memory.buffer else 0,
            'total_messages': len(memory.chat_memory.messages)
        }
    
    def get_all_sessions_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all active sessions.
        
        Returns:
            Dict[str, Dict[str, Any]]: Information for all sessions
        """
        return {
            session_id: self.get_session_info(session_id) 
            for session_id in self._session_memories.keys()
        }
    
    def get_memory_usage_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            Dict[str, Any]: Usage statistics
        """
        total_sessions = len(self._session_memories)
        total_messages = sum(
            len(memory.chat_memory.messages) 
            for memory in self._session_memories.values()
        )
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'average_messages_per_session': total_messages / total_sessions if total_sessions > 0 else 0,
            'active_session_ids': list(self._session_memories.keys())
        }
