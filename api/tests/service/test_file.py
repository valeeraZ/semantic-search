import io
import os
import shutil
from unittest.mock import MagicMock, mock_open

import pytest

from api.web.service.file import FileService


@pytest.fixture
def file_service():
    file_repository = MagicMock()
    return FileService(file_repository=file_repository)


@pytest.fixture
def mock_upload_file():
    upload_file = MagicMock()
    upload_file.filename = "test.txt"
    upload_file.file.read.return_value = b"Test file content"
    return upload_file


def test_create_file(file_service: FileService, mock_upload_file, monkeypatch):
    # Set the return values for the mocked functions
    # Mock the dependencies
    mock_exists = MagicMock(return_value=True)
    mock_mkdir = MagicMock()
    mock_getsize = MagicMock(return_value=123)
    mock_shutil_copyfileobj = MagicMock()
    mock_open_file = mock_open()
    mock_file_parser_instance = MagicMock()
    mock_file_parser_instance.parse.return_value = "Parsed file content"
    mock_file_parser = MagicMock(return_value=mock_file_parser_instance)
    mock_file_model_instance = MagicMock()

    # Use monkeypatch to replace the actual functions with mocks
    monkeypatch.setattr(os.path, "exists", mock_exists)
    monkeypatch.setattr(os, "mkdir", mock_mkdir)
    monkeypatch.setattr("builtins.open", mock_open_file)
    monkeypatch.setattr(
        io, "BytesIO", MagicMock(return_value=io.BytesIO(b"Test file content"))
    )
    monkeypatch.setattr(shutil, "copyfileobj", mock_shutil_copyfileobj)
    monkeypatch.setattr(os.path, "getsize", mock_getsize)
    monkeypatch.setattr("api.web.service.file.FileParser", mock_file_parser)
    file_service.file_repository.create = MagicMock(
        return_value=mock_file_model_instance
    )

    # Call the function under test
    result = file_service.create_file(mock_upload_file)

    # Assertions
    mock_exists.assert_called_once_with("files")  # Corrected line
    mock_open_file.assert_called_with("files/test.txt", "wb+")
    mock_shutil_copyfileobj.assert_called_once()
    mock_file_parser_instance.parse.assert_called_once()
    mock_getsize.assert_called_once_with("files/test.txt")
    # assert file_repository.create.assert_called_once_with(mock_file_model_instance)
    # Assert that file_repository.create was called with an object that has the expected attributes

    create_call_args = file_service.file_repository.create.call_args
    assert create_call_args is not None, "create method was not called."

    created_file = create_call_args[0][
        0
    ]  # This should be the file object passed to the create method
    assert created_file.name == "test.txt", "File name should be 'test.txt'."
    assert (
        created_file.path == "files/test.txt"
    ), "File path should be 'files/test.txt'."
    assert created_file.size == 123, "File size should be 123."
    assert (
        created_file.content == "Parsed file content"
    ), "File content should be 'Parsed file content'."

    assert (
        result == mock_file_model_instance
    ), "The result should be the created file model instance."
