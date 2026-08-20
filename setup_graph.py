import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)


def create_graph():

    with driver.session(
        database=os.getenv("NEO4J_DATABASE", "neo4j")
    ) as session:

        # Clear existing graph
        session.run(
            "MATCH (n) DETACH DELETE n"
        )

        # -------------------------------------------------
        # DEPARTMENTS
        # -------------------------------------------------

        departments = [
            "AI Department",
            "HR Department",
            "Engineering Department",
            "Finance Department",
            "Sales Department",
            "IT Department"
        ]

        for department in departments:
            session.run(
                """
                CREATE (:Department {name: $name})
                """,
                name=department
            )

        # -------------------------------------------------
        # EMPLOYEES
        # -------------------------------------------------

        employees = [
            ("Rahul", "AI Department"),
            ("Priya", "AI Department"),
            ("Arjun", "AI Department"),

            ("Amit", "HR Department"),
            ("Sneha", "HR Department"),

            ("Vikram", "Engineering Department"),
            ("Neha", "Engineering Department"),
            ("Rohan", "Engineering Department"),

            ("Ananya", "Finance Department"),
            ("Karan", "Finance Department"),

            ("Meera", "Sales Department"),
            ("Pooja", "Sales Department"),

            ("Aditya", "IT Department"),
            ("Isha", "IT Department"),
            ("Varun", "IT Department")
        ]

        for employee_name, department_name in employees:

            session.run(
                """
                MATCH (d:Department {name: $department})
                CREATE (e:Employee {name: $employee})
                CREATE (e)-[:WORKS_IN]->(d)
                """,
                employee=employee_name,
                department=department_name
            )

        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        projects = [
            "Phoenix",
            "AI Recruitment",
            "HRMS",
            "Payroll Automation",
            "Customer Analytics",
            "Cloud Migration",
            "Fraud Detection",
            "Employee Portal"
        ]

        for project in projects:

            session.run(
                """
                CREATE (:Project {name: $name})
                """,
                name=project
            )

        # -------------------------------------------------
        # TECHNOLOGIES
        # -------------------------------------------------

        technologies = [
            "Python",
            "LangGraph",
            "Django",
            "React",
            "PostgreSQL",
            "FastAPI",
            "Docker",
            "AWS",
            "Neo4j",
            "Machine Learning"
        ]

        for technology in technologies:

            session.run(
                """
                CREATE (:Technology {name: $name})
                """,
                name=technology
            )

        # -------------------------------------------------
        # MANAGERS
        # -------------------------------------------------

        manager_relationships = [
            ("Priya", "AI Department"),
            ("Amit", "HR Department"),
            ("Vikram", "Engineering Department"),
            ("Ananya", "Finance Department"),
            ("Meera", "Sales Department"),
            ("Aditya", "IT Department")
        ]

        for employee, department in manager_relationships:

            session.run(
                """
                MATCH
                    (e:Employee {name: $employee}),
                    (d:Department {name: $department})

                CREATE (e)-[:MANAGES]->(d)
                """,
                employee=employee,
                department=department
            )

        # -------------------------------------------------
        # EMPLOYEE → PROJECT RELATIONSHIPS
        # -------------------------------------------------

        works_on = [
            ("Rahul", "Phoenix"),
            ("Priya", "AI Recruitment"),
            ("Arjun", "Fraud Detection"),

            ("Amit", "HRMS"),
            ("Sneha", "Employee Portal"),

            ("Vikram", "Cloud Migration"),
            ("Neha", "Phoenix"),
            ("Rohan", "Customer Analytics"),

            ("Ananya", "Payroll Automation"),
            ("Karan", "Payroll Automation"),

            ("Meera", "Customer Analytics"),
            ("Pooja", "Employee Portal"),

            ("Aditya", "Cloud Migration"),
            ("Isha", "HRMS"),
            ("Varun", "Phoenix")
        ]

        for employee, project in works_on:

            session.run(
                """
                MATCH
                    (e:Employee {name: $employee}),
                    (p:Project {name: $project})

                CREATE (e)-[:WORKS_ON]->(p)
                """,
                employee=employee,
                project=project
            )

        # -------------------------------------------------
        # PROJECT → TECHNOLOGY RELATIONSHIPS
        # -------------------------------------------------

        project_technologies = {
            "Phoenix": [
                "Python",
                "LangGraph",
                "Neo4j"
            ],

            "AI Recruitment": [
                "Python",
                "LangGraph",
                "Machine Learning"
            ],

            "HRMS": [
                "Django",
                "React",
                "PostgreSQL"
            ],

            "Payroll Automation": [
                "Python",
                "Django",
                "PostgreSQL"
            ],

            "Customer Analytics": [
                "Python",
                "Machine Learning",
                "FastAPI"
            ],

            "Cloud Migration": [
                "AWS",
                "Docker",
                "FastAPI"
            ],

            "Fraud Detection": [
                "Python",
                "Machine Learning",
                "Neo4j"
            ],

            "Employee Portal": [
                "React",
                "Django",
                "PostgreSQL"
            ]
        }

        for project, technologies_list in project_technologies.items():

            for technology in technologies_list:

                session.run(
                    """
                    MATCH
                        (p:Project {name: $project}),
                        (t:Technology {name: $technology})

                    CREATE (p)-[:USES]->(t)
                    """,
                    project=project,
                    technology=technology
                )


if __name__ == "__main__":

    create_graph()

    driver.close()

    print("Graph created successfully!")