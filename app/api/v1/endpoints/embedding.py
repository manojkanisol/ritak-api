from fastapi import APIRouter, HTTPException,Depends,Request,Header
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from pymongo import MongoClient
from ....config import settings
from ....schemas.embedding import KnowledgeBaseText
from ....core.security import get_token_from_header
from typing import Optional

#Embedding Model
embedding_model = OllamaEmbeddings(model="llama3.1:latest")

router = APIRouter()

#Set MongoDB Connection
client = MongoClient(settings.mongodb_url)

#MongoDB Database Collection
DB_NAME = "vector"
COLLECTION_NAME = "vector_collection"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "rag-index-vectors"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

mongodb_vector_search = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embedding_model,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine"
)

@router.post("/generate_embeddings")
async def generate_embeddings(embedding: KnowledgeBaseText,userId:str = Depends(get_token_from_header),Authorization:Optional[str] = Header(None)):
   document = Document(
       page_content=embedding.text,
       metadata={"userId":userId}
   )
   mongodb_vector_search.add_documents(documents = [document])
   return {
        "response" : "Saved in database"
    }
