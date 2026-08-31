# S.A.V.I.O.R — Agent Instructions

## Project Overview

ParseSight is an Explainable Multimodal RAG application.

Users upload PDF documents and can:

1. View the original PDF.
2. Watch document extraction progress in real time.
3. Inspect elements extracted by Unstructured.
4. See element categories such as Title, NarrativeText, Table, and Image.
5. Click PDF elements and view their extracted metadata.
6. Process images using Gemini Vision.
7. Create embeddings for RAG retrieval.
8. Chat with the document.
9. Trace answers back to the original PDF elements.

The core differentiator is explainability and traceability.

---

# Architecture

The project is a monorepo.

```text
frontend/     React application
backend/      FastAPI application
.agents/      Agent context and project instructions
```

Frontend and backend must remain independently deployable.

Read the following files before making significant architectural changes:

* `.agents/context/project-overview.md`
* `.agents/context/architecture.md`
* `.agents/rules/general.md`

---

# Core Architecture Principle

Always preserve this relationship:

```text
PDF
 ↓
Document Elements
 ↓
RAG Chunks
 ↓
Embeddings
 ↓
Vector Store
```

Do not merge these layers.

## Elements

Elements represent the original document extraction.

They are used for:

* PDF highlighting
* element inspection
* extraction visualization
* source traceability

## Chunks

Chunks are derived from one or more elements.

They are used for:

* retrieval
* context generation
* embeddings

## Embeddings

Embeddings reference chunks.

Do not treat embeddings as the source of truth.

---

# Frontend

Location:

```text
frontend/
```

Technology:

* React
* TypeScript
* Vite
* React Router
* TanStack Query
* Zustand
* PDF.js or React-PDF
* Tailwind CSS

## Frontend Rules

Use feature-based organization.

Preferred structure:

```text
features/
  feature-name/
    components/
    hooks/
    api/
    types/
```

Do not place business logic directly inside large page components.

Keep:

* server state in TanStack Query
* UI state in Zustand
* reusable UI in shared components

---

# Backend

Location:

```text
backend/
```

Technology:

* Python
* FastAPI
* Unstructured
* PostgreSQL
* pgvector
* SQLAlchemy
* Pydantic

## Backend Rules

API routes must remain thin.

Preferred flow:

```text
API Route
 ↓
Service / Use Case
 ↓
Repository / Infrastructure
```

Do not put:

* Unstructured processing
* embedding logic
* Gemini API calls
* database business logic

directly inside API route files.

---

# Document Processing

The document processing pipeline is:

```text
Upload PDF
 ↓
Store Original Document
 ↓
Create Document Record
 ↓
Start Background Processing
 ↓
Unstructured Extraction
 ↓
Store Raw Elements
 ↓
Process Elements by Type
 ↓
Create RAG Chunks
 ↓
Generate Embeddings
 ↓
Store Vectors
 ↓
Mark Document Ready
```

---

# Multimodal Processing

## Text

```text
Text Element
 ↓
Context-aware Chunking
 ↓
Embedding
```

## Table

```text
Table Element
 ↓
Structured Representation
 ↓
Chunking
 ↓
Embedding
```

## Image

```text
Image Element
 ↓
Gemini Vision
 ↓
Structured Image Description
 ↓
Embedding
```

Never embed an image description without maintaining a reference to the original image element.

---

# PDF Element Mapping

Every extracted element should preserve, when available:

```text
element_id
document_id
page_number
category
text
coordinates
metadata
```

Coordinates are critical for frontend visualization.

The frontend must be able to map:

```text
PDF Location
 ↔
Element
 ↔
Chunk
 ↔
Retrieved Source
```

Do not break this relationship.

---

# Real-Time Processing

Document processing progress is streamed to the frontend.

Important events include:

```text
document_uploaded
processing_started
page_processing
element_extracted
image_processing
embedding_created
document_completed
processing_failed
```

Events must have consistent schemas.

Do not introduce new event names without updating the event contract.

---

# Error Handling

Always:

* use structured errors
* log failures with context
* avoid swallowing exceptions
* return meaningful API errors
* preserve document processing status

For background jobs:

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

---

# Database

Use PostgreSQL as the source of truth.

Recommended conceptual entities:

```text
Document
Element
Chunk
Embedding
Conversation
Message
```

Relationships must preserve traceability.

```text
Document
  └── Elements
        └── Chunks
              └── Embeddings
```

---

# Before Making Changes

Before implementing a feature:

1. Inspect the relevant existing code.
2. Read the relevant `.agents/rules/` file.
3. Check architectural decisions in `.agents/decisions/`.
4. Prefer extending existing patterns.
5. Do not introduce a new dependency without justification.
6. Keep changes focused.

---

# Code Quality

Prefer:

* small functions
* explicit types
* clear naming
* dependency injection where appropriate
* testable services

Avoid:

* unnecessary abstractions
* large god classes
* duplicated business logic
* hidden global state
* premature microservices

---

# Testing

For every significant feature:

* add unit tests for business logic
* add integration tests for API/database behavior when appropriate

Critical functionality must be tested:

* PDF upload
* document processing
* element persistence
* chunk creation
* retrieval
* source traceability

---

# Definition of Done

A feature is complete when:

1. The implementation follows the existing architecture.
2. Types and validation are updated.
3. Error handling is included.
4. Relevant tests pass.
5. No existing functionality is broken.
6. Documentation is updated when architecture or contracts change.
