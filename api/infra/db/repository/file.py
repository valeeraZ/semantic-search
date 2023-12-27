from fastapi import Depends
from fastapi_pagination import Page, Params, paginate
from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session, aliased

from api.infra.db.dependencies import get_db_session
from api.infra.db.model.file import File, FileChunk
from api.infra.db.repository.base import BaseRepository


class FileRepository(BaseRepository[File]):
    pass


class FileChunkRepository(BaseRepository[FileChunk]):
    def find_similar_file_chunks(
        self, question_embedding: list[float], params: Params = Params()
    ) -> Page[Row]:
        """
        Finds similar top k file chunks belonging to different files for a question embedding
        :param params: The pagination params
        :param question_embedding: The question embedding
        :return: The similar file chunks
        """
        # get top_k similar file chunks but having different file_id
        # Define a threshold for similarity
        similarity_threshold = 0.25
        file_chunk_alias = aliased(self.model)
        subq = (
            select(
                file_chunk_alias.file_id.label("file_id"),
                func.min(
                    file_chunk_alias.embedding_vector.cosine_distance(
                        question_embedding
                    )
                ).label("min_distance"),
            )
            .group_by(file_chunk_alias.file_id)
            .alias()
        )

        # Main query to get the file chunks with the smallest distance (highest similarity) from each file
        most_similar_chunks_query = (
            select(self.model, subq.c.min_distance)
            .join(subq, self.model.file_id == subq.c.file_id)
            .where(
                self.model.embedding_vector.cosine_distance(question_embedding)
                == subq.c.min_distance,
                self.model.embedding_vector.cosine_distance(question_embedding)
                < similarity_threshold,
            )
            .order_by(subq.c.min_distance)
        )

        result = self.session.execute(most_similar_chunks_query)
        # result contains rows of (file_chunk, min_distance), so we don't use scalars() here
        return paginate(result.all(), params=params)


def get_file_repository(session: Session = Depends(get_db_session)) -> FileRepository:
    return FileRepository(File, session)


def get_file_chunk_repository(
    session: Session = Depends(get_db_session),
) -> FileChunkRepository:
    return FileChunkRepository(FileChunk, session)
