from src.helper import load_data, slip_documents, load_embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

URLS = [
    "https://www.ycombinator.com/",
    "https://www.ycombinator.com/companies",
    "https://www.ycombinator.com/jobs",
    "https://www.ycombinator.com/cofounder-matching",
    "https://www.ycombinator.com/library",
    "https://www.ycombinator.com/about",
    "https://www.ycombinator.com/internships",
    "https://www.ycombinator.com/contact",
    "https://www.ycombinator.com/demoday",
    "https://www.ycombinator.com/blog/startup-school",
    "https://www.ycombinator.com/companies/founders",
    "https://www.ycombinator.com/documents"
]

loaded_data = load_data(URLS)
text_chunks = slip_documents(loaded_data)
embeddings = load_embeddings()
index_name = "yc-bot-db"

pc = Pinecone(api_key=PINECONE_API_KEY)

pc.create_index(
    name=index_name,
    dimension=1536, 
    metric="cosine", 
    spec=ServerlessSpec(
        cloud="aws", 
        region="us-east-1"
    ) 
) 

# Embed each chunk and upsert the embeddings into your Pinecone index.
vector_store = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings, 
)