FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-gi python3-gst-1.0 python3-venv \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav gir1.2-gst-rtsp-server-1.0 \
  && rm -rf /var/lib/apt/lists/*

# venv
RUN python3 -m venv --system-site-packages /venv
ENV PATH="/venv/bin:${PATH}"
RUN pip install --no-cache-dir rich

# rest unchanged
WORKDIR /app
COPY rtsp_streamer/ rtsp_streamer/
CMD ["python", "-m", "rtsp_streamer"]
