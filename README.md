# BioLLM

**BioLLM** is a sophisticated project focused on the application of large language models to solve a range of complex biological tasks. This project is designed to help researchers, developers, and data scientists explore the potential of LLMs in the biological domain by predicting molecular structures, answering domain-specific questions, and visualizing biological entities.

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [APIs Overview](#apis-overview)
- [3D Visualization](#3d-visualization)
- [Demo](#Demo)

---

## About the Project

BioLLM integrates multiple models for tasks such as:

- **Protein 3D Structure Prediction**: Utilizing deep learning to predict the 3D structures of proteins based on sequence data.
- **DNA Sequence Structure Prediction**: Accurately predicting and visualizing DNA sequences.
- **Toxicity Level Prediction**: Assessing the toxicity levels of different molecules.
- **Retrieval-Augmented Question Answering**: Leveraging a RAG model to answer complex biological questions by integrating document retrieval.

The architecture is modular and includes an agent responsible for routing tasks to appropriate models based on the input, making it adaptable and scalable for various biological applications.

## Features

- **Multi-Model Architecture**: Different models for distinct biological tasks, all integrated into a cohesive system.
- **Automated Processing**: Automated data retrieval, document filtering, and response validation to ensure high-quality results.
- **3D Visualization**: Immersive 3D environments to visualize proteins and DNA sequences using Virtual Reality.
- **API-First Design**: APIs built using FastAPI for smooth integration and extensibility.
- **Real-Time Automation**: Selenium integration for web-based automation.
- **Robust Error Handling**: Mechanisms to detect and reduce hallucinations in generated responses.
- **Vector Store**: Leveraging Chroma and Nomic embeddings for document retrieval and storage.

## Project Structure
      
      BioLLM/
      │
      ├── 3d-dart/   # Prediction of the sequences                            
      │ 
      ├── rag/                 
      │   ├── rag.py         # RAG model
      │   ├── scrap_api.py     # Web Scraping logic
      │   └── vectorestore_add.py    # Adding the data scrapped to the database
      │
      ├── api_app.py/      # Contains all FastAPI endpoints     
      │   
      └── requirements.txt      # Python dependencies


## Technology Stack

- **Programming Languages**: Python
- **Framework**: FastAPI
- **Data Storage**: Vector databases with Chroma and Nomic
- **Visualization**: Virtual Reality integration using suitable VR frameworks
- **Web Automation**: Selenium
- **Containerization**: Docker
- **Source Control**: Git

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/medkarim19/BioLLM.git
   cd BioLLM

2. Set up a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install dependencies:
     ```bash
     pip install -r requirements.txt

4. CUDA Support: If you are using a GPU for accelerated deep learning tasks, ensure that the necessary CUDA dependencies are included in the requirements.txt. Here is an example of the relevant lines for PyTorch and CuPy with CUDA 11.8:
     ```bash
     torch==2.0.1+cu118
     torchvision==0.15.2+cu118
     torchaudio==2.0.2+cu118
     cupy-cuda118

5. Ollama Setup
     Ollama is used for LLM deployment and interaction. Follow the steps below to install and launch Ollama:
     
     Download Ollama from the official website.
     
     Install Ollama based on the instructions for your operating system.
     
     Verify the installation by running:
   
          
          ollama --version
   
     Launch Ollama by running:
   
          
          ollama start
   
     Ollama must be running in the background while using the BioLLM project to ensure that the LLM interactions are properly executed.


## Usage

To use the BioLLM project, follow these steps:

1. **Start the FastAPI Application**:
   Launch the FastAPI application by running the following command in the project directory:

   ```bash
   uvicorn api_app:app --reload

This will start the server at http://127.0.0.1:8000.

2. **Access the API Documentation**: Open your web browser and navigate to http://127.0.0.1:8000/docs to access the interactive API documentation provided by FastAPI. You can test the endpoints directly from this interface.

3. **Interacting with the Models**: Use the various endpoints to interact with the different models. Each API endpoint is designed to handle specific biological tasks. Refer to the API overview section below for details on available endpoints and their expected input/output formats.


## APIs Overview


1. **POST /ask**

   Description: Routes the question to the appropriate processing function based on the request.
   Request Body: JSON with a single key "question".
   Response: JSON containing the original question and the generated response.


2. **POST /query**

   Description: Queries the RAG model with the provided question.
   Request Body: String (the question to be queried).
   Response: JSON with the question and the generated response.


3. **POST /process_pdf**

   Description: Uploads and processes a PDF file to extract its text content.
   Request Body: Form data with the key pdf_file.
   Response: JSON indicating the success of the PDF processing.


4. **POST /process_urls**

   Description: Processes a list of URLs, loading their content and storing it in a vector database.
   Request Body: JSON array of URLs.
   Response: JSON confirming successful processing and storage.


5. **POST /process_dna**

   Description: Processes a DNA sequence and generates models in various formats (e.g., FBX).
   Request Body: JSON containing the DNA sequence.
   Response: JSON indicating the success of the FBX file encoding.


6. **POST /esm**

   Description: Processes a protein sequence using the ESM model to predict its structure.
   Request Body: JSON containing the protein sequence.
   Response: JSON indicating the success of the FBX file encoding.


## 3D Visualization
BioLLM leverages 3D visualization tools to represent biological structures. This enables immersive viewing experiences for proteins and DNA sequences, providing deeper insights and enhanced user interaction.

## Demo 
https://github.com/user-attachments/assets/12b514f2-6241-40f2-800e-6b4414bba198
