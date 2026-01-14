from __future__ import annotations

import logging
from pathlib import Path

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa: E402

from .config import Config
from .server import RTSPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)


def list_clips(folder: Path) -> None:
    files = sorted(p.name for p in folder.glob("*") if p.is_file())
    logging.info("Videos in %s: %s", folder, ", ".join(files) or "none")


def main() -> None:
    Gst.init(None)

    cfg = Config()
    list_clips(Path("/videos"))
    RTSPServer(cfg).start()


if __name__ == "__main__":
    main()
