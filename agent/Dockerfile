FROM debian:bookworm-slim

LABEL org.opencontainers.image.source="https://github.com/himmat12/local-coding-agent"
LABEL org.opencontainers.image.name="local-coding-agent"
LABEL org.opencontainers.image.description="A Docker-based local coding agent that runs an Ollama model container and a Python agent container. The agent connects to Ollama over an internal bridge network and provides an interactive terminal experience."
LABEL org.opencontainers.image.licenses="MIT"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/agent \
    TMPDIR=/tmp \
    VENV_PATH=/opt/venv \
    PATH=/opt/venv/bin:$PATH

# Install minimal runtime tools + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    bash \
    git \
    coreutils \
    findutils \
    grep \
    sed \
    gawk \
    ca-certificates \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root agent user
RUN groupadd --gid 10001 agent && \
    useradd --uid 10001 --gid 10001 --create-home --shell /bin/bash agent

WORKDIR /app 

# Install Python dependencies as root (cache layer)
COPY /app/requirements.txt .
RUN python3 -m venv "$VENV_PATH" && \ 
    "$VENV_PATH/bin/pip" install --no-cache-dir -r requirements.txt

# Copy application code
COPY /app .

# Prepare directories (no /logs - use stdout logging)
RUN mkdir -p /tmp/agent && \
    chown -R agent:agent /app /tmp/agent /home/agent

USER agent

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/bin/bash"]