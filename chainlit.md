# Ronald AI: A Personal RAG Chatbot 

[![Chainlit](https://img.shields.io/badge/Made%20with-Chainlit-blue.svg)](https://chainlit.io)
[![LlamaIndex](https://img.shields.io/badge/Powered%20by-LlamaIndex-green.svg)](https://www.llamaindex.ai/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow.svg)](https://huggingface.co/)
[![OpenGVLab InternVL3](https://img.shields.io/badge/LLM%20via-OpenRouter-purple.svg)](https://openrouter.ai/opengvlab/internvl3-14b:free)

---

## Overview

**Ronald AI** is my intelligent and friendly personal assistant, designed to answer my questions based on a specific set of documents. Built with Python using the powerful `Chainlit` framework for the user interface and `LlamaIndex` for efficient data indexing and retrieval, this application provides me with a seamless conversational experience.

The core of Ronald AI is its ability to understand and respond to queries strictly within the context of the documents I provide, ensuring accurate and relevant answers. It leverages a state-of-the-art language model from `OpenRouter` and a high-quality embedding model from `Hugging Face` to comprehend and process my questions effectively.

## Features

-  **RAG pipeline**: Retrieves and grounds answers on local documents.
-  **LLM Integration**: Uses OpenRouter's OpenAI: GPT-OSS 20B Chat model for generation.
-  **Document Indexing**: Auto-loads or rebuilds index from `data/`.
-  **Real-time Chat UI**: Powered by Chainlit with streaming responses.
-  **HuggingFace Embeddings**: Uses `BAAI/bge-small-en-v1.5` for vector search.
- **Simple storage**: Uses LlamaIndex's persistent `StorageContext`.

