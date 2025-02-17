from fastapi import APIRouter, HTTPException,Depends,Request,Header
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from ....config import settings
from ....schemas.chat import UserPrompt
from ....core.security import get_token_from_header
from typing import Optional
from langchain_aws import BedrockEmbeddings
from langchain_aws.chat_models.bedrock import ChatBedrock

router = APIRouter()

#Chat Model
chat_model = ChatOllama(
    model="llama3.1:latest",
    temperature= 0.5,
    num_predict= 1000
)

chat_model_aws = ChatBedrock(
    credentials_profile_name="default",
    region="us-east-1",
    model="us.meta.llama3-1-8b-instruct-v1:0"
)

embedding_model = OllamaEmbeddings(model="llama3.1:latest")
embedding_model_aws = BedrockEmbeddings(credentials_profile_name="default",region_name="us-east-1")

#Set MongoDB Connection
client = MongoClient(settings.mongodb_url)

#MongoDB Database Collection
DB_NAME = "vector"
CHAT_DB_NAME = "chat"
CHAT_COLLECTION_NAME = "chat_histories"
COLLECTION_NAME = "vector_collection"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "rag-index-vectors"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
MONGODB_COLLECTION_HISTORY = client

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
    chat_message_history = MongoDBChatMessageHistory(
        session_id= userId,
        connection_string=settings.mongodb_url,
        database_name=CHAT_DB_NAME,
        collection_name=CHAT_COLLECTION_NAME
    )
    if result:
        chat_message_history.add_user_message(data.prompt)
        chat_message_history.add_ai_message(result)

    return {
        "generated_content": result
    }

@router.post("/chat_history")
async def chat_history(userId:str = Depends(get_token_from_header),Authorization:Optional[str] = Header(None)):
     chat_message_history = MongoDBChatMessageHistory(
        session_id= userId,
        connection_string=settings.mongodb_url,
        database_name=CHAT_DB_NAME,
        collection_name=CHAT_COLLECTION_NAME
    )
     return{
         "chat_history":chat_message_history.messages
     }


# uvicorn.run(app)