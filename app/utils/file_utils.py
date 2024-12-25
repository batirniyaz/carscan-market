import logging
from typing import Optional

import aioboto3
import cv2
import numpy as np
from botocore.exceptions import ClientError
from fastapi import HTTPException, status, UploadFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from app.config import AWS_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ENDPOINT_URL


class S3Manager:
    def __init__(self):
        self.bucket_name = AWS_BUCKET_NAME
        self.endpoint_url = AWS_ENDPOINT_URL
        self.session = aioboto3.Session()

    async def _get_client(self):
        return self.session.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=self.endpoint_url,
        )

    async def upload_file(
        self, file_path: str, key: str, content_type: Optional[str] = None
    ):
        """Загрузить файл в S3."""
        try:
            async with await self._get_client() as s3_client:
                extra_args = {"ContentType": content_type} if content_type else {}
                await s3_client.upload_file(
                    Filename=file_path,
                    Bucket=self.bucket_name,
                    Key=key,
                    ExtraArgs=extra_args,
                )
                logger.info(f"Файл {file_path} загружен как {key}")
                return key
        except ClientError as e:
            logger.error(f"Ошибка при загрузке файла {file_path}: {e}")
            raise

    async def download_file(self, key: str, download_path: str):
        try:
            async with await self._get_client() as s3_client:
                await s3_client.download_file(
                    Bucket=self.bucket_name, Key=key, Filename=download_path
                )
                logger.info(f"Файл {key} скачан в {download_path}")
        except ClientError as e:
            logger.error(f"Ошибка при скачивании файла {key}: {e}")
            raise

    async def delete_file(self, key: str):
        try:
            async with await self._get_client() as s3_client:
                await s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                logger.info(f"Файл {key} удален из S3")
        except ClientError as e:
            logger.error(f"Ошибка при удалении файла {key}: {e}")
            raise

    async def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        try:
            async with await self._get_client() as s3_client:
                url = await s3_client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expiration,
                )
                logger.info(f"Создана ссылка на {key}")
                return url
        except ClientError as e:
            logger.error(f"Ошибка генерации ссылки для {key}: {e}")
            raise

    async def upload_image(
            self, image: UploadFile, key: str, format: str = "jpg"
    ) -> Optional[str]:
        """Загрузить изображение в S3."""
        try:
            file_content = await image.read()
            image_array = np.frombuffer(file_content, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный формат изображения",
                )

            # Кодирование изображения в буфер
            success, buffer = cv2.imencode(f".{format}", image)
            if not success:
                raise ValueError("Ошибка при кодировании изображения")

            async with await self._get_client() as s3_client:
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=buffer.tobytes(),
                    ContentType="image/jpeg",
                )
                logger.info(f"Изображение сохранено как {key}")
                return key
        except ClientError as e:
            logger.error(f"Ошибка при загрузке изображения: {e}")
            raise

# Инициализация менеджера S3
s3_manager = S3Manager()
