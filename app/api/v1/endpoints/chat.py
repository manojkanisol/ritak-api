from fastapi import APIRouter, HTTPException,Depends,Request,Header
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from ....config import settings
from ....schemas.chat import UserPrompt
from ....core.security import get_token_from_header
from typing import Optional


router = APIRouter()

#Chat Model
chat_model = ChatOllama(
    model="llama3.1:latest",
    temperature= 0.5,
    num_predict= 1000
)

embedding_model = OllamaEmbeddings(model="llama3.1:latest")

#Set MongoDB Connection
client = MongoClient(settings.mongodb_url)

#MongoDB Database Collection
DB_NAME = "vector"
COLLECTION_NAME = "vector_collection"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "rag-index-vectors"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

#VectorMongdbSearch
mongodb_vector_search = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embedding_model,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine"
)

#RAG_TEMPLATE
RAG_TEMPLATE = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.
If you don't know to answer,just say that you don't know.Use three sentences maximum and keep the answer concise.

<context>
{context}
</context>

Answer the following question:

{question}"""

# ROOT Navigation


# Chat Streaming
@router.post("/chat_streaming")
async def chat_streaming(data:UserPrompt,userId:str = Depends(get_token_from_header),Authorization:Optional[str] = Header(None)):
    print(data.prompt)
    docs = mongodb_vector_search.similarity_search(query=data.prompt,k=2)
    print(docs)
    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        RunnablePassthrough.assign(context=lambda input:format_docs(input["context"]))
        | rag_prompt
        | chat_model
        | StrOutputParser()
    )

    result = chain.invoke({"context":docs,"question":data.prompt})

    return {
        "generated_content": result
    }

# uvicorn.run(app)