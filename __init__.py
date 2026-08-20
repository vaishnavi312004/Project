import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings

load_dotenv()


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        temperature=0
    )


def get_embeddings():
    return MistralAIEmbeddings(
        model="mistral-embed"
    )