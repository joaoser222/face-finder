from app.models.file import File
from app.controllers.base_controller import BaseController
from PIL import Image
from io import BytesIO
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path

class FileController(BaseController):
    model = File
    prefix = "files"

    def __init__(self):
        super().__init__()
        
        # Define as rotas
        self.router.add_api_route("/thumbnail/{id}", self.get_thumbnail, methods=["GET"])
        self.router.add_api_route("/scaled/{id}", self.get_scaled, methods=["GET"])

    async def get_thumbnail(self, id: int):
        """
        Retorna uma versão miniatura da imagem

        Args:
            id (int): Id do arquivo
        Returns:
            StreamingResponse: Miniatura da imagem
        """
        try:
            file = await self.model.get_or_none(id=id)
            if not file:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")

            file_type, image_format = file.mime_type.split("/")
            
            # Definir o caminho da miniatura
            original_path = Path(file.file_path)
            thumb_dir = original_path.parent / "thumbs"
            thumb_path = thumb_dir / f"{original_path.stem}_thumb.{original_path.suffix}"
            
            # Criar diretório de thumbs se não existir
            thumb_dir.mkdir(exist_ok=True)
            
            # Se a miniatura já existir, retorná-la diretamente
            if thumb_path.exists():
                with open(thumb_path, "rb") as f:
                    return StreamingResponse(BytesIO(f.read()), media_type=file.mime_type)
            
            # Se não existir, criar a miniatura
            with Image.open(file.file_path) as img:
                img.thumbnail((300, 300))  # Redimensiona mantendo o aspect ratio
                
                # Salvar no sistema de arquivos
                img.save(thumb_path, format=image_format.upper(), optimize=True)
                
                # Também preparar para retornar
                buffer = BytesIO()
                img.save(buffer, format=image_format.upper(), optimize=True)
                buffer.seek(0)

            return StreamingResponse(buffer, media_type=file.mime_type)

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_scaled(self, id: int):
        """
        Retorna uma versão escalada da imagem

        Args:
            id (int): Id do arquivo
        Returns:
            StreamingResponse: Imagem escalada
        """
        try:
            file = await self.model.get_or_none(id=id)
            file_type, image_format = file.mime_type.split("/")

            if not file:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
            
            # Limita o tamanho da imagem
            with Image.open(file.file_path) as img:
                img.thumbnail((1280, 1280))  # Redimensiona mantendo o aspect ratio

                # Também preparar para retornar
                buffer = BytesIO()
                img.save(buffer, format=image_format.upper(), optimize=True)
                buffer.seek(0)

            return StreamingResponse(buffer, media_type=file.mime_type)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))