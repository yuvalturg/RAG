# Makefile for RAG Deployment
# Replaces the original deploy.sh script with additional uninstall functionality

# Color definitions
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# NAMESPACE check will be done in individual targets that need it

MAKEFLAGS += --no-print-directory

# Set default target
.DEFAULT_GOAL := help

# Default values
POSTGRES_USER ?= postgres
POSTGRES_PASSWORD ?= rag_password
POSTGRES_DBNAME ?= rag_blueprint
MINIO_USER ?= minio_rag_user
MINIO_PASSWORD ?= minio_rag_password
# HF_TOKEN will be managed by the get_hf_token helper function
RAG_CHART := rag
TOLERATIONS_TEMPLATE=[{"key":"$(1)","effect":"NoSchedule","operator":"Exists"}]

# Values file management
VALUES_FILE := rag-values.yaml
VALUES_EXAMPLE := rag-values.yaml.example

# Helper function to check and create values file
define check_values_file
	@if [ ! -f "$(VALUES_FILE)" ]; then \
		if [ -f "$(VALUES_EXAMPLE)" ]; then \
			echo "$(YELLOW)[INFO]$(NC) Values file not found. Creating from example..."; \
			cp "$(VALUES_EXAMPLE)" "$(VALUES_FILE)"; \
			echo ""; \
			echo "$(GREEN)╔══════════════════════════════════════════════════════════════════════════╗$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(YELLOW)⚠️  IMPORTANT: Configuration Required$(GREEN)      	                           ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(NC)Configuration file has been initialized: $(BLUE)rag-values.yaml$(GREEN)     	   ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(YELLOW)Before continuing, you MUST configure at least:$(GREEN)                         ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(RED)1. Enable at least ONE model$(GREEN) in the global.models section               ║$(NC)"; \
			echo "$(GREEN)║     $(NC)Set $(BLUE)enabled: true$(NC) for your chosen model$(GREEN)                            ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(YELLOW)2. Add your Hugging Face token$(GREEN) (required for model downloads)           ║$(NC)"; \
			echo "$(GREEN)║     $(NC)Get token from: $(BLUE)https://huggingface.co/settings/tokens$(GREEN)              ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(YELLOW)3. (Optional)$(NC) Add TAVILY API key for web search functionality$(GREEN)          ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║  $(BLUE)📝 ACTION REQUIRED:$(GREEN)                                                     ║$(NC)"; \
			echo "$(GREEN)║     $(NC)Open a new terminal window and edit the configuration file:$(GREEN)         ║$(NC)"; \
			echo "$(GREEN)║     $(BLUE)nano rag-values.yaml$(GREEN)  or  $(BLUE)vim rag-values.yaml$(GREEN)                        ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)║     $(NC)After editing, save the file and return here to continue.$(GREEN)           ║$(NC)"; \
			echo "$(GREEN)║                                                                          ║$(NC)"; \
			echo "$(GREEN)╚══════════════════════════════════════════════════════════════════════════╝$(NC)"; \
			echo ""; \
			echo "$(YELLOW)[WAITING]$(NC) Configure rag-values.yaml in another terminal, then press Enter..."; \
			read -p "" continue; \
			echo "$(BLUE)[INFO]$(NC) Continuing with installation..."; \
			echo ""; \
		else \
			echo "$(RED)[ERROR]$(NC) Neither $(VALUES_FILE) nor $(VALUES_EXAMPLE) found."; \
			echo "$(BLUE)[INFO]$(NC) Please create $(VALUES_FILE) with your configuration."; \
			exit 1; \
		fi; \
	fi; \
	$(call validate_values_file)
endef

# Helper function to validate values file
define validate_values_file
	echo "$(BLUE)[INFO]$(NC) Validating configuration values..."; \
	HF_TOKEN=$$(grep "^hf_token:" "$(VALUES_FILE)" 2>/dev/null | sed 's/hf_token: *//' | tr -d '"' | tr -d ' '); \
	LLAMA_STACK_TAVILY=$$(grep "TAVILY_SEARCH_API_KEY:" "$(VALUES_FILE)" 2>/dev/null | sed 's/.*TAVILY_SEARCH_API_KEY: *//' | tr -d '"' | tr -d ' '); \
	UPDATED=0; \
	if [ -z "$$HF_TOKEN" ] || [ "$$HF_TOKEN" = "" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) Hugging Face token is not set. Model downloads may fail."; \
		echo "$(BLUE)[INFO]$(NC) Get your token from: https://huggingface.co/settings/tokens"; \
		echo ""; \
		read -p "Enter your Hugging Face token (or press Enter to skip): " hf_input; \
		if [ -n "$$hf_input" ]; then \
			sed -i.bak "s/^hf_token:.*/hf_token: \"$$hf_input\"/" "$(VALUES_FILE)"; \
			echo "$(GREEN)[SUCCESS]$(NC) Hugging Face token saved to configuration."; \
			UPDATED=1; \
		else \
			echo "$(YELLOW)[WARNING]$(NC) Hugging Face token not provided. Model downloads may fail."; \
		fi; \
		echo ""; \
	fi; \
	if [ -z "$$LLAMA_STACK_TAVILY" ] || [ "$$LLAMA_STACK_TAVILY" = "Paste-your-key-here" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) TAVILY search API key is not set. Web search will be disabled."; \
		echo "$(BLUE)[INFO]$(NC) Get your key from: https://tavily.com/"; \
		echo ""; \
		read -p "Enter your TAVILY search API key (or press Enter to skip): " tavily_input; \
		if [ -n "$$tavily_input" ]; then \
			sed -i.bak "s/TAVILY_SEARCH_API_KEY:.*/TAVILY_SEARCH_API_KEY: \"$$tavily_input\"/" "$(VALUES_FILE)"; \
			echo "$(GREEN)[SUCCESS]$(NC) TAVILY search API key saved to configuration."; \
			UPDATED=1; \
		else \
			echo "$(YELLOW)[WARNING]$(NC) TAVILY search API key not provided. Web search will be disabled."; \
		fi; \
		echo ""; \
	fi; \
	if [ $$UPDATED -eq 1 ]; then \
		echo "$(GREEN)[SUCCESS]$(NC) Configuration updated. Proceeding with installation..."; \
		echo ""; \
	fi; \
	rm -f "$(VALUES_FILE).bak" 2>/dev/null || true
endef

# If using extra tools that require API Keys set the LLAMA_STACK_ENV variable with key, value pairs
# LLAMA_STACK_ENV ?= {Key1: "Value1", Key2: "Value2" etc.}

#ingestion pipeline configuration
SOURCE ?= S3
EMBEDDING_MODEL ?= all-MiniLM-L6-v2
INGESTION_PIPELINE_NAME ?= demo-rag-vector-db
INGESTION_PIPELINE_VERSION ?= 1.0
ACCESS_KEY_ID ?= $(MINIO_USER)
SECRET_ACCESS_KEY ?= $(MINIO_PASSWORD)
BUCKET_NAME ?= documents
ENDPOINT_URL ?= http://minio:9000
REGION ?= us-east-1
# PDF file path variable for upload-pdf target
PDF_DIR = ../../notebooks
S3_TEMPLATE={"access_key_id":"$(1)","secret_access_key":"$(2)","bucket_name":"$(3)","endpoint_url":"$(4)","region":"$(5)"}

# CUSTOM VALUES (full path) FOR EXTRA INGESTION PIPELINE
# CUSTOM_INGESTION_PIPELINE_VALUES = ~/my-values.yaml
# CUSTOM_INGESTION_PIPELINE_NAME ?= my-pipeline

helm_pgvector_args = \
    --set pgvector.secret.user=$(POSTGRES_USER) \
    --set pgvector.secret.password=$(POSTGRES_PASSWORD) \
    --set pgvector.secret.dbname=$(POSTGRES_DBNAME)

helm_minio_args = \
    --set minio.secret.user=$(MINIO_USER) \
    --set minio.secret.password=$(MINIO_PASSWORD)

helm_llm_service_args = \
    --set llm-service.secret.hf_token=$(HF_TOKEN) \
    $(if $(DEVICE),--set llm-service.device='$(DEVICE)',) \
    $(if $(LLM),--set global.models.$(LLM).enabled=true,) \
    $(if $(SAFETY),--set global.models.$(SAFETY).enabled=true,) \
    $(if $(LLM_TOLERATION),--set-json global.models.$(LLM).tolerations='$(call TOLERATIONS_TEMPLATE,$(LLM_TOLERATION))',) \
    $(if $(SAFETY_TOLERATION),--set-json global.models.$(SAFETY).tolerations='$(call TOLERATIONS_TEMPLATE,$(SAFETY_TOLERATION))',) \
    $(if $(RAW_DEPLOYMENT),--set llm-service.rawDeploymentMode=$(RAW_DEPLOYMENT),)

helm_llama_stack_args = \
    $(if $(LLM),--set global.models.$(LLM).enabled=true,) \
    $(if $(SAFETY),--set global.models.$(SAFETY).enabled=true,) \
    $(if $(LLM_URL),--set global.models.$(LLM).url='$(LLM_URL)',) \
    $(if $(SAFETY_URL),--set global.models.$(SAFETY).url='$(SAFETY_URL)',) \
    $(if $(LLM_API_TOKEN),--set global.models.$(LLM).apiToken='$(LLM_API_TOKEN)',) \
    $(if $(SAFETY_API_TOKEN),--set global.models.$(SAFETY).apiToken='$(SAFETY_API_TOKEN)',) \
    $(if $(LLAMA_STACK_ENV),--set-json llama-stack.secrets='$(LLAMA_STACK_ENV)',) \
    $(if $(RAW_DEPLOYMENT),--set llama-stack.rawDeploymentMode=$(RAW_DEPLOYMENT),)

helm_ingestion_args = \
	$(if $(SOURCE),--set ingestion-pipeline.source='$(SOURCE)',) \
	$(if $(EMBEDDING_MODEL),--set ingestion-pipeline.embedding_model='$(EMBEDDING_MODEL)',) \
	$(if $(INGESTION_PIPELINE_NAME),--set ingestion-pipeline.name='$(INGESTION_PIPELINE_NAME)',) \
	$(if $(INGESTION_PIPELINE_VERSION),--set ingestion-pipeline.version='$(INGESTION_PIPELINE_VERSION)',) \
    $(if $(SOURCE),--set-json ingestion-pipeline.S3='$(call S3_TEMPLATE,$(ACCESS_KEY_ID),$(SECRET_ACCESS_KEY),$(BUCKET_NAME),$(ENDPOINT_URL),$(REGION))',)

# Default target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)RAG Stack Helm Deployment$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC) make [TARGET]"
	@echo ""
	@echo "$(GREEN)Main Targets:$(NC)"
	@echo "  install       - Install RAG deployment"
	@echo "  uninstall     - Uninstall RAG deployment"
	@echo "  status        - Check deployment status"
	@echo "  logs          - Show application logs"
	@echo "  health        - Check health of all services"
	@echo ""
	@echo "$(GREEN)Development Targets:$(NC)"
	@echo "  dev           - Start development environment"
	@echo "  validate      - Validate Helm chart"
	@echo "  validate-config - Validate configuration values"
	@echo "  monitor       - Monitor deployment status"
	@echo "  config        - Show current configuration"
	@echo ""
	@echo "$(GREEN)Management Targets:$(NC)"
	@echo "  backup        - Backup PVCs and secrets"
	@echo "  restore       - Restore from backup"
	@echo "  clean         - Clean up all resources including namespace"
	@echo "  init-config   - Initialize configuration from example"
	@echo "  configure-keys - Interactively configure API keys"
	@echo "  edit-config   - Edit configuration file"
	@echo "  show-config   - Show current configuration"
	@echo ""
	@echo "$(GREEN)Configuration:$(NC)"
	@echo "  NAMESPACE     - Target namespace (required)"
	@echo "  VALUES_FILE   - Configuration file (default: rag-values.yaml)"
	@echo "  All other settings are managed in the values file"
	@echo ""
	@echo "$(GREEN)Quick Start:$(NC)"
	@echo "  1. make init-config  # Create configuration from example"
	@echo "  2. make configure-keys  # Set up API keys interactively"
	@echo "  3. make install NAMESPACE=my-rag  # Install with your config"

# Dependency checks
.PHONY: check-deps
check-deps: ## Check required dependencies
	@command -v helm >/dev/null 2>&1 || { echo "$(RED)[ERROR]$(NC) helm is not installed"; exit 1; }
	@command -v oc >/dev/null 2>&1 || { echo "$(RED)[ERROR]$(NC) oc is not installed"; exit 1; }
	@echo "$(GREEN)[SUCCESS]$(NC) All dependencies are installed."

# Namespace validation
.PHONY: check-namespace
check-namespace: ## Check if namespace exists and is accessible
	@oc get namespace $(NAMESPACE) >/dev/null 2>&1 || { echo "$(RED)[ERROR]$(NC) Namespace $(NAMESPACE) does not exist or is not accessible"; exit 1; }

# Configuration management
.PHONY: config
config: ## Show current configuration
	@echo "$(BLUE)[INFO]$(NC) Current configuration:"
	@echo "  Namespace: $(NAMESPACE)"
	@echo "  Values file: $(VALUES_FILE)"
	@if [ -f "$(VALUES_FILE)" ]; then \
		echo "  Configuration: Found"; \
		echo "$(BLUE)[INFO]$(NC) Key settings from $(VALUES_FILE):"; \
		grep -E "^(hf_token|tavily_search_api_key|TAVILY_SEARCH_API_KEY):" "$(VALUES_FILE)" 2>/dev/null || echo "  No API keys found"; \
		echo "$(BLUE)[INFO]$(NC) Model configuration:"; \
		grep -A 5 "global:" "$(VALUES_FILE)" 2>/dev/null | grep -E "(models|enabled)" || echo "  No models configured"; \
	else \
		echo "  Configuration: Not found"; \
		echo "$(YELLOW)[WARNING]$(NC) Run 'make init-config' to create configuration file"; \
	fi

.PHONY: init-config
init-config: ## Initialize configuration from example
	@if [ -f "$(VALUES_FILE)" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) $(VALUES_FILE) already exists."; \
		echo "$(BLUE)[INFO]$(NC) Use 'make edit-config' to modify it, or remove it first."; \
	else \
		if [ -f "$(VALUES_EXAMPLE)" ]; then \
			cp "$(VALUES_EXAMPLE)" "$(VALUES_FILE)"; \
			echo "$(GREEN)[SUCCESS]$(NC) Created $(VALUES_FILE) from $(VALUES_EXAMPLE)"; \
			echo "$(BLUE)[INFO]$(NC) Please edit $(VALUES_FILE) with your configuration:"; \
			echo "  - hf_token: Your Hugging Face token"; \
			echo "  - tavily_search_api_key: Your TAVILY search API key (optional)"; \
			echo "  - global.models: Configure your LLM and safety models"; \
			echo "  - llama-stack.secrets.TAVILY_SEARCH_API_KEY: Set TAVILY key for web search"; \
			echo ""; \
			echo "$(BLUE)[INFO]$(NC) You can edit it with: make edit-config"; \
		else \
			echo "$(RED)[ERROR]$(NC) $(VALUES_EXAMPLE) not found."; \
			exit 1; \
		fi; \
	fi

.PHONY: edit-config
edit-config: ## Edit configuration file
	@if [ -f "$(VALUES_FILE)" ]; then \
		echo "$(BLUE)[INFO]$(NC) Opening $(VALUES_FILE) for editing..."; \
		$${EDITOR:-nano} "$(VALUES_FILE)"; \
	else \
		echo "$(YELLOW)[WARNING]$(NC) $(VALUES_FILE) not found. Creating from example..."; \
		$(MAKE) init-config; \
		$${EDITOR:-nano} "$(VALUES_FILE)"; \
	fi

.PHONY: show-config
show-config: ## Show configuration file contents
	@if [ -f "$(VALUES_FILE)" ]; then \
		echo "$(BLUE)[INFO]$(NC) Contents of $(VALUES_FILE):"; \
		echo ""; \
		cat "$(VALUES_FILE)"; \
	else \
		echo "$(YELLOW)[WARNING]$(NC) $(VALUES_FILE) not found."; \
		echo "$(BLUE)[INFO]$(NC) Run 'make init-config' to create it."; \
	fi

# Configuration validation (moved to validation section)


# Create namespace and deploy
namespace:
	@echo "$(BLUE)[INFO]$(NC) Creating namespace $(NAMESPACE)..."
	@oc create namespace $(NAMESPACE) &> /dev/null && oc label namespace $(NAMESPACE) modelmesh-enabled=false ||:
	@oc project $(NAMESPACE) &> /dev/null ||:
	@echo "$(GREEN)[SUCCESS]$(NC) Namespace $(NAMESPACE) is ready"

# Development targets
.PHONY: dev
dev: ## Start development environment
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for dev"; exit 1; fi
	@$(MAKE) check-deps
	@$(MAKE) validate-config
	@echo "$(BLUE)[INFO]$(NC) Starting RAG development environment..."
	@$(call check_values_file)
	@$(MAKE) install
	@echo "$(GREEN)[SUCCESS]$(NC) Development environment started"

# Validation targets
.PHONY: validate
validate: check-deps ## Validate Helm chart before installation
	@echo "$(BLUE)[INFO]$(NC) Validating Helm chart..."
	@helm lint $(RAG_CHART)
	@helm template $(RAG_CHART) --dry-run
	@echo "$(GREEN)[SUCCESS]$(NC) Helm chart validation passed"

.PHONY: validate-config
validate-config: ## Validate configuration values
	@if [ ! -f "$(VALUES_FILE)" ]; then \
		echo "$(RED)[ERROR]$(NC) Configuration file $(VALUES_FILE) not found."; \
		echo "$(BLUE)[INFO]$(NC) Run 'make init-config' to create it from example."; \
		exit 1; \
	fi
	@$(call validate_values_file)

.PHONY: configure-keys
configure-keys: ## Interactively configure API keys
	@if [ ! -f "$(VALUES_FILE)" ]; then \
		echo "$(RED)[ERROR]$(NC) Configuration file $(VALUES_FILE) not found."; \
		echo "$(BLUE)[INFO]$(NC) Run 'make init-config' to create it from example."; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) Interactive API key configuration..."; \
	echo ""; \
	read -p "Enter your Hugging Face token (or press Enter to skip): " hf_input; \
	if [ -n "$$hf_input" ]; then \
		sed -i.bak "s/^hf_token:.*/hf_token: \"$$hf_input\"/" "$(VALUES_FILE)"; \
		echo "$(GREEN)[SUCCESS]$(NC) Hugging Face token saved to configuration."; \
	else \
		echo "$(YELLOW)[WARNING]$(NC) Hugging Face token not provided."; \
	fi; \
	echo ""; \
	read -p "Enter your TAVILY search API key (or press Enter to skip): " tavily_input; \
	if [ -n "$$tavily_input" ]; then \
		sed -i.bak "s/TAVILY_SEARCH_API_KEY:.*/TAVILY_SEARCH_API_KEY: \"$$tavily_input\"/" "$(VALUES_FILE)"; \
		echo "$(GREEN)[SUCCESS]$(NC) TAVILY search API key saved to configuration."; \
	else \
		echo "$(YELLOW)[WARNING]$(NC) TAVILY search API key not provided."; \
	fi; \
	echo ""; \
	echo "$(GREEN)[SUCCESS]$(NC) Configuration updated."; \
	rm -f "$(VALUES_FILE).bak" 2>/dev/null || true

# Monitoring targets
.PHONY: monitor
monitor: ## Monitor deployment status
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for monitor"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Monitoring deployment status (press Ctrl+C to stop)..."
	@watch -n 5 "oc get pods -n $(NAMESPACE)"

# Logging targets
.PHONY: logs
logs: ## Show logs for all pods
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for logs"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Showing logs for all pods..."
	@oc logs -n $(NAMESPACE) -l app=llamastack --tail=100

.PHONY: logs-llm
logs-llm: ## Show logs for LLM service
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for logs-llm"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Showing logs for LLM service..."
	@oc logs -n $(NAMESPACE) -l app=llm-service --tail=100

# Health check targets
.PHONY: health
health: ## Check health of all services
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for health"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Checking service health..."
	@oc get pods -n $(NAMESPACE) -o wide
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) Checking service endpoints..."
	@oc get svc -n $(NAMESPACE)
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) Checking routes..."
	@oc get routes -n $(NAMESPACE)

# Backup and restore targets
.PHONY: backup
backup: ## Backup PVCs and secrets
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for backup"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Creating backup of PVCs and secrets..."
	@mkdir -p backups/$(NAMESPACE)
	@oc get pvc -n $(NAMESPACE) -o yaml > backups/$(NAMESPACE)/pvcs.yaml
	@oc get secrets -n $(NAMESPACE) -o yaml > backups/$(NAMESPACE)/secrets.yaml
	@echo "$(GREEN)[SUCCESS]$(NC) Backup created in backups/$(NAMESPACE)/"

.PHONY: restore
restore: ## Restore from backup
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for restore"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Restoring from backup..."
	@oc apply -f backups/$(NAMESPACE)/pvcs.yaml
	@oc apply -f backups/$(NAMESPACE)/secrets.yaml
	@echo "$(GREEN)[SUCCESS]$(NC) Restore completed"

# Cleanup targets
.PHONY: clean
clean: ## Clean up all resources including namespace
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for clean"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Cleaning up all resources..."
	@$(MAKE) uninstall
	@oc delete project $(NAMESPACE) || true
	@echo "$(GREEN)[SUCCESS]$(NC) Cleanup completed"

# Configuration file management
.PHONY: clean-config
clean-config: ## Remove configuration file
	@if [ -f "$(VALUES_FILE)" ]; then \
		rm "$(VALUES_FILE)"; \
		echo "$(GREEN)[SUCCESS]$(NC) Configuration file $(VALUES_FILE) removed."; \
	else \
		echo "$(BLUE)[INFO]$(NC) No configuration file found."; \
	fi

.PHONY: depend
depend: ## Update Helm dependencies
	@echo "$(BLUE)[INFO]$(NC) Updating Helm dependencies..."
	@helm dependency update $(RAG_CHART) &> /dev/null
	@echo "$(GREEN)[SUCCESS]$(NC) Helm dependencies updated"

.PHONY: list-models
list-models: depend ## List available models
	@echo "$(BLUE)[INFO]$(NC) Listing available models..."
	@helm template dummy-release $(RAG_CHART) --set llm-service._debugListModels=true | grep ^model:

.PHONY: list-mcps
list-mcps: depend ## List available MCP servers
	@echo "$(BLUE)[INFO]$(NC) Listing available MCP servers..."
	@helm template dummy-release $(RAG_CHART) --set mcp-servers._debugListMcps=true | grep ^MCP

.PHONY: install
install: ## Install the RAG deployment
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for install"; exit 1; fi
	@$(MAKE) check-deps
	@$(MAKE) namespace
	@$(MAKE) depend
	@$(MAKE) delete-jobs
	@$(call check_values_file)
	@echo "$(BLUE)[INFO]$(NC) Installing $(RAG_CHART) helm chart with $(VALUES_FILE)..."
	@helm -n $(NAMESPACE) upgrade --install $(RAG_CHART) $(RAG_CHART) -n $(NAMESPACE) \
		-f $(VALUES_FILE) \
		$(EXTRA_HELM_ARGS)
	@echo "$(BLUE)[INFO]$(NC) Waiting for model services and llamastack to deploy. It may take around 10-15 minutes depending on the size of the model..."
	@oc rollout status deploy/llamastack
	@echo "$(GREEN)[SUCCESS]$(NC) $(RAG_CHART) installed successfully"

# Install with TAVILY integration (deprecated - use values file instead)
.PHONY: install-with-tavily
install-with-tavily: check-deps validate-config ## Install with TAVILY search integration (deprecated)
	@echo "$(YELLOW)[WARNING]$(NC) install-with-tavily is deprecated. Use values file approach instead."
	@echo "$(BLUE)[INFO]$(NC) Please configure TAVILY in your $(VALUES_FILE) and use 'make install'"
	@$(MAKE) install

# Uninstall the deployment and clean up
.PHONY: uninstall
uninstall: ## Uninstall the RAG deployment and clean up resources
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for uninstall"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Uninstalling $(RAG_CHART) helm chart..."
	@helm -n $(NAMESPACE) uninstall $(RAG_CHART)
	@echo "$(BLUE)[INFO]$(NC) Removing pgvector and minio PVCs from $(NAMESPACE)..."
	@oc get pvc -n $(NAMESPACE) -o custom-columns=NAME:.metadata.name | grep -E '^(pg|minio)-data' | xargs -I {} oc delete pvc -n $(NAMESPACE) {} ||:
	@echo "$(BLUE)[INFO]$(NC) Deleting remaining pods in namespace $(NAMESPACE)..."
	@oc delete pods -n $(NAMESPACE) --all
	@echo "$(YELLOW)[INFO]$(NC) Checking for any remaining resources in namespace $(NAMESPACE)..."
	@echo "$(BLUE)[INFO]$(NC) If you want to completely remove the namespace, run: oc delete project $(NAMESPACE)"
	@echo "$(BLUE)[INFO]$(NC) Remaining resources in namespace $(NAMESPACE):"
	@$(MAKE) status
	@echo "$(GREEN)[SUCCESS]$(NC) Uninstall completed"

# Install extra ingestion pipelines (removed duplicate)

# Check deployment status
.PHONY: status
status: ## Check status of the deployment
	@if [ -z "$(NAMESPACE)" ]; then echo "$(RED)[ERROR]$(NC) NAMESPACE is required for status"; exit 1; fi
	@echo "$(BLUE)[INFO]$(NC) Listing pods..."
	@oc get pods -n $(NAMESPACE) || true
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) Listing services..."
	@oc get svc -n $(NAMESPACE) || true
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) Listing routes..."
	@oc get routes -n $(NAMESPACE) || true
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) Listing secrets..."
	@oc get secrets -n $(NAMESPACE) | grep huggingface-secret || true
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) Listing pvcs..."
	@oc get pvc -n $(NAMESPACE) || true

# Install extra ingestion pipelines
.PHONY: install-ingestion-pipeline
install-ingestion-pipeline: ## Install extra ingestion pipelines
	@echo "$(BLUE)[INFO]$(NC) Installing extra ingestion pipeline..."
	@helm -n $(NAMESPACE) install $(CUSTOM_INGESTION_PIPELINE_NAME) rag/charts/ingestion-pipeline-0.1.0.tgz -f $(CUSTOM_INGESTION_PIPELINE_VALUES)
	@echo "$(GREEN)[SUCCESS]$(NC) Extra ingestion pipeline installed"

# Delete all jobs in the namespace
.PHONY: delete-jobs
delete-jobs: ## Delete all jobs in the namespace
	@echo "$(BLUE)[INFO]$(NC) Deleting all jobs in namespace $(NAMESPACE)..."
	@oc delete jobs -n $(NAMESPACE) --all ||:
	@echo "$(GREEN)[SUCCESS]$(NC) Job deletion completed"
