<!-- omit from toc -->
# Local Deployment
This guide walks you through running a Llama Stack server locally using **Ollama** and **Podman**.

<!-- omit from toc -->
## Table of Contents
- [Prerequisites](#prerequisites)
- [Supported Models](#supported-models)
- [Installing the RAG QuickStart](#installing-the-rag-quickstart)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Start Ollama Server](#2-start-ollama-server)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Run Llama Stack with Podman](#4-run-llama-stack-with-podman)
- [Using the RAG UI](#using-the-rag-ui)
- [Environment Variables](#environment-variables)
- [Redeploying Changes](#redeploying-changes)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- [Podman](https://podman.io/docs/installation) or Docker
- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- [Ollama](https://ollama.com/download)

Verify installation:

```bash
podman --version
python3 --version
uv --version
ollama --version
```

Note: `uv` is used for fast Python package management and virtual environment handling. Also, `docker` works as well as podman.

## Supported Models

| Function    | Model Name                             | Hardware    | Local Support |
|-------------|----------------------------------------|-------------|---------------|
| Embedding   | `all-MiniLM-L6-v2`                     | CPU/GPU     | ✓             |
| Generation  | `meta-llama/Llama-3.2-3B-Instruct`     | CPU/GPU     | ✓             |

Note: Local deployment primarily supports CPU and GPU acceleration through Ollama. The models are automatically downloaded when first requested.

## Installing the RAG QuickStart

### 1. Clone Repository

Clone the repo so you have a working copy

```bash
git clone https://github.com/rh-ai-quickstart/RAG
```

### 2. Start Ollama Server

Use the following command to launch the Ollama model:

```bash
ollama run llama3.2:3b-instruct-fp16 --keepalive 60m
```

Note: This will keep the model in memory for 60 minutes.

### 3. Configure Environment Variables

Launch a new terminal window to set the necessary environment variables:

```bash
export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"
export LLAMA_STACK_PORT=8321
```

### 4. Run Llama Stack with Podman

Pull the Docker image:

```bash
podman pull docker.io/llamastack/distribution-ollama
```

Create a local directory for persistent data:

```bash
mkdir -p ~/.llama
```

Run the container:

```bash
podman run -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.containers.internal:11434 \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT
```

Optional: Use a custom network:

```bash
podman network create llama-net
podman run --privileged --network llama-net -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT
```

Verify the container is running:

```bash
podman ps
```

Note: Another option is to connect to a remote Llama Stack Service. Based on the instructions of this quickstart, you should have one running in cluster and you can use `oc port-forward` to make it available on localhost.

```bash
oc get services -l app.kubernetes.io/name=llamastack

oc port-forward svc/llamastack 8321:8321
```

This makes the remote Service available at localhost:8321

## Using the RAG UI

1. Navigate to the frontend directory

```bash
cd frontend
```

2. Run the RAG UI application using the provided start script

```bash
./start.sh
```

This script will automatically:
- Create a virtual environment (if it doesn't exist)
- Install/sync all dependencies with `uv sync`
- Start the Streamlit server with auto-reload enabled
- Watch for file changes and automatically restart

3. Open your browser to the displayed URL (typically `http://localhost:8501`)

4. Upload your PDF documents through the UI and start asking questions!

## Environment Variables

The RAG UI supports the following optional environment variables for configuration:

| Environment Variable       | Description                                    | Default Value             |
|----------------------------|------------------------------------------------|---------------------------|
| `LLAMA_STACK_ENDPOINT`     | The endpoint for the Llama Stack API server    | `http://localhost:8321`   |
| `FIREWORKS_API_KEY`        | API key for Fireworks AI provider (optional)   | (empty string)            |
| `TOGETHER_API_KEY`         | API key for Together AI provider (optional)    | (empty string)            |
| `SAMBANOVA_API_KEY`        | API key for SambaNova provider (optional)      | (empty string)            |
| `OPENAI_API_KEY`           | API key for OpenAI provider (optional)         | (empty string)            |
| `TAVILY_SEARCH_API_KEY`    | API key for Tavily search provider (optional)  | (empty string)            |

**Note**: For the default local deployment using Ollama, you typically only need to ensure `LLAMA_STACK_ENDPOINT` points to your running Llama Stack server. The API keys are only needed if you want to use external AI providers instead of the local Ollama setup.

To set environment variables before starting the UI:

```bash
export LLAMA_STACK_ENDPOINT=http://localhost:8321
./start.sh
```

## Redeploying Changes

Deployment after making changes requires a rebuild of the container image using either `docker` or `podman`. Replace `docker.io` with your target container registry such as `quay.io`.

Note: Use your favorite repository, organization and image name

```bash
export CONTAINER_REGISTRY=docker.io # quay.io
export CONTAINER_ORGANIZATION=yourorg
export IMAGE_NAME=rag
export IMAGE_TAG=1.0.0
```

Build the image:

```bash
podman buildx build --platform linux/amd64,linux/arm64 -t $CONTAINER_REGISTRY/$CONTAINER_ORGANIZATION/$IMAGE_NAME:$IMAGE_TAG -f Containerfile .
```

Login to registry:

```bash
podman login $CONTAINER_REGISTRY
```

Push the image:

```bash
podman push $CONTAINER_REGISTRY/$CONTAINER_ORGANIZATION/$IMAGE_NAME:$IMAGE_TAG
```

Add modification to `deploy/helm/rag/values.yaml`, replacing the placeholders with your values:

```yaml
image:
  repository: {CONTAINER_REGISTRY}/{CONTAINER_ORGANIZATION}/{IMAGE_NAME}
  pullPolicy: IfNotPresent
  tag: {IMAGE_TAG}
```

To redeploy to the cluster run the same `make` command as you did before.

## Troubleshooting

**Check if Podman is running:**

```bash
podman ps
```

**Reinstall dependencies if needed:**

```bash
uv sync --reinstall
```

**Test the client in Python:**

```bash
uv run python -c "from llama_stack_client import LlamaStackClient; print(LlamaStackClient)"
```

**Check uv environment:**

```bash
uv pip list
```

**Run commands in the uv environment:**

```bash
uv run <command>
```

**Reset the entire environment:**

```bash
rm -rf .venv
uv sync
```

