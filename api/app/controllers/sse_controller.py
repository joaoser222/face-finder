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
        
        self.router.add_api_route("/events/{token}", self.events, methods=["GET"])

    async def events(self, token):
        """
        Endpoint para iniciar uma conexão SSE.
        """

        session = await Session.filter(token=token).first()
        if not session:
            raise HTTPException(status_code=401, detail="Sessão não encontrada")
        
        async def event_stream():
            async for event in sse_manager.get_event_generator(session.user_id):
                yield f"data: {json.dumps(event)}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
