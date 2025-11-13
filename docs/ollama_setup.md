# Running Ollama Outside Podman Compose

## Overview

For better performance, Ollama now runs directly on your host machine instead of inside a container. This provides significant speed improvements for LLM inference.

## Quick Setup

### First Time Setup

1. **Install and configure Ollama:**
   ```bash
   make setup-ollama
   ```
   
   This will:
   - Install Ollama (if not already installed)
   - Start the Ollama service
   - Pull the required model (`llama3.2:3b-instruct-fp16`)

2. **Start the RAG stack:**
   ```bash
   make start
   ```

### Manual Setup (Alternative)

If you prefer to set up Ollama manually:

1. **Install Ollama:**
   - **macOS:** Download from https://ollama.ai/download or `brew install ollama`
   - **Linux:** `curl -fsSL https://ollama.ai/install.sh | sh`
   - **Windows:** Download from https://ollama.ai/download

2. **Start Ollama service:**
   - On macOS/Windows: Ollama starts automatically after installation
   - On Linux: `ollama serve` (runs in foreground) or start as systemd service

3. **Pull the required model:**
   ```bash
   ollama pull llama3.2:3b-instruct-fp16
   ```

4. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/version
   ```

5. **Start the RAG stack:**
   ```bash
   make start
   ```

## How It Works

- **Ollama runs on host:** Port 11434 on your local machine
- **Containers connect to host:** Using `host.containers.internal:11434`
- **Better performance:** Direct hardware access without container overhead
- **Model persistence:** Models are stored in `~/.ollama` on your host

## Switching Models

To use a different model:

1. **Pull the new model:**
   ```bash
   ollama pull <model-name>
   ```

2. **Update the Makefile:**
   ```makefile
   OLLAMA_MODEL := <model-name>
   ```

3. **Update podman-compose.yml:**
   ```yaml
   environment:
     INFERENCE_MODEL: "<model-name>"
   ```

4. **Restart services:**
   ```bash
   make restart
   ```

## Troubleshooting

### Ollama not accessible from containers

If containers can't reach Ollama on the host:

1. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/version
   ```

2. **Check Ollama configuration:**
   ```bash
   # Ollama should be listening on all interfaces
   # Set environment variable if needed:
   export OLLAMA_HOST=0.0.0.0
   ollama serve
   ```

3. **Test connectivity from container:**
   ```bash
   podman exec -it rag-llamastack curl http://host.containers.internal:11434/api/version
   ```

### Slow model loading

The first request after starting may be slow as the model loads into memory. Subsequent requests will be much faster.

### Model not found

Ensure you've pulled the model:
```bash
ollama list  # List available models
ollama pull llama3.2:3b-instruct-fp16  # Pull required model
```

## Checking Status

### Check if Ollama is running
```bash
make check-ollama
```

### Test all services
```bash
make test-services
```

### View service configuration
```bash
make config
```

## Benefits of Running Ollama on Host

1. **Better Performance:** Direct access to CPU/GPU without container overhead
2. **Easier Updates:** Update Ollama independently of containers
3. **Model Sharing:** Use the same Ollama instance for multiple projects
4. **Resource Management:** Better control over Ollama's resource usage
5. **Faster Startup:** No need to wait for Ollama container to download models

## Reverting to Containerized Ollama

If you need to run Ollama in a container again, check the git history for the previous `podman-compose.yml` configuration:

```bash
git log --all --full-history -- deploy/local/podman-compose.yml
git show <commit-hash>:deploy/local/podman-compose.yml > podman-compose.yml
```

