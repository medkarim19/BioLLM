from flask import Flask, request, jsonify
import os
import re
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = Flask(__name__)

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"

local_directory = r"C:\Users\omara\Desktop\Talan\chromaDb"

# Function to preprocess content
def preprocess_content(text):
    text = re.sub(r"[\n\s]+", " ", text)
    text = re.sub(r"(?i)(Email|Subscribe|Privacy|Donate|Feedback).*?[\n]", "", text)
    text = re.sub(r"(?i)more information.*", "", text)
    return text

@app.route('/process', methods=['POST'])
def process_documents():
    data = request.get_json()
    urls = data.get('urls', [])
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    
    try:
        # Load and preprocess documents
        docs = [WebBaseLoader(url).load() for url in urls]
        docs_list = [item for sublist in docs for item in sublist]
        for doc in docs_list:
            doc.page_content = preprocess_content(doc.page_content)

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500, chunk_overlap=50
        )
        doc_splits = text_splitter.split_documents(docs_list)

        # Add to vectorDB
        vectorstore = Chroma.from_documents(
            documents=doc_splits,
            collection_name="rag-chroma",
            embedding=NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local"),
            persist_directory=local_directory
        )
        return jsonify({'message': 'Documents processed and stored successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


#Invoke-WebRequest -Uri "http://127.0.0.1:5000/process" -Method Post -ContentType "application/json" -Body '{"urls": ["https://phys.org/news/2024-07-qa-machine-propelling-biology.html"]}'