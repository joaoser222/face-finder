# app/services/sse_manager.py
import json
import asyncio
import logging
import redis.asyncio as redis
from typing import Dict, Any, AsyncGenerator, Optional, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class SSEManager:
    """
    Gerenciador SSE com Redis que remove eventos após confirmação de recebimento.
    Implementa uma fila FIFO (First-In-First-Out) com confirmação.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SSEManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Inicializa a conexão com Redis e estruturas locais."""
        self.redis_conn = redis.from_url(
            os.getenv("DATABASE_REDIS_URL"),
            decode_responses=True
        )
        
        # Dicionário de filas locais por usuário
        self.active_consumers: Dict[str, asyncio.Queue] = {}
        self.lock = asyncio.Lock()
        logger.info("SSEManager initialized with Redis backend")

    async def _get_redis_list_key(self, user_identifier: str) -> str:
        """Retorna a chave Redis para a lista de eventos do usuário"""
        return f"sse:events:{user_identifier}"

    async def _get_processing_key(self, user_identifier: str) -> str:
        """Retorna a chave Redis para o evento em processamento"""
        return f"sse:processing:{user_identifier}"

    async def publish(self, user_identifier: str, data: Dict[str, Any], event_type: Optional[str] = None) -> bool:
        """
        Publica um evento para um usuário específico.
        O evento só será removido após confirmação de recebimento.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "event_type": event_type,
        }
        
        try:
            # Adiciona o evento no final da lista Redis (RPUSH)
            await self.redis_conn.rpush(
                await self._get_redis_list_key(user_identifier),
                json.dumps(event)
            )
            logger.debug(f"Event published for user {user_identifier}")
            return True
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")
            return False

    async def get_next_event(self, user_identifier: str) -> Optional[Dict[str, Any]]:
        try:
            event_json = await self.redis_conn.lmove(
                await self._get_redis_list_key(user_identifier),
                await self._get_processing_key(user_identifier),
                "RIGHT",
                "LEFT"
            )
            
            if event_json:
                event = json.loads(event_json)
                return event['data']
            return None

        except Exception as e:
            logger.error(f"Error getting next event: {str(e)}")
            return None


    async def confirm_event_processed(self, user_identifier: str) -> bool:
        """
        Confirma que o evento atual foi processado e pode ser removido.
        """
        try:
            # Remove o evento que estava em processamento
            removed = await self.redis_conn.lpop(
                await self._get_processing_key(user_identifier)
            )
            return removed is not None
        except Exception as e:
            logger.error(f"Error confirming event processed: {str(e)}")
            return False

    async def get_event_generator(self, user_identifier: str) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            while True:
                event = await self.get_next_event(user_identifier)
                
                if event:
                    try:
                        yield event
                        await self.confirm_event_processed(user_identifier)
                    except Exception as e:
                        logger.error(f"Error processing event: {str(e)}")
                        await self._requeue_event(user_identifier, event)
                        raise
                else:
                    # Esperar até novos eventos serem publicados
                    await asyncio.sleep(0.5)  # pode aumentar um pouco o intervalo
        except asyncio.CancelledError:
            logger.info(f"Event generator cancelled for user {user_identifier}")
            raise
        except Exception as e:
            logger.error(f"Error in event generator: {str(e)}")
            raise


    async def _requeue_event(self, user_identifier: str, event: Dict[str, Any]) -> bool:
        """
        Recoloca um evento que falhou no processamento de volta na fila.
        """
        try:
            event["status"] = "pending"
            event["retries"] = event.get("retries", 0) + 1
            
            # Adiciona no início da fila (LPUSH para reprocessamento imediato)
            await self.redis_conn.lpush(
                await self._get_redis_list_key(user_identifier),
                json.dumps(event)
            )
            
            # Remove da lista de processamento
            await self.redis_conn.lpop(
                await self._get_processing_key(user_identifier)
            )
            
            return True
        except Exception as e:
            logger.error(f"Error requeueing event: {str(e)}")
            return False

# Exportar singleton
sse_manager = SSEManager()