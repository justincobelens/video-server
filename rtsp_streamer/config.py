from __future__ import annotations
import logging
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


log = logging.getLogger("rtsp_streamer.config")
_VIDEO_PATH = _env("VIDEO_PATH")
_CAMERA_DEVICE = _env("CAMERA_DEVICE")


def _validate_video_path(video_path: Path | None) -> None:
    if video_path is None:
        message = "VIDEO_PATH must be set when SOURCE=file"
        log.error(message)
        raise RuntimeError(message)
    if not video_path.parent.is_dir():
        log.error(f"Video folder does not exist: {video_path.parent}")
        raise FileNotFoundError(video_path.parent)
    if not video_path.is_file():
        log.error(f"Video file does not exist: {video_path}")
        raise FileNotFoundError(video_path)


def _validate_camera_device(device_path: Path) -> None:
    if not device_path.exists():
        log.error(f"Camera device does not exist: {device_path}")
        raise FileNotFoundError(device_path)


@dataclass(slots=True, frozen=True)
class Config:
    # input
    source: str = _env("SOURCE", "file")
    video_path: Path | None = Path(_VIDEO_PATH) if _VIDEO_PATH else None
    camera_device: Path | None = Path(_CAMERA_DEVICE) if _CAMERA_DEVICE else None
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

    @property
    def camera_device_path(self) -> Path:
        return self.camera_device or Path(f"/dev/video{self.camera_index}")

    def validate(self) -> None:
        if self.is_webcam:
            _validate_camera_device(self.camera_device_path)
            return
        _validate_video_path(self.video_path)
