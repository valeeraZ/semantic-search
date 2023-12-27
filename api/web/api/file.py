from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, status
from fastapi_pagination import Page, Params

from api.web.schema.file import FileOut
from api.web.schema.search_file_result import SearchFileResult
from api.web.service.file import FileService, get_file_service
from api.web.service.file_chunk import FileChunkService, get_file_chunk_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FileOut)
def create_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    file_service: FileService = Depends(get_file_service),
    file_chunk_service: FileChunkService = Depends(get_file_chunk_service),
):
    """
    Creates a file in the files directory and creates its chunks embeddings in background
    """
    file_db = file_service.create_file(file)
    background_tasks.add_task(
        file_chunk_service.create_file_chunks_embedding, file_db.id, file_db.content
    )
    return file_db


@router.get("/", response_model=Page[FileOut])
def get_files(
    file_service: FileService = Depends(get_file_service),
    params: Params = Depends(Params),
):
    """
    Gets all files
    """
    return file_service.get_files(params)


@router.get("/similar", response_model=Page[SearchFileResult])
def get_similar_files(
    question: str,
    file_chunk_service: FileChunkService = Depends(get_file_chunk_service),
    params: Params = Depends(Params),
):
    """
    Gets similar files to a question
    """
    question_embedding = file_chunk_service.create_embedding(question)
    return file_chunk_service.find_similar_file_chunks(question_embedding, params)
