import os

import openai

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import requests
from googlesearch import search
from os import remove

import spacy

import fitz
import re











### FUNCIONES
def clean_up_text(content: str) -> str:
    """
    Remove unwanted characters and patterns in text input.
    :param content: Text input.
    :return: Cleaned version of original text input.
    """

    # Convertir a minúsculas
    content = content.lower()

    # Eliminar caracteres especiales
    content = re.sub(r'[^\w\s\d]', '', content)

    # Remove specific unwanted patterns and characters
    unwanted_patterns = [
        "\\n", "  —", "——————————", "—————————", "—————",
        r'\\u[\dA-Fa-f]{4}', r'\uf075', r'\uf0b7'
    ]
    for pattern in unwanted_patterns:
        content = re.sub(pattern, "", content)

    # Fix improperly spaced hyphenated words and normalize whitespace
    content = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', content)
    
    # Eliminar espacios en blanco adicionales
    content = re.sub(r"\s+", " ", content)

    return content

def find_context(pregunta):
    nlp = spacy.load("es_dep_news_trf") # Carga el modelo de lenguaje en español
    doc = nlp(pregunta) # Procesa el texto de la pregunta
    keywords = [token.text for token in doc if not token.is_stop and not token.is_punct] # Obtiene las palabras clave
    contexto = " ".join([k for k in keywords]) # Convierte las palabras clave en una cadena separada por espacios
    return contexto

def read_pdf_from_url(url):
    response = requests.get(url)
    response.raise_for_status() # Si hay un error, lanza una excepción
    
    with open("temp_pdf.pdf", "wb") as f:
        f.write(response.content) 
    
    doc = fitz.open("temp_pdf.pdf")  # Abre el documento PDF
    documents = []  # Lista para almacenar los documentos
    for page in doc:
        text = page.get_text()  # Obtiene el texto de la página
        # Crea un objeto de documento con la propiedad 'page_content' y añádelo a la lista
        documents.append({"page_content": text})
    
    doc.close()  # Cierra el documento

    remove("temp_pdf.pdf")  # Elimina el archivo temporal
    
    return documents

def find_pdf_url(query):
    for url in search(query, tld="es", num=5, stop=5, lang="es", pause=2):
        if url.endswith('.pdf'):
            return url
        else:
            print("f")
    raise ValueError("No PDF found in search results")










### pinecone
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
my_index = os.getenv("PINECONE_INDEX_EMPRESA")

# if index is not found
if my_index not in pc.list_indexes().names():        
    pc.create_index(
        name='prueba',
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
    my_index = 'prueba'

index =pc.Index(my_index)


###Llamaindex
from pathlib import Path
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.pinecone import PineconeVectorStore

save = False
if save:
    # Load pdf
    pdf_path = Path('./docs/Iberia.pdf')
    docs0 = PyMuPDFReader().load_data(file_path=pdf_path)

    doc_text = "\n\n".join([d.get_content() for d in docs0])

    # Clean pdf
    cleaned_text = clean_up_text(doc_text)

    documents = [Document(text=cleaned_text)]

    # Embedding model
    embed_model = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY") )

    # Pinecone vector store
    vector_store = PineconeVectorStore(pinecone_index=index)

    # Ingestion pipeline
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(
                chunk_size=1024,
                chunk_overlap=0
                ),
            embed_model,
            ],
            vector_store=vector_store 
        )

    # Now we run our pipeline!
    pipeline.run(documents=documents)

def download_pdf(url, output_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"PDF descargado correctamente y guardado en {output_path}")
    else:
        print(f"Error al descargar el PDF. Código de estado: {response.status_code}")

def upload_pdf(pdf_path, titulo):

    download_pdf(pdf_path, f"./docs/{titulo}.pdf")

    pdf_path = Path(f"./docs/{titulo}.pdf")

    docs0 = PyMuPDFReader().load_data(file_path=pdf_path)

    doc_text = "\n\n".join([d.get_content() for d in docs0])

    # Clean pdf
    cleaned_text = clean_up_text(doc_text)

    documents = [Document(text=cleaned_text, metadata={"file_name": titulo})]
    # documents = [Document(text=cleaned_text)]

    # Embedding model
    embed_model = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY") )

    # Pinecone vector store
    vector_store = PineconeVectorStore(pinecone_index=index)

    # Ingestion pipeline
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(
                chunk_size=1024,
                chunk_overlap=0
                ),
            embed_model,
            ],
            vector_store=vector_store 
        )

    # Now we run our pipeline!
    pipeline.run(documents=documents)















### OpenAI
app = FastAPI()

# Set up CORS middleware for the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retrieve the OpenAI API key from environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORGANIZATION")

print(openai.api_key)
print(openai.organization)

if openai.api_key is None:
    raise ValueError("OpenAI API key not found. Make sure it's set in your environment variables.")

template = """La siguiente es una pregunta hecha por un usuario: {question} 
    Por favor, identifica y devuelve el nombre de la empresa del usuario mencionada en la pregunta,
    si no hay un nombre de empresa explícito, devuelve NO"""

prompt = PromptTemplate(template=template, input_variables=["question"])

# Initialize the language model with specific settings
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7, max_tokens=10)
llm_chain = LLMChain(prompt=prompt, llm=llm)  # Create a chain for processing with the language model



template2 = """Responde solamente 'NO' si la respuesta proporcionada indica que no se encontraron documentos relevantes.
    De lo contrario, responde solamente 'SI'
    Respuesta: {response}"""

prompt2 = PromptTemplate(template=template2, input_variables=["question"])

# Initialize the language model with specific settings
llm2 = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7, max_tokens=10)
llm_chain2 = LLMChain(prompt=prompt2, llm=llm2)  # Create a chain for processing with the language model




















from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
import datetime
from llama_index.core import PromptTemplate

from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)

# Define a model for input validation using Pydantic
class InputModel(BaseModel):
    pregunta: str


def responde(pregunta):
            # Configuración de Pinecone y Vector Store
        vector_store = PineconeVectorStore(pinecone_index=index)
        vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        # Creación del motor de consulta
        # query_engine = vector_index.as_query_engine(response_mode="tree_summarize", similarity_top_k=1, similarity_cutoff=0.7, llm=OpenAI(model="gpt-4o", temperature = 0.7))
        query_engine = vector_index.as_query_engine(response_mode="tree_summarize", similarity_top_k=2, similarity_cutoff=0.8)

        prompt_str = (
            """
            Te llamas AsesorBot, y eres un agente virtual con IA que proporciona información y asesoramiento sobre temas legales y fiscales.
            Responde a la pregunta con la información del documento, hazlo como respondería una gestoría profesional a su cliente,
            eres un experto en el tema y estás respondiendo a un cliente que necesita información precisa y detallada.

            Cuando la respuesta no se encuentra en ninguno de los documentos proporcionados, pide disculpas y recomienda información para saberlo,
            sin mencionar detalles escificos de los documentos ni que la información proporcionada en los documentos no incluye la respuesta.

            Documento: {context_str}
            Pregunta: {query_str}
            Respuesta: 
            """
        )

        # fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")
        # prompt_str = prompt_str.format(
        #     fecha_actual = fecha_actual,
        # )

        prompt = PromptTemplate(
            prompt_str
        )

        # Actualización de los prompts en el motor de consulta
        query_engine.update_prompts(
            {"response_synthesizer:summary_template": prompt}
        )

        # Realización de la consulta
        llm_query = query_engine.query(pregunta)
        response = llm_query.response
        
        return response


# Define an endpoint in the FastAPI app
@app.post("/get_response")
def process_string(input_data: InputModel):
    pregunta = input_data.pregunta

    try:
        nombre_empresa = llm_chain.run(question=pregunta)
        a = 0
        if nombre_empresa != "NO":
            a = 1

            print("Nombre de la empresa: " + nombre_empresa)
            my_index = os.getenv("PINECONE_INDEX_EMPRESA")
            index =pc.Index(my_index)

            vector_store = PineconeVectorStore(pinecone_index=index)
            vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
            query_engine = vector_index.as_query_engine(response_mode="tree_summarize", similarity_top_k=2, similarity_cutoff=0.8)
            prompt_str = (
                "Contesta 'SI', si hay un documento que contiene en el campo 'file_name' del metadata el nombre:"
                f" 'Convenio_colectivo_{nombre_empresa}', y 'Empty Response' si no lo hay."
            )
            prompt = PromptTemplate(prompt_str)

            query_engine.update_prompts({"response_synthesizer:summary_template": prompt})
            llm_query = query_engine.query(nombre_empresa)
            response = llm_query.response

            # filters = MetadataFilters(
            #     filters=[
            #         MetadataFilter(
            #             key="file_name",
            #             operator=FilterOperator.EQ,
            #             value="Naturgy"
            #         )
            #     ]
            # )
            
            # retriever = vector_index.as_retriever(filters=filters)
            # response = retriever.retrieve("Contesta 'SI', si hay un documento que contiene en el campo 'file_name' del metadata el nombre de la empresa ('Convenio_colectivo_' + nombre empresa), y 'Empty Response' si no lo hay.")
            
            print("Respuesta: " + response)
            
            if response == "Empty Response":
                convenio = nombre_empresa + " convenio colectivo pdf"
                pdf_url = find_pdf_url(convenio)
                print("PDF URL: " + pdf_url)
                titulo = "Convenio_colectivo_" + nombre_empresa
                # upload_pdf(pdf_url, titulo)
        else:
            my_index = os.getenv("PINECONE_INDEX_NAME")
            index =pc.Index(my_index)

        
        response = responde(pregunta)

        if a == 0:
            if response != "Empty Response": # If there are results from Pinecone
                return {"response": response}
            else:
                response = "No se encontró información relevante en los documentos proporcionados."
        
        else:
            response2 = llm_chain2.run(response=response)
            if response2 == "NO":
                print("Buscando en Estatuto de los Trabajadores")
                my_index = os.getenv("PINECONE_INDEX_NAME")
                index =pc.Index(my_index)
                response = responde(pregunta)

        return {"response": response}

        
    except Exception as e:
        return {"error": str(e)}
    

