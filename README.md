# AI-CHAT

Simple AI framework to interact with Ollama in a local Web Interface - Minimal Requirements

Project Description: Lightweight Web UI Integration for Ollama This project provides a streamlined method to interact with Ollama via a lightweight Web UI, ideal for developers who want fast, local, and customizable access to large language models without the complexity of a full-stack deployment.

Benefits and Advantages Lightweight and Fast: Minimal setup overhead compared to larger solutions like Open WebUI or full chat platforms. Local and Private: Runs entirely on your machine with no external data sharing, ensuring privacy and control. Customizable: Easily modified to suit specific workflows, including prompt templates, model switching, and API hooks. Low Resource Usage: Designed for systems with modest resources—no heavy frontend frameworks or bloated dependencies. Seamless Integration: Directly interfaces with Ollama's local API, eliminating the need for cloud-based access or additional layers.

Key Features Direct Communication with Ollama: Uses HTTP requests to send prompts and receive streamed or full responses from running Ollama models. Simple UI: Clean interface with a prompt input, conversation history, and real-time response display. Model Switching: Supports toggling between installed models like llama2, mistral, codellama, etc. Local API Configuration: Allows setting Ollama's base URL and custom headers if needed. Session Persistence (optional): Can save prompt/response history to local storage or file for continuity between sessions. Markdown Rendering: Supports markdown-style formatting of responses for enhanced readability. 

Database requirements are handeled from within python with SQLite. Future versions will support SQLcipher to encrypt the chat database. 
