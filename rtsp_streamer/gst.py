from __future__ import annotations
from dataclasses import dataclass
from .config import Config


@dataclass(slots=True)
class PipelineBuilder:
    cfg: Config
    _parts: list[str] | None = None

    def source(self) -> "PipelineBuilder":
        part = (
            f"v4l2src device={self.cfg.camera_device_path} do-timestamp=true"
            if self.cfg.is_webcam
            else f"filesrc location={self.cfg.video_path} ! decodebin"
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
    
    def leaky_queue(self) -> "PipelineBuilder":
        self._add("queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 leaky=downstream")
        return self

    def framerate(self) -> "PipelineBuilder":
        if self.cfg.framerate:
            self._add(f"videorate ! video/x-raw,framerate={self.cfg.framerate}/1")
        return self

    def encode_h264(self) -> "PipelineBuilder":
        fps = self.cfg.framerate or 25
        self._add(
            "videoconvert ! video/x-raw,format=I420 ! "
            "x264enc tune=zerolatency speed-preset=ultrafast "
            f"bitrate={self.cfg.bitrate} key-int-max={fps} "
            "bframes=0 rc-lookahead=0 sync-lookahead=0"
        )
        self._add("video/x-h264,profile=baseline,stream-format=byte-stream,alignment=au")
        self._add("h264parse config-interval=1")
        return self


    def payload_rtp(self, pt: int = 96) -> "PipelineBuilder":
        self._add(
            f"rtph264pay name=pay0 pt={pt} config-interval=1 mtu=1200 aggregate-mode=zero-latency"
        )
        return self


    def default_h264(self) -> str:
        return (
            PipelineBuilder(self.cfg)
            .source()
            .scale()
            .framerate()
            .leaky_queue()
            .encode_h264()
            .leaky_queue()
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
