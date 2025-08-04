"""
Real-time Collaborative Editing Service
WebSocket-based collaborative editing with operational transforms
"""
import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import redis
from fastapi import WebSocket, WebSocketDisconnect
import hashlib

logger = logging.getLogger(__name__)

class OperationType(Enum):
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    REPLACE = "replace"

@dataclass
class Operation:
    type: OperationType
    position: int
    content: str = ""
    length: int = 0
    author: str = ""
    timestamp: float = 0

@dataclass
class Cursor:
    user_id: str
    position: int
    selection_start: int
    selection_end: int
    color: str

@dataclass
class CollaborationState:
    document_id: str
    content: str
    version: int
    operations: List[Operation]
    cursors: Dict[str, Cursor]
    participants: Set[str]
    last_modified: datetime

class CollaborationManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.connections: Dict[str, Dict[str, WebSocket]] = {}  # document_id -> {user_id: websocket}
        self.documents: Dict[str, CollaborationState] = {}
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.operation_queue: Dict[str, List[Operation]] = {}
        self.user_colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
        ]
        self.user_color_index = 0
    
    async def connect_user(self, document_id: str, user_id: str, websocket: WebSocket):
        """Connect a user to a collaborative document"""
        try:
            await websocket.accept()
            
            # Initialize document if not exists
            if document_id not in self.documents:
                await self._initialize_document(document_id)
            
            # Add connection
            if document_id not in self.connections:
                self.connections[document_id] = {}
            self.connections[document_id][user_id] = websocket
            
            # Add participant
            self.documents[document_id].participants.add(user_id)
            
            # Assign user color
            user_color = self.user_colors[self.user_color_index % len(self.user_colors)]
            self.user_color_index += 1
            
            # Create initial cursor
            cursor = Cursor(
                user_id=user_id,
                position=0,
                selection_start=0,
                selection_end=0,
                color=user_color
            )
            self.documents[document_id].cursors[user_id] = cursor
            
            # Send initial state to new user
            await self._send_initial_state(document_id, user_id)
            
            # Notify other users of new participant
            await self._broadcast_participant_update(document_id, user_id, "joined")
            
            logger.info(f"User {user_id} connected to document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect user {user_id} to document {document_id}: {e}")
            raise
    
    async def disconnect_user(self, document_id: str, user_id: str):
        """Disconnect a user from a collaborative document"""
        try:
            if document_id in self.connections and user_id in self.connections[document_id]:
                del self.connections[document_id][user_id]
            
            if document_id in self.documents:
                self.documents[document_id].participants.discard(user_id)
                if user_id in self.documents[document_id].cursors:
                    del self.documents[document_id].cursors[user_id]
                
                # Notify other users
                await self._broadcast_participant_update(document_id, user_id, "left")
                
                # Clean up empty documents
                if not self.documents[document_id].participants:
                    await self._cleanup_document(document_id)
            
            logger.info(f"User {user_id} disconnected from document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to disconnect user {user_id} from document {document_id}: {e}")
    
    async def handle_operation(self, document_id: str, user_id: str, operation_data: Dict[str, Any]):
        """Handle incoming operation from a user"""
        try:
            if document_id not in self.documents:
                logger.error(f"Document {document_id} not found")
                return
            
            # Parse operation
            operation = Operation(
                type=OperationType(operation_data["type"]),
                position=operation_data["position"],
                content=operation_data.get("content", ""),
                length=operation_data.get("length", 0),
                author=user_id,
                timestamp=datetime.now().timestamp()
            )
            
            # Apply operational transform
            transformed_op = await self._transform_operation(document_id, operation)
            
            # Apply operation to document
            await self._apply_operation(document_id, transformed_op)
            
            # Broadcast to other users
            await self._broadcast_operation(document_id, user_id, transformed_op)
            
            # Persist changes
            await self._persist_document(document_id)
            
        except Exception as e:
            logger.error(f"Failed to handle operation for document {document_id}: {e}")
    
    async def handle_cursor_update(self, document_id: str, user_id: str, cursor_data: Dict[str, Any]):
        """Handle cursor position update"""
        try:
            if document_id not in self.documents:
                return
            
            # Update cursor
            if user_id in self.documents[document_id].cursors:
                cursor = self.documents[document_id].cursors[user_id]
                cursor.position = cursor_data.get("position", cursor.position)
                cursor.selection_start = cursor_data.get("selection_start", cursor.selection_start)
                cursor.selection_end = cursor_data.get("selection_end", cursor.selection_end)
                
                # Broadcast cursor update
                await self._broadcast_cursor_update(document_id, user_id, cursor)
            
        except Exception as e:
            logger.error(f"Failed to handle cursor update for document {document_id}: {e}")
    
    async def _initialize_document(self, document_id: str):
        """Initialize a new collaborative document"""
        try:
            # Try to load from Redis first
            stored_state = await self._load_document_from_redis(document_id)
            
            if stored_state:
                self.documents[document_id] = stored_state
            else:
                # Create new document
                self.documents[document_id] = CollaborationState(
                    document_id=document_id,
                    content="",
                    version=0,
                    operations=[],
                    cursors={},
                    participants=set(),
                    last_modified=datetime.now()
                )
            
            # Initialize operation queue
            self.operation_queue[document_id] = []
            
        except Exception as e:
            logger.error(f"Failed to initialize document {document_id}: {e}")
            raise
    
    async def _send_initial_state(self, document_id: str, user_id: str):
        """Send initial document state to a newly connected user"""
        try:
            state = self.documents[document_id]
            websocket = self.connections[document_id][user_id]
            
            initial_message = {
                "type": "initial_state",
                "document_id": document_id,
                "content": state.content,
                "version": state.version,
                "participants": list(state.participants),
                "cursors": {uid: asdict(cursor) for uid, cursor in state.cursors.items() if uid != user_id}
            }
            
            await websocket.send_text(json.dumps(initial_message))
            
        except Exception as e:
            logger.error(f"Failed to send initial state to user {user_id}: {e}")
    
    async def _transform_operation(self, document_id: str, operation: Operation) -> Operation:
        """Apply operational transform to handle concurrent operations"""
        try:
            state = self.documents[document_id]
            
            # Simple operational transform implementation
            # In production, use a more sophisticated OT algorithm like ShareJS
            transformed_op = operation
            
            # Transform against queued operations
            for queued_op in self.operation_queue.get(document_id, []):
                if queued_op.author != operation.author:
                    transformed_op = self._transform_against_operation(transformed_op, queued_op)
            
            return transformed_op
            
        except Exception as e:
            logger.error(f"Failed to transform operation: {e}")
            return operation
    
    def _transform_against_operation(self, op1: Operation, op2: Operation) -> Operation:
        """Transform one operation against another"""
        # Simplified operational transform logic
        # Production implementation should use established OT algorithms
        
        if op2.type == OperationType.INSERT:
            if op1.position >= op2.position:
                op1.position += len(op2.content)
        elif op2.type == OperationType.DELETE:
            if op1.position > op2.position:
                op1.position -= op2.length
        
        return op1
    
    async def _apply_operation(self, document_id: str, operation: Operation):
        """Apply operation to document content"""
        try:
            state = self.documents[document_id]
            
            if operation.type == OperationType.INSERT:
                state.content = (
                    state.content[:operation.position] + 
                    operation.content + 
                    state.content[operation.position:]
                )
            elif operation.type == OperationType.DELETE:
                end_pos = operation.position + operation.length
                state.content = (
                    state.content[:operation.position] + 
                    state.content[end_pos:]
                )
            elif operation.type == OperationType.REPLACE:
                end_pos = operation.position + operation.length
                state.content = (
                    state.content[:operation.position] + 
                    operation.content + 
                    state.content[end_pos:]
                )
            
            # Update version and timestamp
            state.version += 1
            state.last_modified = datetime.now()
            
            # Add to operation history
            state.operations.append(operation)
            
            # Keep only recent operations (last 100)
            if len(state.operations) > 100:
                state.operations = state.operations[-100:]
            
            # Add to operation queue for transform
            if document_id not in self.operation_queue:
                self.operation_queue[document_id] = []
            self.operation_queue[document_id].append(operation)
            
            # Keep queue size manageable
            if len(self.operation_queue[document_id]) > 50:
                self.operation_queue[document_id] = self.operation_queue[document_id][-50:]
            
        except Exception as e:
            logger.error(f"Failed to apply operation: {e}")
            raise
    
    async def _broadcast_operation(self, document_id: str, author_id: str, operation: Operation):
        """Broadcast operation to all connected users except the author"""
        try:
            if document_id not in self.connections:
                return
            
            message = {
                "type": "operation",
                "document_id": document_id,
                "operation": {
                    "type": operation.type.value,
                    "position": operation.position,
                    "content": operation.content,
                    "length": operation.length,
                    "author": operation.author,
                    "timestamp": operation.timestamp
                },
                "version": self.documents[document_id].version
            }
            
            message_json = json.dumps(message)
            
            # Send to all users except the author
            for user_id, websocket in self.connections[document_id].items():
                if user_id != author_id:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        logger.warning(f"Failed to send to user {user_id}: {e}")
                        # Remove disconnected user
                        await self.disconnect_user(document_id, user_id)
            
        except Exception as e:
            logger.error(f"Failed to broadcast operation: {e}")
    
    async def _broadcast_cursor_update(self, document_id: str, user_id: str, cursor: Cursor):
        """Broadcast cursor update to all users except the owner"""
        try:
            if document_id not in self.connections:
                return
            
            message = {
                "type": "cursor_update",
                "document_id": document_id,
                "user_id": user_id,
                "cursor": asdict(cursor)
            }
            
            message_json = json.dumps(message)
            
            for uid, websocket in self.connections[document_id].items():
                if uid != user_id:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        logger.warning(f"Failed to send cursor update to user {uid}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast cursor update: {e}")
    
    async def _broadcast_participant_update(self, document_id: str, user_id: str, action: str):
        """Broadcast participant join/leave to all users"""
        try:
            if document_id not in self.connections:
                return
            
            message = {
                "type": "participant_update",
                "document_id": document_id,
                "user_id": user_id,
                "action": action,
                "participants": list(self.documents[document_id].participants)
            }
            
            message_json = json.dumps(message)
            
            for uid, websocket in self.connections[document_id].items():
                if uid != user_id:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        logger.warning(f"Failed to send participant update to user {uid}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast participant update: {e}")
    
    async def _persist_document(self, document_id: str):
        """Persist document state to Redis"""
        try:
            state = self.documents[document_id]
            
            # Serialize state
            state_data = {
                "document_id": state.document_id,
                "content": state.content,
                "version": state.version,
                "operations": [asdict(op) for op in state.operations[-50:]],  # Keep last 50 operations
                "last_modified": state.last_modified.isoformat()
            }
            
            # Store in Redis with expiration (24 hours)
            key = f"collab_doc:{document_id}"
            await asyncio.to_thread(
                self.redis_client.setex,
                key,
                86400,  # 24 hours
                json.dumps(state_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to persist document {document_id}: {e}")
    
    async def _load_document_from_redis(self, document_id: str) -> Optional[CollaborationState]:
        """Load document state from Redis"""
        try:
            key = f"collab_doc:{document_id}"
            data = await asyncio.to_thread(self.redis_client.get, key)
            
            if not data:
                return None
            
            state_data = json.loads(data)
            
            # Reconstruct operations
            operations = []
            for op_data in state_data.get("operations", []):
                operations.append(Operation(
                    type=OperationType(op_data["type"]),
                    position=op_data["position"],
                    content=op_data.get("content", ""),
                    length=op_data.get("length", 0),
                    author=op_data.get("author", ""),
                    timestamp=op_data.get("timestamp", 0)
                ))
            
            return CollaborationState(
                document_id=state_data["document_id"],
                content=state_data["content"],
                version=state_data["version"],
                operations=operations,
                cursors={},
                participants=set(),
                last_modified=datetime.fromisoformat(state_data["last_modified"])
            )
            
        except Exception as e:
            logger.error(f"Failed to load document {document_id} from Redis: {e}")
            return None
    
    async def _cleanup_document(self, document_id: str):
        """Clean up document when no users are connected"""
        try:
            # Persist final state
            await self._persist_document(document_id)
            
            # Remove from memory
            if document_id in self.documents:
                del self.documents[document_id]
            
            if document_id in self.connections:
                del self.connections[document_id]
            
            if document_id in self.operation_queue:
                del self.operation_queue[document_id]
            
            logger.info(f"Cleaned up document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup document {document_id}: {e}")
    
    async def get_document_stats(self, document_id: str) -> Dict[str, Any]:
        """Get statistics for a collaborative document"""
        try:
            if document_id not in self.documents:
                return {}
            
            state = self.documents[document_id]
            
            return {
                "document_id": document_id,
                "version": state.version,
                "content_length": len(state.content),
                "participants_count": len(state.participants),
                "participants": list(state.participants),
                "operations_count": len(state.operations),
                "last_modified": state.last_modified.isoformat(),
                "cursors_count": len(state.cursors)
            }
            
        except Exception as e:
            logger.error(f"Failed to get document stats for {document_id}: {e}")
            return {}

# Global collaboration manager instance
collaboration_manager = CollaborationManager()