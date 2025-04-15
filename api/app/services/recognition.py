import asyncio
from pathlib import Path
from insightface.app import FaceAnalysis
from PIL import Image
import numpy as np
from app.models.face import Face
from app.utils import logger_info, logger_error
import os
class Recognition:
    def __init__(self, app):
        """
        Inicialização síncrona padrão.
        Recebe uma instância já configurada do FaceAnalysis.
        """
        self.app = app

    @classmethod
    async def create(cls, model_name="buffalo_l"):
        """
        Factory method assíncrono para criação da instância.
        Garante o download do modelo se necessário.
        """
        app = FaceAnalysis(name=model_name)
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        return cls(app)
    
    @staticmethod
    def is_model_downloaded(model_name='buffalo_l'):
        base_dir = os.path.expanduser('~/.insightface/models')
        model_dir = os.path.join(base_dir, model_name)
        
        if not os.path.exists(model_dir):
            return False

        return True

    @staticmethod
    async def download_model(model_name="buffalo_l"):
        """
        Factory method assíncrono para download do modelo.
        """
        try:
            logger_info(__name__, f"Baixando modelo '{model_name}' para reconhecimento")
            # Executa o prepare em uma thread separada (pois é uma operação bloqueante)
            app = FaceAnalysis(name=model_name)
            await asyncio.to_thread(
                lambda: app.prepare(ctx_id=0, det_size=(640, 640))
            )
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
