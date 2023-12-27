import io
import os
import shutil

from fastapi import Depends, UploadFile
from fastapi_pagination import Page, Params

from api.infra.db.model.file import File
from api.infra.db.repository.file import FileRepository, get_file_repository
from api.web.schema.file import FileOut
from api.web.service.file_parser import FileParser


class FileService:
    def __init__(self, file_repository: FileRepository):
        self.file_repository = file_repository

    def create_file(self, file: UploadFile) -> File:
        """
        Creates a file in the files directory
        :param file: The file to be created
        :return: The file path
        """
        allowed_extensions = ["txt", "pdf"]
        extension = file.filename.split(".")[-1]
        if extension not in allowed_extensions:
            raise ValueError(f"Unsupported file extension: {extension}")

        folder = "files"
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_path = os.path.join(folder, file.filename)

        with open(file_path, "wb+") as f:
            file_like_object = io.BytesIO(file.file.read())
            shutil.copyfileobj(file_like_object, f)
        content_parser = FileParser(file_path)
        file_text_content = content_parser.parse()
        file_model = File(
            name=file.filename,
            path=file_path,
            size=os.path.getsize(file_path),
            content=file_text_content,
        )
        return self.file_repository.create(file_model)

    def get_files(self, params: Params = Params()) -> Page[File]:
        """
        Gets all files
        :return: The files
        """
        return self.file_repository.get_many(params=params)

    def find_file_by_id(self, file_id: int) -> FileOut:
        """
        Finds a file by id
        :param file_id: The file id
        :return: The file
        """
        file = self.file_repository.get_by_id(file_id)
        return FileOut(
            id=file.id,
            name=file.name,
            size=file.size,
            resume_content=file.content[:100],
            created_at=file.created_at,
            updated_at=file.updated_at,
        )


def get_file_service(
    file_repository: FileRepository = Depends(get_file_repository),
) -> FileService:
    return FileService(file_repository)
