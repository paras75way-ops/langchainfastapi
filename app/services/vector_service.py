import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
 
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

VECTORSTORE_DIR = "vectorstore"


embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  
)

def get_vectorstore() -> Chroma:
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )


def add_to_vectorstore(pdf_id: str, file_path: str, filename: str):
    
    loader = PyPDFLoader(file_path)
    pages = loader.load()
 
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(pages)

     
    for chunk in chunks:
        chunk.metadata["pdf_id"] = pdf_id
        chunk.metadata["filename"] = filename

    print(f"Total chunks: {len(chunks)}")

    
    db = get_vectorstore()
    for i, chunk in enumerate(chunks):
        db.add_documents([chunk])
        print(f"Embedded chunk {i+1}/{len(chunks)}")
        time.sleep(0.5)    

    print(f"✅ Done embedding PDF: {filename}")


def delete_from_vectorstore(pdf_id: str):
    db = get_vectorstore()
    results = db.get(where={"pdf_id": pdf_id})
    ids_to_delete = results["ids"]

    if ids_to_delete:
        db.delete(ids=ids_to_delete)
        print(f"🗑️ Deleted {len(ids_to_delete)} chunks for pdf_id: {pdf_id}")
    else:
        print(f"⚠️ No chunks found for pdf_id: {pdf_id}")


def query_vectorstore(question: str, k: int = 4) -> list:
    db = get_vectorstore()
    return db.similarity_search(question, k=k)