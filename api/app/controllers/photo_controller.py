from app.models.photo import Photo
from app.models.face import Face
from app.controllers.view_controller import ViewController
from PIL import Image
from io import BytesIO
from fastapi import HTTPException,Depends,Query
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path
import os
from tortoise import transactions,connections
from app.utils import logger_info,logger_error

class PhotoController(ViewController):
    model = Photo
    prefix = "photos"
    search_field = "original_name"

    def __init__(self):
        super().__init__()
        
        # Define as rotas
        self.router.add_api_route("/thumbnail/{id}", self.get_thumbnail, methods=["GET"])
        self.router.add_api_route("/scaled/{id}", self.get_scaled, methods=["GET"])
        self.router.add_api_route("/face-thumbnail/{face_id}", self.get_face_thumbnail, methods=["GET"])
        self.router.add_api_route(
            "/by-owner/{owner_type}/{owner_id}", 
            self.get_by_owner, 
            methods=["GET"], 
            dependencies=[Depends(self.set_current_user)]
        )
        self.router.add_api_route(
            "/faces/{id}", 
            self.get_faces, 
            methods=["GET"], 
            dependencies=[Depends(self.set_current_user)]
        )
    
    async def get_by_owner(
        self,
        owner_type: str,
        owner_id: int,
        page: int = Query(1, ge=1, description="Número da página"),
        search: str = Query(None, description="Pesquisa")
    ):
        """
        Retorna fotos paginadas de uma collection
        
        Args:
            owner_type (str): Tipo do owner
            owner_id (int): Id do owner
            page (int): Número da página (default: 1)
            search (str, optional): Texto de pesquisa
        
        Returns:
            dict: {
                "items": lista de fotos,
                "total": total de fotos,
                "page": página atual,
                "per_page": itens por página,
                "total_pages": total de páginas
            }
        """
        try:
            query = self.get_model_by_user().filter(owner_type=owner_type, owner_id=owner_id)
            if self.search_field:
                query = query.filter(**{f"{self.search_field}__icontains": search})
                
            
            return await self.query_paginator(query, page)
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_faces(self, id: int):
        """
        Retorna as faces de uma foto

        Args:
            id (int): Id da foto
        Returns:
            list: Lista de faces
        """
        try:
            faces = await Face.filter(photo_id=id).all()
            return faces
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_face_thumbnail(self, face_id: int):
        """
        Retorna uma versão miniatura da face

        Args:
            face_id (int): Id da face
        Returns:
            StreamingResponse: Miniatura da face
        """
        try:
            face = await Face.get_or_none(id=face_id)
            if not face:
                raise HTTPException(status_code=404, detail="Face não encontrada")
            
            face_path = await face.get_face_path()
            if not os.path.exists(face_path):
                raise HTTPException(status_code=404, detail="Miniatura da face não encontrada")
            
            with open(face_path, "rb") as f:
                return StreamingResponse(BytesIO(f.read()), media_type="image/jpeg")
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))
    
    async def delete(self, id: int):
        """
        Exclui um registro na model pelo id

        Args:
            id (int): Id do registro
        """
        try:
            async with transactions.in_transaction():
                record = await self.get_model_by_user().get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                
                # Remove o arquivo salvo localmente
                if os.path.exists(record.file_path):
                    os.remove(record.file_path)
                
                # Remove as faces associadas
                if(record.face_count > 0):
                    conn = connections.get("default")
    
                    result = await conn.execute_query_dict("""
                        SELECT 
                            COUNT(faces.id) as counter
                        FROM faces
                        INNER JOIN search_faces ON search_faces.face_id = faces.id
                        WHERE 
                            faces.photo_id = $1
                    """,
                        [record.id]
                    )

                    if result[0]["counter"] > 0:
                        raise Exception("Não foi possível excluir o registro, pois ele possui uma pesquisa associada")
                    else:
                        await conn.execute_query_dict("DELETE FROM faces WHERE photo_id = $1", [record.id])

                await record.delete()
            return JSONResponse(content={})
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(400, str(e))

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
    