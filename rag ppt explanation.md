1\. Core Paradigms

Standard / Naive RAG



The basic approach:



Question → Search → Relevant chunks → LLM



👉 Use when the question and documents are straightforward.



Advanced RAG



Adds improvements before/after retrieval, such as better query processing and re-ranking.



👉 Standard RAG + better retrieval.



Modular RAG



Uses separate modules and can combine or route between different retrieval methods.



👉 More flexible RAG.



Easy difference:

Standard = basic | Advanced = improved | Modular = flexible



2\. Query Transformation \& Optimization



These architectures mainly improve the user's question before searching.



HyDE



Instead of directly searching with the question, it first creates a hypothetical answer and searches using that.



👉 Useful when the question itself doesn't match the document wording well.



RAG-Fusion / Multi-Query



Creates multiple versions of the question and searches with them.



👉 Gives different search perspectives.



Step-Back RAG



Moves one step back and asks a broader/general question first.



👉 Useful when the original question needs background knowledge.



Query Rewriting



Rephrases a confusing or poorly written question into a better search query.



👉 Makes retrieval easier.



Easy difference:

All four improve the query, but in different ways:

hypothetical answer | multiple queries | broader query | rewritten query



3\. Advanced Structuring \& Chunking



Here the focus is not mainly on changing the question.

It changes how we organize and retrieve the document information.



Parent-Child RAG



Searches a small child chunk but gives the LLM its larger parent context.



👉 Small for searching, bigger for understanding.



Sentence Window



Finds a relevant sentence and also brings the nearby sentences.



👉 Prevents losing context around the matching sentence.



RAPTOR



Creates summaries at different levels and retrieves from those levels.



👉 Useful for understanding information across a large document.



Hierarchical RAG



Searches from broad → specific levels.



👉 First finds the right section, then finds the relevant information inside it.



Easy difference:

These mainly solve the problem of "How much context should I retrieve, and how should my documents be organized?"



4\. Knowledge / Graph / Hybrid Retrieval



Here we move beyond only vector search.



Graph RAG



Uses relationships between entities.



Example:



Employee → works on → Project → uses → Technology



👉 Good for questions involving relationships and multiple connections.



Hybrid RAG



Uses vector/semantic search + keyword search together.



👉 Useful when both meaning and exact words matter.



Vector-SQL Hybrid RAG



Uses vector search for unstructured information and SQL for structured data.



👉 Useful when you need both documents and database information.



Easy difference:

Graph = relationships | Hybrid = vector + keyword | Vector-SQL = documents + database



5\. Autonomous / Evaluative / Iterative RAG



Here RAG becomes more intelligent and self-managing.



Agentic RAG



The system can decide what to search, which tool to use, and what to do next.



Corrective RAG



Checks the retrieved information and tries to correct poor retrieval.



Self-RAG



The model evaluates its own retrieval and answer.



Adaptive RAG



Chooses an appropriate retrieval strategy depending on the question.



Iterative / Interleaved RAG



Retrieves → thinks/generates → retrieves again → continues.



Speculative RAG



Uses a smaller model to create a draft and a stronger model to verify/refine it.



Easy difference:

These focus on making RAG more intelligent, self-checking, adaptive, or iterative.



6\. Real-Time \& Multimodal

Multimodal RAG



Works with more than text:



Text + Images + Charts + Video



👉 Useful when information isn't only written text.



Streaming / Dynamic RAG



Works with information that changes continuously or needs to stay fresh.



👉 Useful for live or frequently changing information.



Easy difference:

Multimodal = different types of data | Dynamic = changing/live data





We have different RAG architectures because Standard RAG cannot solve every type of problem. Some architectures improve the question, some improve document retrieval and context, some use graphs or databases, some make the system self-evaluating or agentic, and some handle multimodal or real-time information. So we choose the RAG architecture based on the problem we need to solve.









Slide 5 — Query \& Retrieval Optimization

1\. Naive / Standard RAG



How:

Question → Search → Top results → Answer



Problem it solves:

Basic retrieval.



👉 This is our starting/basic RAG.



2\. Advanced RAG



How:

Question → Improve question → Search → Re-rank results → Answer



Why?

Sometimes basic search gives noisy or less relevant results.



👉 It improves the retrieval process.



3\. Modular RAG



How:

Question → Router → Choose Vector / SQL / API → Answer



Why?

Different questions may need different sources.



👉 It makes RAG flexible instead of using only one retrieval method.



4\. HyDE



How:

Question → Create a hypothetical answer → Search using it



Why?

Sometimes the words in the question don't match the words in the documents.



👉 It helps when there is a vocabulary mismatch.



5\. RAG-Fusion / Multi-Query



How:

One question → Multiple versions of the question → Multiple searches → Combine results



Why?

One query may miss useful information.



👉 It searches from multiple perspectives.



6\. Step-Back Query RAG



How:

Specific question → Broader question → Retrieve information



Why?

Sometimes the question needs some background knowledge before we can answer it properly.



👉 It steps back from the specific question to understand the bigger picture.



7\. Query Rewriting RAG



How:

Messy question → Better/re-written question → Search



Why?

Users don't always ask questions clearly.



Example:



"what about leave for next year?"



RAG rewrites it into something more meaningful for retrieval.



👉 It makes unclear/conversational questions easier to search.



🧠 Easy way to remember the differences

Type	Main idea

Standard	Basic search

Advanced	Improve search + ranking

Modular	Choose the right source

HyDE	Search using hypothetical answer

Multi-Query	Search multiple versions

Step-Back	Get broader context

Query Rewriting	Make the question clearer

How you can explain the slide naturally:



"All these architectures are trying to improve retrieval, but they improve different parts. Advanced RAG improves the retrieval process, Modular RAG can choose different sources, HyDE helps with vocabulary mismatch, Multi-Query searches from different perspectives, Step-Back gets broader background information, and Query Rewriting makes unclear questions easier to search."





Slide 6 — Structure \& Indexing



This slide's main idea is:



"Retrieval quality doesn't depend only on embeddings. How we structure and organize the information also matters."



There are 4 approaches here:



1\. Standard RAG



Break the document into chunks → store/search those chunks → answer.



👉 Basic chunk-based retrieval.



2\. Parent-Child RAG



We create a large parent chunk and smaller child chunks.



We search the small child chunks, but when we find a match, we return the larger parent chunk.



👉 Search small, understand with bigger context.



The slide also mentions Sentence Window Retrieval, which follows a similar idea but works around individual sentences.



3\. RAPTOR



It groups similar chunks, creates summaries, and then creates higher-level summaries.



👉 Instead of searching only small chunks, it can retrieve information at different levels of detail.



4\. Hierarchical RAG



It searches in levels:



Global → Relevant document/topic → Local → Relevant chunk



👉 First find the right area, then find the exact information.



🧠 Easy difference



Standard: Search chunks

Parent-Child: Search small → return bigger context

RAPTOR: Chunks → clusters → summaries → higher-level understanding

Hierarchical: Search broad → narrow



Presentation line:



"These architectures mainly focus on how we organize and retrieve information. Standard RAG searches chunks directly, Parent-Child gives larger context after finding a small match, RAPTOR creates different levels of summaries, and Hierarchical RAG searches from broad to specific."





Slide 6 — Beyond Basic Vector Retrieval



Main idea:



"Sometimes normal vector search is not enough, so we combine it with other ways of retrieving information."



1\. Graph RAG



Instead of only searching text, it uses relationships between things.



Example:



Employee → works on → Project → uses → Technology → owned by → Team



👉 Useful when the answer depends on relationships or multiple connections.



2\. Hybrid RAG



Uses two types of search:



Dense search → understands meaning

BM25 → looks for exact words/terms



Then it combines and re-ranks the results.



👉 Useful when both meaning and exact terms matter.



3\. Vector-SQL Hybrid RAG



Uses:



Vector search → documents/text

SQL → structured tables/data



Then combines the information for the LLM.



👉 Useful when one question needs both textual information and numerical/database information.



🧠 Easy difference



Graph RAG → relationships

Hybrid RAG → semantic + exact keyword search

Vector-SQL RAG → documents + database



Presentation line:



"The main idea here is that one retrieval method cannot solve every problem. Graph RAG is useful for relationships, Hybrid RAG combines semantic and keyword search, and Vector-SQL combines document knowledge with structured database data."







Next Slide — Autonomous, Evaluative \& Iterative RAG



Main idea:



"Here, RAG becomes more intelligent — instead of retrieving information once and directly answering, the system can evaluate, decide, correct, or retrieve again."



1\. Agentic RAG



The system can decide what to search and which tool/source to use.



👉 RAG that can make decisions.



2\. Corrective RAG



It checks the retrieved information. If the retrieval is poor, it tries to improve it.



👉 RAG that can correct bad retrieval.



3\. Self-RAG



The model evaluates its own retrieval and answer.



👉 RAG that can self-check.



4\. Adaptive RAG



It chooses a suitable retrieval approach depending on the question or situation.



👉 RAG that adapts to the query.



5\. Iterative / Interleaved RAG



Instead of retrieving only once:



Retrieve → Generate/Reason → Retrieve again → Improve



👉 RAG that works in multiple rounds.



6\. Speculative RAG



A smaller model can create a draft, and a stronger model checks/refines it.



👉 Faster draft + stronger verification.



🧠 Easy difference



Agentic → decides

Corrective → corrects

Self-RAG → self-checks

Adaptive → chooses strategy

Iterative → repeats retrieval

Speculative → drafts + verifies



Presentation line



"These approaches make RAG more intelligent than basic retrieval. Some can make decisions, some evaluate or correct the retrieved information, some adapt to the query, and some perform retrieval in multiple rounds."







Slide 9 — Beyond the Core RAG Types

1\. Traditional Vector RAG



This is the approach we've already studied:



Document → Chunk → Embedding → Vector DB → Similarity Search → Context



👉 It uses dense vector similarity to find relevant information.



2\. Vectorless RAG



Here we don't depend on dense vector similarity.



Instead:



Document → Structure / Index → Reasoning / Navigation → Relevant Sections → Context



👉 It finds information by using the structure of the data and navigation/reasoning, rather than only comparing embeddings.



Simple difference:



Vector RAG = find by semantic similarity

Vectorless RAG = find using structure/navigation



3\. Sparse / BM25 RAG



This uses keyword-based search instead of dense embeddings.



For example, if you search:



ERR\_CONNECTION\_REFUSED



it looks for that exact/important term.



👉 Good for exact terms, error codes, product IDs, names, etc.



Difference:



Dense/vector search → meaning

Sparse/BM25 → keywords



4\. Late-Interaction Retrieval



Instead of representing the whole chunk with one single vector, it performs a more detailed interaction between the query and document.



👉 Useful when we need fine-grained matching and better retrieval precision.



Simple way:



Normal vector RAG → one overall representation

Late interaction → more detailed query-document matching



5\. Temporal RAG



This considers time while retrieving information.



It can consider:



Document versions

Effective dates

Time periods



Example:



"What was our leave policy in 2024?"



👉 It tries to retrieve information relevant to the correct time period.



Useful for policies, regulations, prices, news, etc.



6\. Personalized / Memory-Augmented RAG



This combines external retrieval with user-specific or conversational memory.



Example:



A chatbot remembers the user's previous conversation/preferences and also retrieves information from its knowledge base.



👉 Useful for personalized assistants and long-running conversations.



🧠 Very easy difference

Type	Main idea

Traditional Vector RAG	Find by semantic similarity

Vectorless RAG	Find using structure/navigation

Sparse / BM25	Find using keywords

Late Interaction	Fine-grained query-document matching

Temporal RAG	Consider time/version

Personalized RAG	Use user/conversation memory

🎤 How I'd explain the whole slide



"These are some emerging approaches that go beyond traditional vector RAG. Vectorless RAG retrieves using structure rather than dense similarity, BM25 focuses on exact keywords, Late Interaction provides more fine-grained matching, Temporal RAG considers time and document versions, and Personalized RAG combines retrieval with user or conversation memory. The main point is that vector similarity is only one way of retrieving information; RAG can use different strategies depending on the problem."





**last slide**



**“Till now, we have seen that RAG is not just one fixed pipeline. There are different architectures, and each one solves a different retrieval problem.**



**So instead of asking ‘Which RAG is best?’, we should ask ‘What problem am I trying to solve?’**



**For example:**



**If the question uses different vocabulary from the documents, normal retrieval may struggle. So we can use HyDE — it creates a hypothetical answer and searches using that.**

**If the question is ambiguous or conversational, we can use Query Rewriting to improve the query before searching.**

**If we need multiple perspectives or different search results, we can use RAG-Fusion.**

**If the problem is related to chunk size and context, we can use Parent-Child RAG.**

**For very large documents, RAPTOR helps retrieve information at different levels of abstraction.**

**If the information has relationships between entities, like Employee → Project → Technology, Graph RAG is more suitable.**

**If we need both semantic meaning and exact matching, we can use Hybrid RAG.**

**If the question involves numbers and documents, Vector-SQL Hybrid makes sense because SQL is better for structured numerical data.**

**If the initial retrieval is bad, Corrective RAG checks and improves the retrieval instead of blindly generating an answer.**

**If the question requires multiple steps and research, we can use Agentic RAG.**

**If the query complexity changes from question to question, Adaptive RAG can dynamically choose how much retrieval is needed.**

**If our data contains images, charts or videos, we need Multimodal RAG.**

**If information is changing continuously, like live data, Streaming RAG is useful.**

**If we need exact keywords, codes or SKUs, Sparse/BM25 RAG is useful because keyword matching can be better than semantic similarity.**

**And if the answer depends on time or versions, we use Temporal RAG so that we retrieve information relevant to the correct time period.”**

**The important thing to say at the end**



**The bottom message of the slide is the actual takeaway:**



**“RAG is not a single pipeline. The architecture should match the information problem.”**



**So you can conclude:**



**“We don't need to use a complex RAG architecture everywhere. We should first understand the retrieval problem, start with simple RAG, measure how well retrieval is working, and only add complexity when the problem actually requires it.”**



**Super simple way to remember the whole slide**



**Think of it as:**



**Problem → Choose the RAG architecture**



**If you have...	Think of...**

**Vocabulary mismatch	HyDE**

**Ambiguous question	Query Rewriting**

**Multiple perspectives	RAG-Fusion**

**Chunk/context issue	Parent-Child**

**Huge documents	RAPTOR**

**Relationships	Graph RAG**

**Meaning + exact matching	Hybrid RAG**

**No dense vectors needed	Vectorless RAG**

**Numbers + documents	Vector-SQL Hybrid**

**Poor retrieval	Corrective RAG**

**Complex research	Agentic RAG**

**Different query complexity	Adaptive RAG**

**Images/charts/video	Multimodal RAG**

**Live-changing data	Streaming RAG**

**Exact codes/keywords	Sparse/BM25 RAG**

**Time/version matters	Temporal RAG**



**One-line ending for your presentation:**



**“So the important thing is not knowing the maximum number of RAG types — it is knowing which architecture solves which retrieval problem.”**

