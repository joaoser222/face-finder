from app.models.search import Search,SearchStatus
from app.models.search_face import SearchFace
from .view_controller import ViewController
from app.models.photo import Photo
from app.models.job import Job
from app.models.collection import Collection,CollectionStatus
from tortoise import transactions
from fastapi import UploadFile, HTTPException, Form, Query, Depends
from fastapi.responses import JSONResponse,StreamingResponse
import json,os
from app.utils import logger_info,logger_error,execute_raw_sql
from app.services.recognition import Recognition
from app.tasks import search_faces
import zipfile,io

class SearchController(ViewController):
    model = Search
    prefix = "searches"

    def __init__(self):
        super().__init__()

        self.router.add_api_route(
            "/collections",
            self.get_collections,
            methods=["GET"],
            dependencies=[Depends(self.set_current_user)]
        )

        self.router.add_api_route(
            "/download/{search_id}",
            self.download_result,
            methods=["GET"],
            dependencies=[Depends(self.set_current_user)]
        )
            
    async def create(
        self,
        file: UploadFile,
        params: str = Form(...)
    ):
        try:
            params_dict = json.loads(params)
            params_dict["user_id"] = self.current_user.id

            async with transactions.in_transaction():
                # Criação do registro
                record = await self.model.create(**params_dict)
                # Upload e persistência da foto
                photo = await self.process_uploaded_file(file, Photo, record)

            # Inicializa o FaceAnalysis uma única vez
            recognition = await Recognition.create()
            photo = await recognition.process_single_photo(photo)

            # Validação pós-processamento
            if not photo.face_count:
                if os.path.exists(photo.file_path):
                    os.remove(photo.file_path)
                await photo.delete()
                await record.delete()
                raise HTTPException(400, "A foto não contém faces!")
            else:
                record.thumbnail_photo_id = photo.id
                await record.save()
            
            job = await Job.create(
                process_type="search_faces",
                owner_type='search',
                owner_id=record.id
            )
            
            search_faces.delay(job.id)
            
            logger_info(__name__, f"Job criado para processamento de pesquisa: {record.id}")
            return record

        except json.JSONDecodeError as e:
            logger_error(__name__, e)
            raise HTTPException(400, str(e))

        except Exception as e:
            logger_error(__name__, e)
            raise HTTPException(400, str(e))
    
    async def get_collections(
        self,
        page: int = Query(1, ge=1, description="Número da página"),
        search: str = Query(None, description="Pesquisa")
    ):
        """
        Retorna fotos paginadas de uma collection
        
        Args:
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
            filter_search=""
            if self.search_field and search:
                filter_search = f" AND collections.name LIKE '%%{search}%%'"

            raw_query = f"""
                SELECT collections.* FROM collections
                WHERE
                    collections.user_id = {self.current_user.id} AND
                    collections.status = {CollectionStatus.FINISHED} AND
                    EXISTS (
                        SELECT 1 FROM faces
                        INNER JOIN photos ON photos.owner_id=collections.id
                        WHERE
                            photos.owner_type='collection' AND
                            faces.photo_id = photos.id
                    )
                    {filter_search}
            """
            return await self.query_paginator(raw_query, page)
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))
    
    async def update(self, id: int, params: dict):
        """
        Atualiza um registro na model pelo id

        Args:
            id (int): Id do registro
            params (dict): Parâmetros do registro
        Returns:
            Record: Registro atualizado
        """
        try:
            async with transactions.in_transaction():
                record = await self.get_model_by_user().get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                
                if(params.get('force_recreate')):
                    await SearchFace.filter(search_id=record.id).delete()

                record.tolerance_level = params['tolerance_level']
                await record.save()

                job = await Job.create(
                    process_type="search_faces",
                    owner_type='search',
                    owner_id=record.id
                )

                search_faces.delay(job.id)
                
            return record
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))
    
    async def download_result(self, search_id: int):
        try:
            # Cria um gerador de chunks para streaming
            async def generate_zip_chunks():
                zip_buffer = io.BytesIO()
                raw_query = f"""
                    SELECT photos.file_path, photos.original_name FROM photos
                    WHERE
                        photos.user_id = {self.current_user.id} AND
                        EXISTS (
                            SELECT 1
                            FROM search_faces
                            WHERE 
                                search_faces.photo_id = photos.id AND 
                                search_faces.search_id = {search_id}
                        )
                """
                files_to_zip = await execute_raw_sql(raw_query)

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for file_to_zip in files_to_zip:
                        zip_file.write(file_to_zip['file_path'], arcname=file_to_zip['original_name'])

                zip_buffer.seek(0)
                
                # Lê o ZIP em chunks de 1MB
                while chunk := zip_buffer.read(1024 * 1024):
                    yield chunk
                    zip_buffer.flush()

                zip_buffer.close()

            # Configura o StreamingResponse com o gerador
            return StreamingResponse(
                generate_zip_chunks(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": "attachment; filename=download.zip"
                }
            )

        except Exception as e:
            logger_error(__name__, e)
            raise HTTPException(status_code=400, detail=str(e))

