# app/services/sse_manager.py
import json
import asyncio
import logging
import redis.asyncio as redis
from typing import Dict, Any, AsyncGenerator, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class SSEManager:
    """
    Gerenciador SSE usando Redis como backend para suportar múltiplas instâncias.
    Implementa padrão publish-subscribe com canais por usuário.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SSEManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Inicializa a conexão com Redis e estruturas locais."""
        # Conexão Redis (usando URL de conexão)
        self.redis_conn = redis.from_url(
            os.getenv("DATABASE_REDIS_URL"),
            decode_responses=True
        )
        
        # Dicionário de subscribers locais (por user_identifier)
        self.local_subscribers: Dict[str, asyncio.Queue] = {}
        self.lock = asyncio.Lock()
        logger.info("SSEManager initialized with Redis backend")
    
    async def subscribe(self, user_identifier: str) -> None:
        """
        Registra um usuário para receber eventos.
        Cria um subscription no Redis e uma fila local para o usuário.
        """
        async with self.lock:
            if user_identifier not in self.local_subscribers:
                # Cria uma fila local para o usuário
                self.local_subscribers[user_identifier] = asyncio.Queue()
                
                # Inicia a escuta do canal Redis em segundo plano
                asyncio.create_task(
                    self._redis_listener(user_identifier)
                )
                logger.info(f"User {user_identifier} subscribed to SSE via Redis")
    
    async def unsubscribe(self, user_identifier: str) -> None:
        """Remove a inscrição de um usuário."""
        async with self.lock:
            if user_identifier in self.local_subscribers:
                del self.local_subscribers[user_identifier]
                logger.info(f"User {user_identifier} unsubscribed from SSE")
    
    async def publish(self, user_identifier: str, data: Dict[str, Any], event_type: Optional[str] = None) -> bool:
        """
        Publica um evento para um usuário específico via Redis.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        if event_type:
            event["event"] = event_type
        
        # Publica no canal específico do usuário
        try:
            await self.redis_conn.publish(
                f"sse:{user_identifier}",
                json.dumps(event)
            )
            logger.debug(f"Event published to Redis channel sse:{user_identifier}")
            return True
        except Exception as e:
            logger.error(f"Error publishing to Redis: {str(e)}")
            return False
    
    async def publish_to_all(self, data: Dict[str, Any], event_type: Optional[str] = None) -> int:
        """
        Publica um evento para todos os usuários via Redis.
        (Implementação alternativa usando um canal broadcast)
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "broadcast": True
        }
        
        if event_type:
            event["event"] = event_type
        
        try:
            await self.redis_conn.publish(
                "sse:broadcast",
                json.dumps(event)
            )
            logger.debug("Broadcast event published to Redis")
            return len(self.local_subscribers)
        except Exception as e:
            logger.error(f"Error publishing broadcast: {str(e)}")
            return 0
    
    async def get_event_generator(self, user_identifier: str) -> AsyncGenerator[str, None]:
        """
        Cria um gerador de eventos SSE para um usuário.
        """
        await self.subscribe(user_identifier)
        
        try:
            while True:
                # Pega eventos da fila local do usuário
                event = await self.local_subscribers[user_identifier].get()
                yield self._format_sse_event(event)
        except asyncio.CancelledError:
            logger.info(f"SSE connection cancelled for user {user_identifier}")
            await self.unsubscribe(user_identifier)
            raise
        except Exception as e:
            logger.error(f"Error in event generator for user {user_identifier}: {str(e)}")
            await self.unsubscribe(user_identifier)
            raise
    
    async def _redis_listener(self, user_identifier: str) -> None:
        """
        Escuta mensagens do Redis e coloca na fila local do usuário.
        """
        pubsub = self.redis_conn.pubsub()
        await pubsub.subscribe(
            f"sse:{user_identifier}",
            "sse:broadcast"
        )
        
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                
                event = json.loads(message["data"])
                
                # Verifica se é um broadcast ou mensagem específica
                if (message["channel"] == "sse:broadcast" and 
                    not event.get("broadcast", False)):
                    continue
                
                # Adiciona na fila local do usuário
                if user_identifier in self.local_subscribers:
                    await self.local_subscribers[user_identifier].put(event)
        except Exception as e:
            logger.error(f"Redis listener error for {user_identifier}: {str(e)}")
        finally:
            await pubsub.unsubscribe()
            logger.info(f"Stopped Redis listener for {user_identifier}")
    
    def _format_sse_event(self, event: dict) -> str:
        """Formata um evento no formato SSE."""
        message = ""
        
        if "event" in event:
            message += f"event: {event['event']}\n"
        
        message += f"data: {json.dumps(event['data'])}\n\n"
        return message

# Exportar singleton
sse_manager = SSEManager()