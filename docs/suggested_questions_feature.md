# Suggested Questions Feature

## Overview

The RAG chat UI now includes a **Suggested Questions** feature that displays relevant questions based on the selected vector databases. This helps users quickly explore the capabilities of each database with pre-defined, contextually relevant questions.

## Features

1. **Database-Specific Questions**: Each vector database has its own set of suggested questions tailored to its content
2. **Smart Display**: Shows 4 questions initially with a "Show More" button to reveal additional questions
3. **Multi-Database Support**: When multiple databases are selected, questions from all selected databases are combined and displayed
4. **One-Click Query**: Users can click any suggested question to automatically send it to the chat and receive a response
5. **Visual Feedback**: Each question button shows which database it's associated with via a tooltip

## Configuration

### Helm Deployment (OpenShift/Kubernetes)

Questions are configured at the root level in the `rag-values.yaml` file in a dedicated `suggestedQuestions` section:

```yaml
# Suggested Questions Configuration
# These questions appear in the chat UI when users select a database
# The key should match the vector_store_name (identifier) of the database
suggestedQuestions:
  hr-vector-db-v1-0:
    - "What are the health insurance benefits offered?"
    - "How many vacation days do employees get?"
    - "What is the parental leave policy?"
    - "What are the retirement benefits?"
    - "How do I enroll in benefits?"
    - "What is the employee assistance program?"
  
  legal-vector-db-v1-0:
    - "What are the key contract terms?"
    - "What is the liability clause?"
    # ... more questions
```

This root-level configuration keeps the questions separate from the ingestion pipeline configuration, making it easier to manage and modify.

The questions are passed to the UI via environment variables:

```yaml
env:
  - name: "RAG_QUESTION_SUGGESTIONS"
    value: |
      {
        "hr-vector-db-v1-0": [
          "What are the health insurance benefits offered?",
          "How many vacation days do employees get?",
          ...
        ],
        "legal-vector-db-v1-0": [
          "What are the key contract terms?",
          ...
        ]
      }
```

### Local Deployment (Podman/Docker)

Questions are configured in the `podman-compose.yml` file under the `rag-ui` service:

```yaml
services:
  rag-ui:
    environment:
      RAG_QUESTION_SUGGESTIONS: |
        {
          "hr-vector-db-v1-0": [
            "What are the health insurance benefits offered?",
            ...
          ]
        }
```

## Default Question Sets

The following databases come with pre-configured questions:

### HR Database (`hr-vector-db-v1-0`)
- What are the health insurance benefits offered?
- How many vacation days do employees get?
- What is the parental leave policy?
- What are the retirement benefits?
- How do I enroll in benefits?
- What is the employee assistance program?

### Legal Database (`legal-vector-db-v1-0`)
- What are the key contract terms?
- What is the liability clause?
- What are the termination conditions?
- What are the intellectual property rights?
- What is the dispute resolution process?
- What are the compliance requirements?

### Sales Database (`sales-vector-db-v1-0`)
- What is the sales process?
- How do I qualify leads?
- What are the pricing strategies?
- What is the commission structure?
- How do I handle customer objections?
- What are the territory assignments?

### Procurement Database (`procurement-vector-db-v1-0`)
- What is the procurement process?
- How do I submit a purchase request?
- What are the approval requirements?
- Who are the approved vendors?
- What is the purchasing policy?
- How do I track my order?

### Tech Support Database (`techsupport-vector-db-v1-0`)
- How do I install CloudSync on Mac?
- How do I install CloudSync on Windows?
- How do I sync files between devices?
- How do I troubleshoot CloudSync sync issues?
- How do I install Linux on TechGear Pro Laptop?
- Where can I find video drivers for TechGear Pro?

## User Experience

1. **Select Database(s)**: In the sidebar, select one or more document collections
2. **View Suggestions**: The main chat area displays a "💡 Suggested Questions" section with relevant questions
3. **Click to Query**: Click any question button to automatically send it to the chat
4. **Show More/Less**: If there are more than 4 questions, use the "Show More" button to expand, or "Show Less" to collapse

## Customization

To add or modify questions for a database:

1. **For Helm deployments**: 
   - Edit the root-level `suggestedQuestions` section in `rag-values.yaml`
   - Also update the `RAG_QUESTION_SUGGESTIONS` environment variable in the UI `env` section to match
2. **For local deployments**: 
   - Update the `RAG_QUESTION_SUGGESTIONS` JSON in `podman-compose.yml`

### JSON Format

The question suggestions use this structure:

```json
{
  "vector-db-identifier": [
    "Question 1?",
    "Question 2?",
    "Question 3?"
  ]
}
```

**Important**: The key must match the `identifier` of the vector database (typically `{name}-v{version}`), not just the `vector_db_name`.

## Technical Implementation

### Files Modified

1. **`deploy/helm/rag-values.yaml`**: Added question mappings to pipeline configs and environment variables
2. **`deploy/local/podman-compose.yml`**: Added question mappings to UI service
3. **`frontend/llama_stack_ui/distribution/ui/modules/utils.py`**: Added helper functions to load and filter questions
4. **`frontend/llama_stack_ui/distribution/ui/page/playground/chat.py`**: Added UI components and click handlers

### Key Functions

- `get_question_suggestions()`: Loads questions from environment variable
- `get_suggestions_for_databases()`: Filters questions based on selected databases
- `display_suggested_questions()`: Renders the UI with buttons and expand/collapse functionality
- Question click handler: Automatically sends selected question to chat

## Benefits

1. **Improved Discoverability**: Users can quickly understand what each database contains
2. **Faster Onboarding**: New users can start exploring immediately with relevant examples
3. **Better UX**: Reduces the cognitive load of formulating questions
4. **Contextual Help**: Questions are tailored to each specific database's content
5. **Clean Configuration**: Root-level `suggestedQuestions` section separates UI concerns from pipeline configuration
