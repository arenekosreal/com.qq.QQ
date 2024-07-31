import hashlib
import json
import logging
import math
import sys
from typing import Literal, Self
from dataclasses import dataclass
from pathlib import Path


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_stream_handler = logging.StreamHandler()
_stream_handler.setLevel(_logger.level)
_fmt = logging.Formatter("%(asctime)s-%(levelname)s-%(message)s", "%Y-%m-%d %H:%M:%S")
_stream_handler.setFormatter(_fmt)
[_logger.removeHandler(handler) for handler in _logger.handlers]
_logger.addHandler(_stream_handler)

AlgorithmType = Literal["SHA256"]  # TODO: more algorithms


IntegrityDictInfo = dict[
    Literal["algorithm", "hash", "blockSize", "blocks"],
    AlgorithmType | str | int | list[str],
]


@dataclass
class IntegrityInfo:
    """
    ```json
    {
        "algorithm": "SHA256",
        "hash": "932cafcedb9780bd300f3a03fab763dc700dbe89cedd0c77b0b57258f92ef480",
        "blockSize": 4194304,
        "blocks": [
            "932cafcedb9780bd300f3a03fab763dc700dbe89cedd0c77b0b57258f92ef480"
        ]
    }
    """

    algorithm: AlgorithmType
    hash_: str
    blocksize: int
    blocks: list[str]


FileMetaDictInfo = dict[
    Literal["size", "offset", "unpacked", "integrity"], int | str | IntegrityDictInfo
]


@dataclass
class FileMetaInfo:
    """
    ```json
    {
        "size": 80,
        "offset": "0",
        "integrity": {
            "algorithm": "SHA256",
            "hash": "932cafcedb9780bd300f3a03fab763dc700dbe89cedd0c77b0b57258f92ef480",
            "blockSize": 4194304,
            "blocks": [
                "932cafcedb9780bd300f3a03fab763dc700dbe89cedd0c77b0b57258f92ef480"
            ]
        }
    }
    ```
    """

    size: int
    offset: str  # NOTE: Use int(info.offset) to convert, this is string in raw json
    unpacked: bool
    integrity: IntegrityInfo


FolderMetaDictInfo = dict[
    str, FileMetaDictInfo | dict[Literal["files"], "FolderMetaDictInfo"]
]


@dataclass
class FolderMetaInfo:
    """
    ```json
    {
        "ark-engine": {
            "files": {
                "arkeng-engine.js": {
                    "size": 353936,
                    "offset": "240",
                    "integrity": {
                        "algorithm": "SHA256",
                        "hash": "0391524cf9df3a4649f3e9a5b872e5c13244f41306ad056dc1fa69946290997b",
                        "blockSize": 4194304,
                        "blocks": [
                            "0391524cf9df3a4649f3e9a5b872e5c13244f41306ad056dc1fa69946290997b"
                        ]
                    }
                },
                "arkeng-wasmoon.js": {
                    "size": 219776,
                    "offset": "354176",
                    "integrity": {
                        "algorithm": "SHA256",
                        "hash": "4d08565457667d48941272c601b1454248a381f7880e03222d0b01d58ea8d467",
                        "blockSize": 4194304,
                        "blocks": [
                            "4d08565457667d48941272c601b1454248a381f7880e03222d0b01d58ea8d467"
                        ]
                    }
                },
                "arkeng-yoga.js": {
                    "size": 329488,
                    "offset": "573952",
                    "integrity": {
                        "algorithm": "SHA256",
                        "hash": "79e4dab35c6b11c3eb0c97dd32048d0d7aa3ed2e65bc9c48ca40a9a4ab46a1da",
                        "blockSize": 4194304,
                        "blocks": [
                            "79e4dab35c6b11c3eb0c97dd32048d0d7aa3ed2e65bc9c48ca40a9a4ab46a1da"
                        ]
                    }
                }
            }
        },
        "denoiser-wasm.js": {
            "size": 2136816,
            "offset": "903440",
            "integrity": {
                "algorithm": "SHA256",
                "hash": "2ffc5abdeb594e295acc7deb79f4976369fdfa997e9db0e6c23a4a0bb6ec91be",
                "blockSize": 4194304,
                "blocks": [
                    "2ffc5abdeb594e295acc7deb79f4976369fdfa997e9db0e6c23a4a0bb6ec91be"
                ]
            }
        }
    }
    ```
    """

    files: dict[str, FileMetaInfo]
    folders: dict[str, Self]

    def listdir(self, recursive: bool = False) -> list[Path]:
        """List contents in the folder

        Args:
            recursive(bool): If check recursivly. Defaults to False

        Returns:
            list[Path]: A list of paths of files/folders in the folder.
        """
        paths: list[Path] = []
        for f in self.files:
            paths.append(Path(f))
        if recursive:
            for f, i in self.folders.items():
                paths.extend([Path(f) / d for d in i.listdir()])
        return paths

    def get_file(self, path: Path) -> FileMetaInfo | None:
        """Get file in the folder

        Args:
            path(Path): The path relative to the folder

        Returns:
            FileMetaInfo | None: The description of file, None if no such file.

        Remarks:
            Not check recursively. Only checks path.name
        """
        for f, i in self.files.items():
            if f == path.name:
                return i


def _to_integrity_info(data: IntegrityDictInfo) -> IntegrityInfo:
    algorithm: AlgorithmType | None = None
    hash_: str | None = None
    blocksize: int | None = None
    blocks: list[str] | None = None
    for key, value in data.items():
        match key:
            case "algorithm":
                if not isinstance(value, str):
                    raise ValueError("Invalid algorithm ", value)
                match value:
                    case "SHA256":  # TODO Add more algorithms here
                        algorithm = value
                    case _:
                        raise NotImplementedError("Unsupported algorithm ", value)
            case "hash":
                if not isinstance(value, str):
                    raise ValueError("Invalid hash ", value)
                hash_ = value
            case "blockSize":
                if not isinstance(value, int):
                    raise ValueError("Invalid blockSize ", value)
                blocksize = value
            case "blocks":
                if not isinstance(value, list):
                    raise ValueError("Invalid blocks ", value)
                blocks = value

    assert algorithm is not None
    assert hash_ is not None
    assert blocksize is not None
    assert blocks is not None
    return IntegrityInfo(
        algorithm=algorithm, hash_=hash_, blocksize=blocksize, blocks=blocks
    )


def _to_file_meta_info(data: FileMetaDictInfo) -> FileMetaInfo:
    size: int | None = None
    offset: str | None = None
    unpacked: bool = False
    integrity: IntegrityInfo | None = None
    for key, value in data.items():
        match key:
            case "size":
                if not isinstance(value, int):
                    raise ValueError("Invalid size ", value)
                size = value
            case "offset":
                if not isinstance(value, str):
                    raise ValueError("Invalid offset ", value)
                offset = value
                unpacked = False
            case "unpacked":
                if not isinstance(value, bool):
                    raise ValueError("Invalid unpack ", value)
                offset = ""
                unpacked = value
            case "integrity":
                if not isinstance(value, dict):
                    raise ValueError("Invalid integrity ", value)
                integrity = _to_integrity_info(value)
    assert size is not None
    if not unpacked:
        assert offset is not None and offset != ""
    else:
        assert offset == ""
    assert integrity is not None
    return FileMetaInfo(
        size=size, offset=offset, unpacked=unpacked, integrity=integrity
    )


def _to_folder_meta_info(data: FolderMetaDictInfo) -> FolderMetaInfo:
    files: dict[str, FileMetaInfo] = {}
    folders: dict[str, FolderMetaInfo] = {}
    for key, value in data.items():
        if list(value.keys()) == ["files"]:
            folders[key] = _to_folder_meta_info(value["files"])  # pyright: ignore [reportArgumentType]
        else:
            files[key] = _to_file_meta_info(value)  # pyright: ignore [reportArgumentType]
    return FolderMetaInfo(files=files, folders=folders)


def _check_sha256(
    file_bytes: bytes, integrity: IntegrityInfo, check_blocks: bool
) -> bool:
    if check_blocks:
        blocks = [
            file_bytes[i : i + integrity.blocksize]
            for i in range(0, len(file_bytes), integrity.blocksize)
        ]
        for block in blocks:
            i = blocks.index(block)
            calculator = hashlib.sha256(block)
            actual_digest = calculator.hexdigest()
            target_digest = integrity.blocks[i]
            if actual_digest != target_digest:
                _logger.error("Block %s's hash check failed", i)
                _logger.debug("Wants %s, got %s", target_digest, actual_digest)
                return False
    actual_digest = hashlib.sha256(file_bytes).hexdigest()
    target_digest = integrity.hash_
    if actual_digest != target_digest:
        _logger.error("Hash check failed")
        _logger.debug("Wants %s, got %s", target_digest, actual_digest)
    return actual_digest == target_digest


def check_file(
    file_bytes: bytes, integrity: IntegrityInfo, check_blocks: bool = True
) -> bool:
    """Check the integrity of file bytes

    Args:
        file_bytes(bytes): The read file in bytes
        integrity(IntegrityInfo): The checksums of file
        check_blocks(bool): If check file blocks splited by integrity.blocksize

    Returns:
        bool: If check success
    """
    match integrity.algorithm:
        case "SHA256":
            return _check_sha256(file_bytes, integrity, check_blocks)


def get_header(asar: bytes, align: int = 4) -> tuple[FolderMetaInfo, int]:
    """Get filesystem structure in asar archive

    Args:
        asar(bytes): The read asar archive in bytes
        align(int): How many bytes are aligned, to calculate padding. Defaults to 4 bytes(DWORD)

    Returns:
        tuple[FolderMetaInfo, int]: The filesystem structure and position where file content starts.

    See also: https://knifecoat.com/Posts/ASAR+Format+Spec
    """
    FILE_HEADER_END = 16
    JSON_HEADER_SIZE_LENGTH = 4
    json_header_size_bytes = asar[
        FILE_HEADER_END - JSON_HEADER_SIZE_LENGTH : FILE_HEADER_END
    ]
    json_header_size_int = int.from_bytes(json_header_size_bytes, sys.byteorder)
    _logger.debug("JSON header size is %s", json_header_size_int)
    json_header_end = FILE_HEADER_END + json_header_size_int
    _logger.debug("JSON header ends at %s", json_header_end)
    json_header_bytes = asar[FILE_HEADER_END:json_header_end]
    headers: dict[Literal["files"], FolderMetaDictInfo] = json.loads(json_header_bytes)
    if _logger.level == logging.DEBUG:
        with open("header.debug.json", "w") as writer:
            json.dump(headers, writer, indent=4)
    content_start = math.ceil(json_header_end / align) * align
    _logger.debug("Padding is %s", content_start - json_header_end)
    return _to_folder_meta_info(headers["files"]), content_start


def get_file(
    asar: bytes, file_info: FileMetaInfo, force_validate: bool = False
) -> bytes:
    """Get file bytes in asar archive

    Args:
        asar(bytes): The read asar archive in bytes
        file_info(FileMetaInfo): the description info of file
        force_validate(bool): If raise RuntimeError when check integrity failed

    Returns:
        bytes: the file contents in bytes.
    """
    if file_info.unpacked:
        raise ValueError("The file is unpacked so it cannot be extracted in archive")
    _, offsetbase = get_header(asar)
    file_offset = offsetbase + int(file_info.offset)
    file_bytes = asar[file_offset : file_offset + file_info.size]
    if not check_file(file_bytes, file_info.integrity):
        _logger.error("Check integrity for file failed.")
        if force_validate:
            raise RuntimeError("Failed to check integrity")
    return file_bytes


if __name__ == "__main__":
    with open("application.asar", "rb") as reader:
        content = reader.read()
    root, _ = get_header(content)
    for f in root.listdir():
        if f.name.startswith("preload") and f.name.endswith(".js"):
            file_info = root.get_file(f)
            if file_info is not None:
                with open(f.name, "wb") as writer:
                    content_to_write = get_file(content, file_info)
                    _ = writer.write(content_to_write)
