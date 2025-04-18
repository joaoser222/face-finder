import asyncio
from pathlib import Path
from insightface.app import FaceAnalysis
from PIL import Image
import numpy as np
from app.models.face import Face
from app.models.photo import Photo
from app.models.search_face import SearchFace
from app.models.search import Search
from app.utils import logger_info, logger_error
import os
class Recognition:
    model_path = '/app/files/system/insightface'
    model_name = 'buffalo_l'

    def __init__(self, app):
        """
        Inicialização síncrona padrão.
        Recebe uma instância já configurada do FaceAnalysis.
        """
        self.app = app

    @classmethod
    def get_face_analyzer(cls):
        return FaceAnalysis(name=cls.model_name,root=cls.model_path)

    @classmethod
    async def create(cls):
        """
        Factory method assíncrono para criação da instância.
        Garante o download do modelo se necessário.
        """
        app = cls.get_face_analyzer()
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        return cls(app)
    
    @classmethod
    def is_model_downloaded(cls):
        model_dir = os.path.join(cls.model_path, 'models', cls.model_name)
        
        if not os.path.exists(model_dir):
            return False

        return True

    @classmethod
    def download_model(cls):
        """
        Factory method assíncrono para download do modelo.
        """
        try:
            logger_info(__name__, f"Baixando modelo '{cls.model_name}' para reconhecimento")

            # Executa o prepare em uma thread separada (pois é uma operação bloqueante)
            app = cls.get_face_analyzer()
            app.prepare(ctx_id=0, det_size=(640, 640))
        except Exception as e:
            logger_error(__name__, e)
            raise
    
    async def compare_faces(self, search: Search, face: dict):
        """
        Compara duas faces e cria um registro de face na busca caso o nível de similaridade 
        seja maior ou igual ao nível de tolerância
        """
        try:
            [photo_search_id] = await Photo.filter(
                owner_id=search.id,
                owner_type="search"
            ).values_list('id', flat=True)

            reference_face = await Face.filter(photo_id=photo_search_id).first()

            similarity = np.dot(reference_face.data['embedding'], face.data['embedding']) / (
                np.linalg.norm(reference_face.data['embedding']) * np.linalg.norm(face.data['embedding'])
            )

            if similarity >= float(search.tolerance_level*0.01):
                has_face = await SearchFace.filter(search_id=search.id, face_id=face.id).exists()
                if not has_face:
                    face = await SearchFace.create(
                        search_id=search.id,
                        similarity=float(similarity),
                        face_id=face.id,
                        photo_id=face.photo_id,
                        user_id=search.user_id
                    )
                    return face
        except Exception as e:
            logger_error(__name__, e)
            raise

    async def process_single_photo(self, photo):
        """
        Processa uma foto de forma assíncrona
        """
        try:
            # Carregar imagem
            img_pil = Image.open(photo.file_path)
            img_np = np.array(img_pil)  # Converte para numpy array

            # Converte para BGR para ficar compativel com insightface
            img = img_np[:, :, ::-1].copy()
            
            # Detectar faces (esta parte roda na thread do pool)
            faces = self.app.get(img)

            if(len(faces) > 0):
                # Definir o caminho das faces
                original_path = Path(photo.file_path)
                face_dir = original_path.parent / "faces"

                # Criar diretório de faces se não existir
                face_dir.mkdir(exist_ok=True)

                # Processar faces detectadas
                for face in faces:
                    # Salvar face no banco de dados
                    face_record = await Face.create(
                        data={
                            "bbox": face.bbox.tolist(),
                            "landmark": face.landmark.tolist() if face.landmark is not None else None,
                            "gender": int(face.gender) if hasattr(face, "gender") else None,
                            "age": int(face.age) if hasattr(face, "age") else None,
                            "embedding": face.embedding.tolist() if hasattr(face, "embedding") else None,
                            "score": float(face.det_score),
                        },
                        user_id=photo.user_id,
                        photo_id=photo.id,
                    )
                    
                    face_path = await face_record.get_face_path()

                    x1, y1, x2, y2 = face.bbox.astype(int)
            
                    # Cortar o rosto da imagem original
                    face_img = img_pil.crop((x1, y1, x2, y2))
                    
                    # Salvar a imagem do rosto na pasta local
                    face_img.save(face_path, optimize=True)

                    logger_info(__name__, f'Face {face_record.id} salva em {face_path}')
                    
                    photo.face_count += 1

            photo.is_indexed = True
            await photo.save()
            return photo
            
        except Exception as e:
            logger_error(__name__, e)
            return photo  # Retorna a foto mesmo com erro para continuar o processamento
