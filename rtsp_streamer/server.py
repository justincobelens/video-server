from __future__ import annotations

import logging
import socket

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer, GLib  # type: ignore
# from rich.logging import RichHandler

from .config import Config
from .gst import PipelineBuilder

log = logging.getLogger("rtsp_streamer.server")


class RTSPServer:
    def __init__(self, cfg: Config) -> None:
        if cfg.is_webcam:
            log.info(f"Using webcam source: {cfg.camera_device_path}")
        else:
            log.info(f"Using file source: {cfg.video_path}")
        cfg.validate()
        self.cfg = cfg

        factory = GstRtspServer.RTSPMediaFactory()
        launch_str = PipelineBuilder(cfg).default_h264()
        factory.set_launch(launch_str)
        factory.set_shared(True)

        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(str(cfg.rtsp_port))
        self.server.get_mount_points().add_factory(cfg.mount_point, factory)

        # factory.set_protocols(GstRtspServer.RTSPLowerTrans.UDP)

    def start(self) -> None:
        self.server.attach(None)
        host = socket.gethostname()
        log.info(
            "RTSP started  ➜  [link = rtsp://%s:%s%s[/link]",
            host,
            self.cfg.rtsp_port,
            self.cfg.mount_point,
        )
        GLib.MainLoop().run()
