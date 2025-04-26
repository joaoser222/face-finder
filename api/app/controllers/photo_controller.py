from app.models.photo import Photo
from app.models.face import Face
from app.controllers.view_controller import ViewController
from PIL import Image
from io import BytesIO
from fastapi import HTTPException,Depends,Query
from fastapi.responses import StreamingResponse
from pathlib import Path
import os
from app.utils import logger_info,logger_error,execute_raw_sql

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
            "/faces/{photo_id}", 
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
            raw_query = ""
            filter_search=""
            if self.search_field and search:
                filter_search = f" AND photos.{self.search_field} LIKE '%%{search}%%'"
            
            if(owner_type=='search'):
                raw_query = f"""
                    SELECT photos.* FROM photos
                    WHERE
                        photos.user_id = {self.current_user.id} AND
                        EXISTS (
                            SELECT 1
                            FROM search_faces
                            WHERE 
                                search_faces.photo_id = photos.id AND 
                                search_faces.search_id = {owner_id}
                        )
                        {filter_search}
                """
            elif(owner_type=='collection'):
                raw_query = f"""
                    SELECT photos.* FROM photos
                    WHERE
                        photos.user_id = {self.current_user.id} AND
                        photos.owner_type = 'collection' AND
                        photos.owner_id = {owner_id}
                        {filter_search}
                """
            return await self.query_paginator(raw_query, page)
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_faces(self, photo_id: int,search_id: int = Query(None, description="Pesquisa de Face")):
        """
        Retorna as faces de uma foto

        Args:
            id (int): Id da foto
        Returns:
            list: Lista de faces
        """
        try:
            result = []

            # Caso o id de pesquisa seja passado na query, retorna as faces da pesquisa
            if(search_id):
                query = f"""
                    SELECT 
                        faces.*,
                        search_face.similarity 
                    FROM faces
                    INNER JOIN search_faces ON search_faces.face_id = faces.id
                    WHERE
                        search_faces.search_id = {search_id} AND
                        faces.user_id = {self.current_user.id} AND
                        faces.photo_id = {photo_id}
                """

                result = await execute_raw_sql(query)
            else:
                result = await Face.filter(photo_id=photo_id).all()
               
            return result
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
    