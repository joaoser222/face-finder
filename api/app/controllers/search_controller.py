from app.models.search import Search
from .view_controller import ViewController
from app.models.photo import Photo
from app.models.job import Job
from tortoise import transactions
from fastapi import UploadFile, HTTPException, Form
import json,os
from app.utils import logger_info,logger_error
from app.services.recognition import Recognition
from app.tasks import search_faces

class SearchController(ViewController):
    model = Search
    prefix = "searches"

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


