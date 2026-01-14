from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path


def _env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(_env(key, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass(slots=True, frozen=True)
class Config:
    # input
    source: str = _env("SOURCE", "file")
    video_path: Path | None = Path(_env("VIDEO_PATH")) if _env("VIDEO_PATH") else None
    camera_index: int = _env_int("CAMERA_INDEX", 0)

    # output
    rtsp_port: int = _env_int("RTSP_PORT", 8554)
    mount_point: str = _env("MOUNT_POINT", "/video")

    # encoding
    width: int | None = (
        _env_int("WIDTH", 0) or None
    )  # 0 -> None, to skip in caps
    height: int | None = _env_int("HEIGHT", 0) or None
    framerate: int | None = _env_int("FRAMERATE", 0) or None
    bitrate: int = _env_int("BITRATE", 800)

    @property
    def is_webcam(self) -> bool:
        return self.source.lower() == "webcam"

    def validate(self) -> None:
        if self.is_webcam:
            return
        if self.video_path is None:
            raise RuntimeError("VIDEO_PATH must be set when SOURCE=file")
        if not self.video_path.is_file():
            raise FileNotFoundError(self.video_path)
