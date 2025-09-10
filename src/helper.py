from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


def load_data(URLS):
    loader = UnstructuredURLLoader(URLS)
    data = loader.load()
    return data

def  slip_documents(data):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
    text_chunks = text_splitter.split_documents(data)
    return text_chunks

def load_embeddings():
    embeddings = OpenAIEmbeddings()
    return embeddings