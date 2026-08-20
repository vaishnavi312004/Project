import os

from tavily import TavilyClient

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import get_llm, get_embeddings


class CorrectiveRAG:

    def __init__(self):

        # LLM

        self.llm = get_llm()

        # Embeddings

        self.embeddings = get_embeddings()

        # Corrective RAG PDF directory

        self.pdf_directory = "data/corrective"

        # Chroma database

        self.persist_directory = "data/chroma_hr"

        self.collection_name = "hr_documents"

        # Tavily

        self.tavily = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

        # Load / create vector store

        self.vector_store = self.load_documents()

    # LOAD PDFs DYNAMICALLY

    def load_documents(self):

        documents = []

        # Check directory

        if not os.path.exists(self.pdf_directory):

            raise FileNotFoundError(
                f"Directory not found: {self.pdf_directory}"
            )

        # Automatically find all PDFs

        pdf_files = [
            file
            for file in os.listdir(self.pdf_directory)
            if file.lower().endswith(".pdf")
        ]

        if not pdf_files:

            raise ValueError(
                "No PDF files found in data/corrective"
            )

        # Load every PDF

        for filename in pdf_files:

            pdf_path = os.path.join(
                self.pdf_directory,
                filename
            )

            print(f"Loading PDF: {filename}")

            loader = PyPDFLoader(pdf_path)

            documents.extend(
                loader.load()
            )

        # Split documents

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )

        chunks = splitter.split_documents(
            documents
        )

        print(
            f"Loaded {len(documents)} pages "
            f"and created {len(chunks)} chunks."
        )

        # Create Chroma vector store

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )

        return vector_store

    # RETRIEVE

    def retrieve(self, question):

        return self.vector_store.similarity_search(
            question,
            k=3
        )

    # RELEVANCE EVALUATION

    def evaluate_relevance(
        self,
        question,
        documents
    ):

        if not documents:

            return "IRRELEVANT"

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        prompt = f"""
You are evaluating retrieved documents.

Question:
{question}

Retrieved documents:
{context}

Determine whether the retrieved documents
contain enough information to answer the question.

Return exactly one word:

RELEVANT

or

IRRELEVANT
"""

        response = self.llm.invoke(prompt)

        result = response.content.strip().upper()

        if result == "RELEVANT":

            return "RELEVANT"

        return "IRRELEVANT"

    # WEB SEARCH

    def web_search(self, question):

        response = self.tavily.search(
            query=question,
            max_results=3
        )

        return [
            result["content"]
            for result in response.get("results", [])
            if result.get("content")
        ]

    # GENERATE ANSWER

    def generate_answer(
        self,
        question,
        context
    ):

        if not context:

            return (
                "I could not find enough information "
                "to answer the question."
            )

        context_text = "\n\n".join(context)

        prompt = f"""
You are an enterprise HR assistant.

Question:
{question}

Context:
{context_text}

Answer the question using only the
provided context.

Rules:
- Do not invent information.
- Do not make unsupported assumptions.
- If the context is insufficient, say so.
- Keep the answer concise and clear.
"""

        response = self.llm.invoke(prompt)

        return response.content.strip()

    # COMPLETE CORRECTIVE RAG

    def run(self, question):

        # 1. Retrieve from internal PDFs

        documents = self.retrieve(
            question
        )

        # 2. Evaluate relevance
        evaluation = self.evaluate_relevance(
            question,
            documents
        )

        # 3. Correct retrieval if necessary

        if evaluation == "RELEVANT":

            context = [
                document.page_content
                for document in documents
            ]

            source = "Internal HR Documents"

        else:

            context = self.web_search(
                question
            )

            source = "Tavily Web Search"

        # 4. Generate answer

        answer = self.generate_answer(
            question,
            context
        )

        # 5. Return result         

        return {
            "answer": answer,
            "evaluation": evaluation,
            "source": source,
            "context": context
        }