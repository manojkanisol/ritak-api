import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

app = FastAPI()

class Item(BaseModel):
    dataSource:str

class UserPrompt(BaseModel):
    prompt:str

#Embedding Model
embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")

#Chat Model
chat_model = ChatOllama(
    model="llama3.1:latest",
    temperature= 0.5,
    num_predict= 1000
)

#Set MongoDB Connection
client = MongoClient("mongodb://43.225.26.120:27017/?directConnection=true")

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
@app.get("/")
async def app_status():
    return "app is running"

# Convert Data into Embeddings
@app.post("/generate_embeddings")
async def generate_embeddings(item:Item):
   document = Document(
       page_content=item.dataSource,
       metadata={"source":"riak-ui"}
   )
   mongodb_vector_search.add_documents(documents = [document])
   return {
        "response" : "Saved in database"
    }

# Chat Streaming
@app.post("/chat_streaming")
async def chat_streaming(data:UserPrompt):
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