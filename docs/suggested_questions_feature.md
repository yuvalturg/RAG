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

Questions are configured at the root level in the `rag-values.yaml` file in a dedicated `suggestedQuestions` section. The Helm chart automatically creates a ConfigMap from this configuration and injects it into the UI pod as an environment variable:

```yaml
# Suggested Questions Configuration
# These questions appear in the chat UI when users select a database
# The key should match the vector_store_name (identifier) of the database
# This configuration will be stored in a ConfigMap and injected as an environment variable
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

The Helm chart creates a ConfigMap named `<release-name>-rag-suggested-questions` that contains the JSON-formatted questions, which is then mounted as the `RAG_QUESTION_SUGGESTIONS` environment variable in the deployment.

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
   - Run `helm upgrade` to update the ConfigMap
   - The changes will be automatically applied to the UI pods
   
2. **For local deployments**: 
   - Update the `RAG_QUESTION_SUGGESTIONS` JSON in `podman-compose.yml`
   - Restart the `rag-ui` container

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
