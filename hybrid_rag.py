import os
import sqlite3
import re

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import get_llm, get_embeddings


class HybridRAG:

    def __init__(self):

        # LLM

        self.llm = get_llm()

        # Embeddings

        self.embeddings = get_embeddings()
        # Hybrid RAG data directory

        self.data_directory = "data/hybrid"

        # Chroma

        self.persist_directory = "data/chroma"

        self.collection_name = "business_documents"

        # SQLite database

        self.database = os.path.join(
            self.data_directory,
            "sales.db"
        )
        # Load PDF documents

        self.vector_store = self.load_documents()

    # LOAD PDF DOCUMENTS DYNAMICALLY

    def load_documents(self):

        documents = []

        # Check directory

        if not os.path.exists(self.data_directory):

            raise FileNotFoundError(
                f"Directory not found: {self.data_directory}"
            )
        # Find all PDFs dynamically

        pdf_files = [
            filename
            for filename in os.listdir(
                self.data_directory
            )
            if filename.lower().endswith(".pdf")
        ]

        if not pdf_files:

            raise ValueError(
                "No PDF files found in data/hybrid"
            )
        # Load every PDF

        for filename in pdf_files:

            pdf_path = os.path.join(
                self.data_directory,
                filename
            )

            print(
                f"Loading PDF: {filename}"
            )

            loader = PyPDFLoader(
                pdf_path
            )

            documents.extend(
                loader.load()
            )
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )

        chunks = text_splitter.split_documents(
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

    # GENERATE SQL

    def generate_sql(self, question):

        schema = """
Table: sales

Columns:

id INTEGER
city TEXT
product TEXT
quarter TEXT
revenue REAL
units INTEGER
"""

        prompt = f"""
You are a SQLite SQL expert.

Convert the user's business question into
a read-only SQL query.

Database schema:
{schema}

Question:
{question}

Rules:
- Return ONLY SQL.
- Only generate SELECT queries.
- Do not use INSERT.
- Do not use UPDATE.
- Do not use DELETE.
- Do not use DROP.
- Do not use ALTER.
- Do not use CREATE.
"""

        response = self.llm.invoke(
            prompt
        )

        sql = response.content.strip()

        # Remove markdown code fences
        sql = re.sub(
            r"```(?:sql)?",
            "",
            sql,
            flags=re.IGNORECASE
        ).replace(
            "```",
            ""
        ).strip()

        return sql

    # VALIDATE SQL

    def validate_sql(self, sql):

        sql = sql.strip()

        if not sql.upper().startswith("SELECT"):

            raise ValueError(
                "Only SELECT queries are allowed."
            )

        forbidden = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "CREATE",
            "REPLACE",
            "TRUNCATE"
        ]

        upper_sql = sql.upper()

        for keyword in forbidden:

            if re.search(
                rf"\b{keyword}\b",
                upper_sql
            ):

                raise ValueError(
                    f"Unsafe SQL generated: {keyword}"
                )

    # RUN SQL
    def run_sql(self, sql):

        self.validate_sql(sql)

        if not os.path.exists(self.database):

            raise FileNotFoundError(
                f"Database not found: {self.database}"
            )

        connection = sqlite3.connect(
            self.database
        )

        try:

            cursor = connection.cursor()

            cursor.execute(sql)

            columns = [
                description[0]
                for description in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

        finally:

            connection.close()

    # RETRIEVE DOCUMENTS

    def retrieve_documents(self, question):

        return self.vector_store.similarity_search(
            question,
            k=3
        )
    # GENERATE FINAL ANSWER

    def generate_answer(
        self,
        question,
        sql,
        sql_result,
        documents
    ):

        if documents:

            document_context = "\n\n".join(
                doc.page_content
                for doc in documents
            )

        else:

            document_context = (
                "No relevant business documents found."
            )

        prompt = f"""
You are a business analyst.

Answer the user's question using both:

1. Structured SQL results
2. Relevant business documents

Question:
{question}

SQL Query:
{sql}

SQL Results:
{sql_result}

Relevant Business Documents:
{document_context}

Rules:

- Use SQL results for numerical facts.
- Use documents for business context.
- Do not invent numbers.
- Do not invent business information.
- Clearly explain the result.
- If the available information is insufficient,
  clearly say so.
"""

        response = self.llm.invoke(
            prompt
        )

        return response.content.strip()

    # COMPLETE HYBRID RAG PIPELINE

    def run(self, question):

        # STEP 1: Generate SQL

        sql = self.generate_sql(
            question
        )

        # STEP 2: Execute SQL

        sql_result = self.run_sql(
            sql
        )

        # STEP 3: Retrieve PDF context

        documents = self.retrieve_documents(
            question
        )

        # STEP 4: Generate final answer

        answer = self.generate_answer(
            question,
            sql,
            sql_result,
            documents
        )

        # STEP 5: Return everything
        return {
            "answer": answer,
            "sql": sql,
            "sql_result": sql_result,
            "documents": documents
        }