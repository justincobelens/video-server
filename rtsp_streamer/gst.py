from __future__ import annotations
from dataclasses import dataclass
from .config import Config


@dataclass(slots=True)
class PipelineBuilder:
    cfg: Config
    _parts: list[str] | None = None

    def source(self) -> "PipelineBuilder":
        part = (
            f"v4l2src device=/dev/video{self.cfg.camera_index} ! videoconvert"
            if self.cfg.is_webcam
            else f"filesrc location={self.cfg.video_path} ! decodebin ! videoconvert"
        )
        self._add(part)
        return self

    def scale(self) -> "PipelineBuilder":
        if self.cfg.width and self.cfg.height:
            self._add(
                "videoscale ! "
                f"video/x-raw,width={self.cfg.width},height={self.cfg.height}"
            )
        return self

    def framerate(self) -> "PipelineBuilder":
        if self.cfg.framerate:
            self._add(f"videorate ! video/x-raw,framerate={self.cfg.framerate}/1")
        return self

    def encode_h264(self) -> "PipelineBuilder":
        self._add(
            "x264enc tune=zerolatency "
            f"speed-preset=ultrafast bitrate={self.cfg.bitrate}"
        )
        return self

    def payload_rtp(self, pt: int = 96) -> "PipelineBuilder":
        self._add(f"rtph264pay name=pay0 pt={pt} ")
        return self

    def default_h264(self) -> str:
        return (
            PipelineBuilder(self.cfg)
            .source()
            .scale()
            .framerate()
            .encode_h264()
            .payload_rtp()
            .build()
        )

    def _add(self, segment: str) -> None:
        if self._parts is None:
            self._parts = []
        self._parts.append(segment)

    def build(self) -> str:
        if not self._parts:
            raise RuntimeError("pipeline is empty")
        return " ! ".join(self._parts)
