import os
import re
from langchain_nomic.embeddings import NomicEmbeddings


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"

### LLM

local_llm = "llama3"


### Index

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings, HuggingFaceBgeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

urls = ["https://phys.org/news/2024-07-scientists-figure-birds-tropics.html"
    
]

# Load documents
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Function to preprocess content
def preprocess_content(text):
    # Remove ads, email forms, and other unrelated content
    text = re.sub(r"[\n\s]+", " ", text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r"(?i)(Email|Subscribe|Privacy|Donate|Feedback).*?[\n]", "", text)  # Remove common sections
    text = re.sub(r"(?i)more information.*", "", text)
    return text

# Preprocess documents
for doc in docs_list:
    doc.page_content = preprocess_content(doc.page_content)
    

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500, chunk_overlap=50
)

# Split documents into chunks
doc_splits = text_splitter.split_documents(docs_list)
local_directory = r"C:\Users\omara\Desktop\Talan\chromaDb"
# Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="rag-chroma",
    embedding=NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local"),
    persist_directory=local_directory
)