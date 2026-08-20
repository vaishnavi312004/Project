import os
import re

from neo4j import GraphDatabase

from . import get_llm


class GraphRAG:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(
                os.getenv("NEO4J_USERNAME"),
                os.getenv("NEO4J_PASSWORD")
            )
        )

        self.database = os.getenv(
            "NEO4J_DATABASE",
            "neo4j"
        )

        self.driver.verify_connectivity()

        self.llm = get_llm()

    # GET DYNAMIC GRAPH SCHEMA

    def get_schema(self):

        with self.driver.session(
            database=self.database
        ) as session:

            labels_result = session.run(
                """
                CALL db.labels()
                YIELD label
                RETURN label
                ORDER BY label
                """
            )

            labels = [
                record["label"]
                for record in labels_result
            ]

            relationships_result = session.run(
                """
                CALL db.relationshipTypes()
                YIELD relationshipType
                RETURN relationshipType
                ORDER BY relationshipType
                """
            )

            relationships = [
                record["relationshipType"]
                for record in relationships_result
            ]

        schema = "Node Labels:\n"

        for label in labels:
            schema += f"- {label}\n"

        schema += "\nRelationship Types:\n"

        for relationship in relationships:
            schema += f"- {relationship}\n"

        schema += """
        
Important:
Employee, Department, Project and Technology nodes
use a name property when available.

For entity names, prefer case-insensitive matching.

For example, if the user says AI and the database
contains AI Department, use:

MATCH (d:Department)
WHERE toLower(d.name) CONTAINS toLower('AI')

Do not assume that the user's wording exactly matches
the stored database value.
"""

        return schema

    # GENERATE CYPHER

    def generate_cypher(self, question):

        schema = self.get_schema()

        prompt = f"""
You are an expert Neo4j Cypher developer.

Convert the user's question into ONE READ-ONLY
Cypher query.

Current graph schema:

{schema}

User question:

{question}

Rules:

- Return ONLY the Cypher query.
- Do not explain the query.
- Use MATCH or OPTIONAL MATCH.
- Use WHERE when filtering is needed.
- Use RETURN.
- DISTINCT is allowed.
- COUNT, SUM, AVG, MIN and MAX are allowed.
- ORDER BY is allowed.
- LIMIT is allowed.
- WITH is allowed.
- Multi-hop traversal is allowed.

Entity matching:

- Do not assume exact database names.
- Use case-insensitive matching.
- Use CONTAINS when the user gives a partial name.
- For example, if the user says AI Department, use:

MATCH (d:Department)
WHERE toLower(d.name) CONTAINS toLower('AI')

instead of assuming:

d.name = 'AI'

- Do not invent labels.
- Do not invent relationship types.
- Do not invent properties.

Security:

- Do NOT use CREATE.
- Do NOT use DELETE.
- Do NOT use SET.
- Do NOT use MERGE.
- Do NOT use REMOVE.
- Do NOT use DROP.
- Do NOT use CALL.
- Do NOT use LOAD CSV.

Return ONLY the Cypher query.
"""

        response = self.llm.invoke(prompt)

        cypher = response.content.strip()

        # Remove markdown code fences
        cypher = re.sub(
            r"```(?:cypher)?",
            "",
            cypher,
            flags=re.IGNORECASE
        )

        cypher = cypher.replace(
            "```",
            ""
        ).strip()

        return cypher

    # VALIDATE CYPHER

    def validate_cypher(self, cypher):

        upper_query = cypher.upper()

        forbidden = [
            "CREATE",
            "DELETE",
            "SET",
            "MERGE",
            "REMOVE",
            "DROP",
            "CALL",
            "LOAD CSV"
        ]

        for keyword in forbidden:

            if re.search(
                rf"\b{keyword}\b",
                upper_query
            ):

                raise ValueError(
                    f"Unsafe Cypher generated: {keyword}"
                )

        if not re.search(
            r"\bMATCH\b",
            upper_query
        ):

            raise ValueError(
                "Generated query does not contain MATCH."
            )
    # EXECUTE CYPHER

    def retrieve(self, cypher):

        self.validate_cypher(cypher)

        with self.driver.session(
            database=self.database
        ) as session:

            result = session.run(cypher)

            return [
                record.data()
                for record in result
            ]

    # GENERATE ANSWER

    def generate_answer(
        self,
        question,
        cypher,
        context
    ):

        prompt = f"""
You are a knowledge assistant.

Answer the question using ONLY the information
retrieved from the Neo4j graph.

Question:
{question}

Cypher query:
{cypher}

Retrieved graph information:
{context}

Rules:

- Do not invent information.
- Do not use outside knowledge.
- Use only the retrieved graph information.
- If the information is insufficient, say so.
- Keep the answer concise and clear.
"""

        response = self.llm.invoke(prompt)

        return response.content

    # MAIN PIPELINE

    def run(self, question):

        try:

            # Generate Cypher dynamically
            cypher = self.generate_cypher(
                question
            )

            # Retrieve graph data
            context = self.retrieve(
                cypher
            )

            # No results
            if not context:

                return {
                    "answer":
                        "No relevant information was found in the graph.",
                    "cypher": cypher,
                    "context": []
                }

            # Generate final answer
            answer = self.generate_answer(
                question,
                cypher,
                context
            )

            return {
                "answer": answer,
                "cypher": cypher,
                "context": context
            }

        except Exception as e:

            return {
                "answer":
                    f"Graph RAG error: {str(e)}",
                "cypher": "",
                "context": []
            }
    # CLOSE CONNECTION
    def close(self):

        self.driver.close()