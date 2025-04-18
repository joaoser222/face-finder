from fastapi.responses import StreamingResponse
from fastapi import HTTPException
import json
from app.controllers.base_controller import BaseController
from app.models.session import Session
from app.services.sse_manager import sse_manager

class SSEController(BaseController):
    prefix = "sse"

    def __init__(self):
        super().__init__()
        
        # Rota para eventos SSE que requer autenticação
        self.router.add_api_route("/events/{token}", self.events, methods=["GET"])

    async def events(self,token):
        """
        Endpoint para iniciar uma conexão SSE.
        O usuário já está disponível em self.current_user devido ao Depends(self.set_current_user)
        
        Returns:
            Um StreamingResponse que mantém a conexão aberta
        """

        session = await Session.filter(token=token).first()
        if not session:
            raise HTTPException(status_code=401, detail="Sessão não encontrada")
        
        # Iniciar stream de eventos
        return StreamingResponse(
            sse_manager.get_event_generator(session.user_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )