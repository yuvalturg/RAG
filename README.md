<!-- omit from toc -->
# RAG QuickStart

Retrieval-Augmented Generation (RAG) enhances Large Language Models (LLMs) by retrieving relevant external knowledge to improve accuracy, reduce hallucinations, and support domain-specific conversations.

This QuickStart allows users to explore the capabilities of RAG by:
- Uploading documents to be embedded
- Tweaking sampling parameters to influence LLM responses.
- Using custom system prompts
- Switching between simple and agent based RAG
- Switching between standard agents and ReAct agents.
<!-- omit from toc -->
## Table of Contents
- [Architecture](#architecture)
- [Deployment](#deployment)




## Architecture
![RAG System Architecture](docs/img/rag-architecture.png)

*This diagram illustrates both the ingestion pipeline for document processing and the RAG pipeline for query handling. For more details click [here](docs/rag-reference-architecture.md).*

| Layer/Component | Technology | Purpose/Description |
|-----------------|------------|---------------------|
| **Orchestration** | OpenShift AI | Container orchestration and GPU acceleration |
| **Framework** | LLaMA Stack | Standardizes core building blocks and simplifies AI application development |
| **UI Layer** | Streamlit | User-friendly chatbot interface for chat-based interaction |
| **LLM** | Llama-3.2-3B-Instruct | Generates contextual responses based on retrieved documents |
| **Safety** | Safety Guardrail | Blocks harmful requests and responses for secure AI interactions |
| **Integration** | MCP Servers | Model Context Protocol servers for enhanced functionality |
| **Embedding** | all-MiniLM-L6-v2 | Converts text to vector embeddings |
| **Vector DB** | PostgreSQL + PGVector | Stores embeddings and enables semantic search |
| **Retrieval** | Vector Search | Retrieves relevant documents based on query similarity |
| **Data Ingestion** | Kubeflow Pipelines | Multi-modal data ingestion with preprocessing pipelines for cleaning, chunking, and embedding generation |
| **Storage** | S3 Bucket | Document source for enterprise content |

## Deployment
The quickstart supports two modes of deployments. Follow the links below for setup instructions for your preferred deployment method.
- [Local](docs/local_setup_guide.md)
- [Openshift](docs/openshift_setup_guide.md)