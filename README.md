# The Complete RAG Architectures Master Study Guide
### A Presentation-Ready Reference for Retrieval-Augmented Generation Systems

---

## MODULE 1: THE ANATOMY OF A RAG SYSTEM (THE BASELINE)

### 1.1 The Core Lifecycle

Think of a RAG system as a **restaurant kitchen with a librarian attached**. Before any customer (user) walks in, the librarian has already organized a giant reference library (Ingestion). When a customer places an order (query), the librarian sprints to fetch the exact right pages (Retrieval), and hands them to the chef, who cooks a fresh answer using those pages as ingredients (Generation).

**PHASE 1 — INGESTION (happens before any user ever asks a question)**

1. **Parsing:** Raw source documents (PDFs, HTML, Word docs, Slack exports, database rows) are loaded and stripped of noise — headers, footers, boilerplate, broken formatting.
2. **Chunking:** The clean text is sliced into digestible pieces (e.g., 200–500 tokens each). This matters enormously — a chunk that's too big buries the signal; too small loses context.
3. **Embedding:** Each chunk is passed through an embedding model, which converts the text into a vector — a long list of numbers representing its *meaning* in mathematical space. Similar meanings land near each other in this space.
4. **Vector Storage:** These vectors (plus the original text and metadata like source, date, and author) are stored in a vector database (e.g., Pinecone, Weaviate, Qdrant, pgvector) for fast lookup later.

**PHASE 2 — RETRIEVAL (happens the moment a user asks something)**

1. **Query Embedding:** The user's question is converted into a vector using the *same* embedding model used during ingestion.
2. **Query Matching:** The system searches the vector database for the chunks whose vectors are mathematically "closest" to the query vector.
3. **Distance Metrics:** "Closeness" is calculated using metrics like **Cosine Similarity** (angle between vectors — most common), **Euclidean Distance** (straight-line distance), or **Dot Product** (magnitude-weighted similarity).
4. **Top-K Selection:** The system returns the K best-matching chunks (e.g., top 5) — these are the "evidence" the LLM will use.

**PHASE 3 — GENERATION (the final answer is written)**

1. **Context Assembly:** The retrieved chunks are stitched together into a single "context block" and inserted into a prompt template, alongside the original user question.
2. **Context Synthesis:** The LLM reads the question *and* the retrieved evidence together, and generates an answer that is grounded in — and ideally cites — that evidence, rather than relying purely on its own trained-in memory.
3. **Delivery:** The final answer is returned to the user, often with source citations pointing back to the original documents.

**The Golden Rule:** RAG doesn't change what the LLM *knows how to do* (reason, write, summarize) — it changes what the LLM *has in front of it* when it does that reasoning.

---

### 1.2 The "Why": Why RAG Still Matters in August 2026 (Even With Massive Context Windows)

A common objection today is: "Models now have 1M–10M token context windows — why not just paste the entire knowledge base into the prompt every time?" Four reasons RAG remains essential:

- **💰 Cost:** Feeding millions of tokens into every single query is extraordinarily expensive at scale. Retrieving only the 5–10 relevant chunks (a few thousand tokens) instead of the entire corpus can cut inference cost by orders of magnitude when running thousands of queries per day.
- **✅ Verification:** Long-context "needle in a haystack" recall degrades in practice — models can skim over or under-weight facts buried deep in a massive context. Retrieval narrows the field to only what's relevant, and enables clean citation back to a specific source, which is critical for trust and auditability.
- **🔄 Dynamic Data Updating:** Model weights are frozen at training time. A company's internal wiki, pricing sheet, or product catalog changes daily. RAG lets you update the *retrieval index* in seconds — no retraining, no fine-tuning, no waiting for the next model release.
- **🎯 Precision & Reduced Hallucination:** Grounding generation in explicitly retrieved, verifiable text sharply reduces the chance the model invents facts, because it's "reading off the page" rather than reciting from fuzzy trained-in memory.

---

## MODULE 2: THE COMPLETE COMPENDIUM OF RAG TYPES & ARCHITECTURES

---

### CATEGORY A: THE CORE PARADIGMS

---

#### 1. Naive (Standard) RAG

💡 **Concept:** The "vanilla" version — exactly the three-phase pipeline from Module 1, with no bells or whistles. Think of it as a librarian who grabs the first five books that superficially look related and hands them straight to the chef, no double-checking.

⚙️ **Data Flow:**
1. Documents chunked and embedded once, offline.
2. User query embedded as-is.
3. Top-K nearest chunks retrieved via a single similarity search.
4. Chunks inserted into prompt verbatim.
5. LLM generates an answer directly from that context.

🎯 **The Pain Point Solved:** It solves the base problem of hallucination-from-no-context and stale knowledge. It does *not* solve retrieval precision, ranking quality, or complex multi-hop reasoning.

🏢 **Use-Case:** A simple internal FAQ bot over a small, clean, well-structured knowledge base (e.g., an HR policy chatbot) where queries are simple, factual, and single-hop.

---

#### 2. Advanced RAG (Pre/Post-Retrieval Optimization)

💡 **Concept:** Naive RAG with quality-control checkpoints added *before* the search (cleaning the question) and *after* the search (cleaning the results) — like an editor who polishes the question before it reaches the librarian, and re-checks the books before they reach the chef.

⚙️ **Data Flow:**
1. **Pre-retrieval:** Query is cleaned, expanded, or rewritten; metadata filters may be applied (e.g., "only search 2026 documents").
2. Query embedded and searched.
3. **Post-retrieval:** Retrieved chunks are re-ranked by a specialized cross-encoder re-ranker model for true relevance (not just vector distance), and irrelevant chunks are filtered/compressed.
4. Cleaned, ranked chunks passed to the LLM.
5. LLM generates the final answer.

🎯 **The Pain Point Solved:** Fixes the "garbage in, garbage out" problem of Naive RAG — poor query phrasing and noisy retrieved chunks that dilute answer quality.

🏢 **Use-Case:** Enterprise search assistants over large, messy document repositories (e.g., legal contract search) where raw similarity search alone returns too much noise.

---

#### 3. Modular RAG (Plugin-Based Flexible Routing)

💡 **Concept:** Instead of one fixed pipeline, imagine a set of interchangeable Lego blocks — a routing module, a search module, a memory module, a fusion module — that can be assembled and reordered depending on the task. It's the architectural "framework" that most of the other types in this guide plug into.

⚙️ **Data Flow:**
1. Incoming query hits a **router** module.
2. Router decides which retrieval module(s) to invoke (vector search, keyword search, an API call, a SQL query, etc.) based on query type.
3. Selected module(s) execute in parallel or in sequence.
4. A **fusion module** merges and deduplicates results from multiple sources.
5. Optional **memory module** injects conversation history.
6. LLM generates the final synthesized answer.

🎯 **The Pain Point Solved:** Fixes the rigidity of a single, one-size-fits-all pipeline — different queries genuinely need different retrieval strategies.

🏢 **Use-Case:** A production-grade enterprise copilot that must handle document Q&A, structured database lookups, and live API calls all inside one chat interface.

---

### CATEGORY B: QUERY-TRANSFORMATION & OPTIMIZATION TECH

---

#### 4. HyDE (Hypothetical Document Embeddings)

💡 **Concept:** Instead of searching with the *question*, the system first asks the LLM to imagine what a perfect *answer* would look like, then searches using that imagined answer. It's like describing your dream house to a friend so they can go find real listings that match its "shape," rather than searching using your vague request alone.

⚙️ **Data Flow:**
1. User submits a query.
2. LLM generates a hypothetical, plausible-sounding answer document (which may contain inaccuracies — that's fine, it's never shown to the user).
3. That hypothetical document is embedded (not the original query).
4. This hypothetical-document vector searches the vector database.
5. Real chunks that closely resemble the *hypothetical answer's phrasing and structure* are retrieved.
6. LLM generates the final, grounded answer using these real chunks.

🎯 **The Pain Point Solved:** Fixes the "vocabulary mismatch" problem — short, terse questions often use different wording than the answer passages that would satisfy them, so direct query-to-document matching underperforms.

🏢 **Use-Case:** Technical/scientific Q&A systems where questions are phrased casually but the source documents use dense, formal, jargon-heavy language.

---

#### 5. RAG-Fusion / Multi-Query RAG (with Reciprocal Rank Fusion)

💡 **Concept:** Instead of asking the librarian one question, you ask them the same question rephrased five different ways, then combine and re-rank all the books each version returned. Like triangulating a target from multiple angles instead of trusting one shot.

⚙️ **Data Flow:**
1. LLM generates N variations of the original query (different phrasings/angles).
2. Each variant query is independently embedded and searched.
3. Each search returns its own ranked list of chunks.
4. **Reciprocal Rank Fusion (RRF)** algorithm combines all lists — chunks appearing high in *multiple* lists get boosted scores.
5. The final fused, re-ranked list is passed to the LLM.
6. LLM synthesizes the answer.

🎯 **The Pain Point Solved:** Fixes single-query blind spots — one phrasing of a question may miss relevant chunks that a slightly different phrasing would catch.

🏢 **Use-Case:** Broad research or discovery queries (e.g., "what are the risks of this M&A deal?") where the ideal answer likely spans multiple angles/subtopics.

---

#### 6. Step-Back Query RAG (Abstracting the Prompt for Broader Context)

💡 **Concept:** Before diving into specifics, the system asks a more general, "zoomed-out" version of the question first — like a doctor asking about your overall health history before zeroing in on your specific symptom.

⚙️ **Data Flow:**
1. User asks a specific, narrow question.
2. LLM generates a "step-back" abstraction — a broader, higher-level version of that question (e.g., "What was Instagram's user growth in 2023?" → step-back → "What is Instagram's overall growth history?").
3. Both the original specific query AND the step-back query are used to retrieve chunks (often two separate searches).
4. Both result sets are combined into context.
5. LLM answers the original specific question, now armed with both fine-grained and broad background context.

🎯 **The Pain Point Solved:** Fixes shallow answers to questions that actually require background/foundational context to answer correctly — narrow retrieval alone misses the "big picture" facts needed for reasoning.

🏢 **Use-Case:** Multi-step analytical or reasoning-heavy queries in finance, science, or policy analysis, where surface-level facts alone lead to an incomplete answer.

---

#### 7. Query Rewriting / Reformulation RAG

💡 **Concept:** A dedicated "translator" module sits between the user and the search engine, cleaning up typos, resolving ambiguous pronouns, and rewriting casual chat-speak into a clear, self-contained, searchable question.

⚙️ **Data Flow:**
1. Raw user query received (possibly full of typos, slang, or references like "what about that one from before?").
2. A rewriting LLM call reformulates the query into a clear, standalone, context-resolved question — pulling in relevant context from chat history if needed.
3. The rewritten query is embedded and searched.
4. Retrieved chunks passed to generation.
5. LLM answers using the clarified intent.

🎯 **The Pain Point Solved:** Fixes poor retrieval caused by ambiguous, conversational, or context-dependent queries — especially critical in multi-turn chat where "it" or "that" refers to something said three messages ago.

🏢 **Use-Case:** Multi-turn conversational assistants and customer support chatbots where follow-up questions constantly reference earlier turns.

---

### CATEGORY C: ADVANCED STRUCTURING & CHUNKING LAYOUTS

---

#### 8. Parent-Child / Sub-Document RAG

💡 **Concept:** Search using small, precise index cards, but once you find the right one, hand the chef the entire chapter it came from — not just the card. Small chunks are great for *finding* things; big chunks are great for *understanding* things.

⚙️ **Data Flow:**
1. During ingestion, each document is split into small "child" chunks (e.g., single sentences or 100 tokens) AND larger "parent" chunks (e.g., full sections or 1000 tokens) that contain those children.
2. Only the small child chunks are embedded and indexed for search — small chunks produce sharper, more precise vector matches.
3. At query time, the system searches over child-chunk vectors.
4. Once a matching child is found, the system fetches its *parent* chunk (via a stored mapping/ID reference) instead of the tiny child text.
5. The full parent chunk(s) are passed to the LLM as context.
6. LLM generates the answer with rich surrounding context, not a fragment.

🎯 **The Pain Point Solved:** Fixes the fundamental chunk-size trade-off: small chunks retrieve precisely but lack context; large chunks have context but retrieve imprecisely (their vector represents a diluted "average" meaning).

🏢 **Use-Case:** Long-form legal or technical documents where a single sentence needs to be found precisely, but the LLM needs the surrounding clauses/paragraph to interpret it correctly.

---

#### 9. Sentence Window Retrieval

💡 **Concept:** A close cousin of Parent-Child RAG, but instead of a whole "chapter," you grab just the sentences immediately *before and after* the matched sentence — like reading the paragraph around a highlighted line rather than the whole book.

⚙️ **Data Flow:**
1. Documents are split into individual sentences during ingestion, each embedded separately, each tagged with its position in the document.
2. At query time, a search matches on individual sentence vectors (maximum precision).
3. For each matched sentence, the system pulls a fixed "window" of N sentences before and after it from the original document.
4. This expanded window (not the single sentence) is assembled into the context.
5. LLM generates the answer with local context intact.

🎯 **The Pain Point Solved:** Fixes the loss of local context around a highly precise match — a single retrieved sentence is often too terse or ambiguous to answer a question on its own.

🏢 **Use-Case:** Dense technical manuals or medical literature, where one specific sentence contains the exact fact, but a sentence or two of surrounding qualification (dosage limits, exceptions) is essential for a correct answer.

---

#### 10. RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval)

💡 **Concept:** Instead of one flat pile of chunks, build a *tree* — like a corporate org chart of information. Leaf nodes are raw text chunks; each layer above summarizes the layer below it, all the way up to one master summary at the top. Retrieval can then grab a very specific leaf, or a bird's-eye summary, depending on what the question needs.

⚙️ **Data Flow:**
1. Documents chunked into base-level "leaf" chunks and embedded (Layer 0).
2. Similar leaf chunks are clustered together (using an unsupervised clustering algorithm).
3. Each cluster is summarized by an LLM into a single higher-level node (Layer 1).
4. Steps 2–3 repeat recursively — Layer 1 nodes get clustered and summarized into Layer 2, and so on — building a full tree up to a root summary.
5. All nodes at *every* layer (not just the leaves) are embedded and indexed together.
6. At query time, retrieval searches across the whole tree simultaneously, so both fine-grained leaf facts and high-level thematic summaries can be returned.
7. LLM synthesizes an answer using whichever tree level(s) best match the question.

🎯 **The Pain Point Solved:** Fixes RAG's blindness to "big picture" or thematic questions ("What are the overarching risks across this 500-page report?") that no single chunk could ever answer, since flat retrieval can only ever return literal, local text.

🏢 **Use-Case:** Summarizing or reasoning across extremely long documents — annual reports, entire book series, litigation discovery archives — where answers require synthesis across the whole corpus, not one paragraph.

---

#### 11. Hierarchical RAG (Multi-Tiered Global/Local Index Routing)

💡 **Concept:** A two-stage librarian system — first you go to the "floor directory" to pick the right *section* of the library (global index), and only then do you search *within* that section for the exact book (local index). Think of it as coarse-to-fine narrowing.

⚙️ **Data Flow:**
1. A high-level **global index** is built — one summary/embedding per document, folder, or topic cluster (very coarse).
2. A detailed **local index** is built underneath each global entry — the actual fine-grained chunks within that document/topic.
3. At query time, the system first searches the global index to identify the most relevant document(s) or topic cluster(s).
4. The local index *within* those selected documents/clusters is then searched for the specific matching chunks.
5. Only chunks from the pre-filtered relevant zone are passed to the LLM.
6. LLM generates the answer.

🎯 **The Pain Point Solved:** Fixes retrieval accuracy and speed at massive scale — searching every chunk in a million-document corpus is slow and noisy; narrowing to the right neighborhood first dramatically improves both speed and precision.

🏢 **Use-Case:** Enterprise-wide knowledge bases spanning many separate product lines or departments (e.g., a multinational's global document repository), where topic-level routing prevents cross-department contamination of results.

---

### CATEGORY D: KNOWLEDGE-MAP & STRUCTURAL ARCHITECTURES

---

#### 12. Graph RAG / KG-RAG (Knowledge Graph Entity-Relation Traversal)

💡 **Concept:** Instead of a pile of loose index cards, imagine a wall covered in sticky notes connected by strings — "Company A" — [acquired] → "Company B" — [founded by] → "Person C." Retrieval doesn't just fetch a note, it *walks the strings* to gather connected facts.

⚙️ **Data Flow:**
1. During ingestion, an LLM extracts entities (people, companies, products) and their relationships from source text, building a **knowledge graph** (nodes = entities, edges = relationships).
2. The graph is stored in a graph database (e.g., Neo4j) — often alongside a traditional vector index for the raw text too.
3. At query time, entities are extracted from the user's question.
4. The system traverses the graph outward from those entities, following relevant relationship edges (multi-hop traversal).
5. Connected facts/entities gathered along the traversal path are assembled into context — capturing relationships a flat vector search would completely miss.
6. LLM generates an answer that correctly reflects multi-entity relationships.

🎯 **The Pain Point Solved:** Fixes **multi-hop reasoning failure** — vector search finds *similar* text but has no concept of explicit relationships ("Who is the CEO of the company that acquired the company Sarah founded?" requires hopping across three connected facts).

🏢 **Use-Case:** Corporate due-diligence, fraud investigation, or pharmaceutical research, where the answer depends on tracing chains of relationships between entities, not just topical similarity.

---

#### 13. Hybrid RAG (Dense Vector + Sparse BM25 Keyword Matching)

💡 **Concept:** Run two search engines side by side — one that understands *meaning* (semantic/dense vectors) and one that's ruthlessly literal about *exact words* (BM25 keyword search) — then merge their results. Meaning-search alone can miss an exact product SKU or acronym; keyword-search alone can miss a paraphrased question.

⚙️ **Data Flow:**
1. Documents are indexed twice in parallel: once as dense vector embeddings, and once in a traditional sparse keyword index (BM25/TF-IDF).
2. At query time, the same query runs against *both* indexes simultaneously.
3. Dense search returns semantically similar chunks; sparse search returns chunks with exact keyword/term overlap.
4. Results from both are merged and re-ranked (often using RRF, similar to RAG-Fusion) into one unified ranked list.
5. Top merged results passed to the LLM for generation.

🎯 **The Pain Point Solved:** Fixes the classic weakness of pure vector search on exact-match terms — product codes, error codes, legal citation numbers, rare proper nouns — which embeddings often blur together or under-weight.

🏢 **Use-Case:** E-commerce product search or IT support ticketing systems, where users search using precise SKUs/error codes *and* natural-language descriptions interchangeably.

---

#### 14. Vector-SQL Hybrid RAG (Unstructured Text + Structured Tables)

💡 **Concept:** Some answers live in paragraphs; others live in spreadsheets. This architecture lets one query pull from *both* — like asking a research assistant who can read the footnotes *and* run the numbers in the attached spreadsheet.

⚙️ **Data Flow:**
1. Unstructured documents are chunked/embedded as usual into a vector store; structured data (databases, spreadsheets) remains in its native SQL tables.
2. At query time, a router/LLM determines whether the question needs unstructured retrieval, a structured query, or both.
3. For the structured portion: the LLM generates a SQL query (text-to-SQL) from the natural-language question and executes it against the database.
4. For the unstructured portion: a standard vector similarity search runs in parallel.
5. Both the SQL query results (tables/numbers) and the retrieved text chunks are merged into one context block.
6. LLM generates a single coherent answer synthesizing both numeric and narrative evidence.

🎯 **The Pain Point Solved:** Fixes RAG's blindness to structured, tabular business data — vector search is fundamentally bad at precise aggregation, filtering, and math (e.g., "average," "sum," "top 10 by revenue"), which SQL handles natively.

🏢 **Use-Case:** Business intelligence copilots that must answer questions like "Summarize customer complaints about Product X *and* tell me its Q3 revenue trend" in one response.

---

### CATEGORY E: AUTONOMOUS, EVALUATIVE & ITERATIVE SYSTEMS

---

#### 15. Agentic RAG (Autonomous LLM Research Loops with Multi-Tool Usage)

💡 **Concept:** Instead of a single librarian trip, the LLM becomes an autonomous research agent — it can decide to search the vector DB, then decide that's insufficient, then call a web search tool, then a calculator, then loop back and search again — all on its own judgment, like a human analyst conducting open-ended research.

⚙️ **Data Flow:**
1. User query received by an LLM acting as a planning **agent**.
2. Agent decides which tool to invoke first (vector search, SQL query, web search, calculator, code execution, etc.).
3. Tool executes; result is returned to the agent.
4. Agent evaluates whether it now has enough information to answer.
5. If not, agent decides on and invokes the *next* tool/action — this loop (plan → act → observe) repeats an arbitrary number of times.
6. Once the agent judges it has sufficient evidence, it synthesizes and returns the final answer.

🎯 **The Pain Point Solved:** Fixes RAG's rigid, single-shot retrieval limitation — many real questions require multiple, *sequential*, decision-dependent lookups that can't be predicted in advance by a fixed pipeline.

🏢 **Use-Case:** Complex research or analyst-style assistants (e.g., "Research this company's litigation history, cross-reference it with recent news, and estimate risk exposure") requiring open-ended, multi-tool investigation.

---

#### 16. Corrective RAG / CRAG (Algorithmic Validation with Web-Search Fallback)

💡 **Concept:** A built-in quality inspector grades every batch of retrieved documents before they reach the chef. If the batch is bad, it doesn't just shrug — it goes and fetches fresher ingredients from an external source (the live web) instead.

⚙️ **Data Flow:**
1. Standard retrieval occurs, pulling top-K chunks from the vector index.
2. A lightweight **evaluator model** grades the retrieved chunks as "Correct," "Ambiguous," or "Incorrect" relative to the query.
3. If graded **Correct** → chunks are refined/compressed and passed straight to generation.
4. If graded **Incorrect** → the system discards the internal chunks and triggers a **live web search** as a fallback to find better evidence.
5. If graded **Ambiguous** → both internal chunks and supplementary web results are combined.
6. LLM generates the final answer from whichever evidence passed inspection.

🎯 **The Pain Point Solved:** Fixes silent failures — Naive RAG will confidently generate an answer even from irrelevant retrieved chunks. CRAG adds a self-checking safety net so bad retrieval doesn't quietly poison the final answer.

🏢 **Use-Case:** Customer-facing support bots where internal documentation may be incomplete or outdated, and a fallback to verified external sources meaningfully improves reliability.

---

#### 17. Self-RAG (Token-Level Self-Critique and Dynamic Retrieval)

💡 **Concept:** The model doesn't just retrieve once and write — it constantly asks itself, mid-sentence, "Do I actually need to look something up right now to keep being accurate?" and grades its own output for being supported, relevant, and useful as it goes.

⚙️ **Data Flow:**
1. LLM begins generating a response to the query.
2. At each step, the model emits special internal **reflection tokens** deciding: "Retrieve now?" (yes/no).
3. If "yes," a retrieval call is triggered *on the fly*, mid-generation, injecting fresh chunks exactly when needed (rather than once, upfront).
4. After generating a candidate segment, the model self-critiques it with more reflection tokens: is this segment relevant, is it fully supported by the retrieved evidence, is it useful?
5. Low-scoring segments are revised or regenerated.
6. The final response is assembled only from segments that pass the model's own self-critique.

🎯 **The Pain Point Solved:** Fixes wasteful, unnecessary retrieval (not every sentence needs external facts) *and* fixes unsupported/hallucinated claims slipping through unchecked, by building critique directly into the generation loop itself.

🏢 **Use-Case:** Long-form, high-stakes content generation (e.g., medical or financial report drafting) where each individual claim needs to be independently verifiable and appropriately grounded.

---

#### 18. Adaptive RAG (Intent-Routing Based on Query Complexity)

💡 **Concept:** A triage nurse at the front desk decides how serious your case is before routing you — a simple sniffle goes straight to a quick checkup (no retrieval needed at all), while a complex case gets routed to multi-step specialist review (full agentic RAG). Not every question deserves the same amount of machinery.

⚙️ **Data Flow:**
1. Incoming query hits a lightweight **complexity classifier** (often a small, fast model).
2. Classifier labels the query as: (a) simple/no-retrieval-needed — LLM can answer directly from its own knowledge; (b) single-step — one standard retrieval pass suffices; or (c) complex/multi-hop — requires iterative or agentic retrieval.
3. Query is routed to the matching pipeline strength based on that label.
4. The selected pipeline executes (anywhere from zero retrieval calls to a full multi-step agent loop).
5. LLM generates the final answer using whatever context that pipeline gathered.

🎯 **The Pain Point Solved:** Fixes wasted compute/latency — running full heavyweight multi-hop retrieval on a trivial greeting ("hi, what's 2+2?") is slow and unnecessary; Adaptive RAG scales effort to actual need.

🏢 **Use-Case:** High-traffic consumer chat products where query difficulty varies enormously turn-by-turn, and cost/latency efficiency at scale is a core product requirement.

---

#### 19. Iterative / Interleaved RAG (Continuous Generation-Then-Retrieval Loop)

💡 **Concept:** Rather than retrieve once and generate once, the system alternates: generate a bit, notice a gap, retrieve to fill that gap, generate a bit more, notice the next gap, retrieve again — weaving retrieval and writing together like a student writing an essay while repeatedly flipping back to source material paragraph by paragraph.

⚙️ **Data Flow:**
1. Initial retrieval pass gathers a starting context set.
2. LLM begins generating the answer using that context.
3. As generation proceeds, the system detects when the model needs a fact it doesn't currently have (an information gap).
4. A fresh, targeted retrieval query is issued *based on what's already been generated so far* (not just the original question).
5. Newly retrieved chunks are injected, and generation continues/resumes.
6. Steps 3–5 repeat until the full, multi-part answer is complete.

🎯 **The Pain Point Solved:** Fixes single-shot retrieval's inability to support long, multi-part answers where later parts of the answer require *different* evidence than earlier parts (a single upfront search can't anticipate every sub-topic needed).

🏢 **Use-Case:** Long-form report or multi-step tutorial generation (e.g., "write a complete implementation guide for X"), where each section logically requires its own distinct supporting evidence.

---

#### 20. Speculative RAG (Small-Model Drafting, Large-Model Verification)

💡 **Concept:** A junior analyst (small, fast model) quickly drafts several candidate answers in parallel using different evidence subsets; a senior partner (large, powerful model) then reviews and picks/refines the best one — getting near-large-model quality at a fraction of the latency and cost.

⚙️ **Data Flow:**
1. Retrieval returns a broader-than-usual set of relevant chunks, clustered into several distinct evidence subsets.
2. A small, fast, cheap "drafter" LLM generates a candidate answer *in parallel* for each evidence subset.
3. All candidate drafts are collected.
4. A large, more capable "verifier" LLM reviews all drafts against the full evidence, scoring each for accuracy and coherence.
5. The verifier either selects the best draft outright or synthesizes/edits a final answer combining the strongest elements.
6. Final verified answer is returned to the user.

🎯 **The Pain Point Solved:** Fixes the latency/cost of always running a single, slow, expensive large model end-to-end — parallel cheap drafting plus a single verification pass is often both faster and cheaper while preserving quality.

🏢 **Use-Case:** Latency-sensitive, high-volume production systems (e.g., live customer chat) that still need large-model-level answer quality without large-model-level response times.

---

### CATEGORY F: REAL-TIME & ADVANCED DATA MODAL ELEMENTS

---

#### 21. Multimodal RAG (Retrieving Charts, Images, Layouts, and Video Timeframes)

💡 **Concept:** The librarian's shelves aren't just books anymore — they include photo albums, architectural blueprints, and video tapes. Retrieval must be able to find and hand over *any* of these formats, not just text passages, and the "chef" (LLM) must be able to actually look at them.

⚙️ **Data Flow:**
1. During ingestion, non-text elements (images, charts, tables-as-images, video frames) are extracted alongside regular text — often using a vision-capable model to generate rich text descriptions/captions of visual content.
2. Both text chunks and visual elements are embedded — sometimes with a unified multimodal embedding model that places text and images in the *same* vector space, sometimes with separate embeddings linked by metadata.
3. At query time, the query (which may itself contain an image) is embedded and searched across both modalities simultaneously.
4. Matching text chunks *and* matching images/chart crops/video timestamps are retrieved together.
5. A multimodal-capable LLM receives both the text context and the actual visual content (not just a caption) as input.
6. LLM generates an answer that reasons over both text and visual evidence.

🎯 **The Pain Point Solved:** Fixes RAG's traditional text-only blindness — critical information in technical manuals, financial reports, and product catalogs frequently lives in a chart, diagram, or photo, not in prose.

🏢 **Use-Case:** Engineering documentation assistants (retrieving the correct schematic diagram) or financial analysis tools (retrieving and reasoning over the actual chart image from an earnings report, not just its caption).

---

#### 22. Streaming / Dynamic RAG (Querying Live, Continuous Data Telemetry Streams)

💡 **Concept:** Instead of a static library that's updated occasionally, imagine a newsroom ticker that never stops — sensor readings, stock prices, live logs — flowing in continuously. Retrieval here isn't "find the right old book," it's "tell me what's happening *right now* within this constantly moving river of data."

⚙️ **Data Flow:**
1. A continuous data stream (IoT sensor feed, live logs, real-time market data, social media firehose) is ingested incrementally, often through a stream-processing layer (e.g., Kafka).
2. Incoming events are embedded and indexed in near-real-time (often into a rolling/time-windowed index rather than a permanent static one), with older data aged out or archived.
3. At query time, retrieval targets the most recent, relevant window of the stream — frequently combined with time-based filters (e.g., "last 5 minutes").
4. Retrieved live data points are assembled into context, often alongside relevant static/historical knowledge for comparison.
5. LLM generates an answer reflecting the current, live state of the system — not a stale snapshot.

🎯 **The Pain Point Solved:** Fixes the "freshness ceiling" of standard RAG, where the index is only as current as the last batch ingestion job — some domains (fraud detection, operations monitoring, live trading) genuinely need second-by-second freshness.

🏢 **Use-Case:** Real-time operations dashboards or anomaly-detection copilots (e.g., "what's happening with server cluster 4 right now?") built on live infrastructure telemetry.

---

## MODULE 3: ARCHITECTURAL SELECTION MATRIX

| RAG Type | Implementation Complexity | Compute Resource Cost | Primary Structural Strength | When to Avoid It |
|---|---|---|---|---|
| Naive (Standard) RAG | Low | Low | Fast to build; simple to reason about | Complex, multi-hop, or ambiguous queries |
| Advanced RAG | Medium | Medium | Cleaner retrieval via re-ranking + filtering | Ultra-low-latency requirements |
| Modular RAG | High | Medium–High | Maximum flexibility across query types | Small, single-purpose bots (overkill) |
| HyDE | Medium | Medium (extra LLM call) | Bridges question/answer vocabulary gap | Highly factual, keyword-exact queries |
| RAG-Fusion / Multi-Query | Medium | Medium–High (N searches) | Broader recall across phrasings | Simple, unambiguous single-fact queries |
| Step-Back Query RAG | Medium | Medium (extra LLM call) | Supplies missing background context | Narrow factoid lookups |
| Query Rewriting RAG | Low–Medium | Low–Medium | Handles conversational/ambiguous input | Single-turn, already-clear queries |
| Parent-Child RAG | Medium | Medium (dual storage) | Precision search + rich context delivery | Very short, atomic documents |
| Sentence Window Retrieval | Medium | Low–Medium | Maximum precision with local context | Documents needing broad thematic context |
| RAPTOR | High | High (recursive summarization) | Handles both detail and thematic queries | Small corpora; frequently-changing data |
| Hierarchical RAG | High | Medium–High | Scales to massive, multi-domain corpora | Small, single-topic knowledge bases |
| Graph RAG / KG-RAG | High | High (graph build + traversal) | True multi-hop relational reasoning | Unstructured, relation-poor content |
| Hybrid RAG (Dense+BM25) | Medium | Medium (dual index) | Balances semantic + exact-match recall | Purely conversational, non-technical text |
| Vector-SQL Hybrid RAG | High | Medium–High | Unifies narrative + numeric/tabular answers | Domains with no structured data at all |
| Agentic RAG | High | High (many LLM calls) | Handles open-ended, multi-step research | Latency-critical, simple lookups |
| Corrective RAG (CRAG) | Medium–High | Medium (evaluator + fallback) | Self-checks and recovers from bad retrieval | Static, already-reliable internal data |
| Self-RAG | High | High (fine-tuning + reflection tokens) | Built-in claim-level self-verification | Teams without capacity to fine-tune models |
| Adaptive RAG | Medium | Low–High (varies by route) | Cost/latency efficiency at scale | Low-traffic apps with uniform query types |
| Iterative / Interleaved RAG | High | High (repeated retrieval calls) | Supports long, multi-part evidence needs | Short, single-fact answers |
| Speculative RAG | High | Medium (parallel small + 1 large call) | Large-model quality at lower latency | Low-traffic, cost-insensitive setups |
| Multimodal RAG | High | High (vision models + storage) | Reasons over images/charts/video | Purely text-based knowledge bases |
| Streaming / Dynamic RAG | High | High (continuous infra) | Second-by-second data freshness | Static, rarely-changing knowledge |

---

### Quick-Reference Cheat Sheet for Your Presentation

- **Struggling with vague questions?** → HyDE, Query Rewriting, Step-Back
- **Struggling with chunk size trade-offs?** → Parent-Child, Sentence Window
- **Struggling with "big picture" summarization?** → RAPTOR, Hierarchical RAG
- **Struggling with relationships between entities?** → Graph RAG
- **Struggling with exact-match terms (SKUs, codes)?** → Hybrid RAG (BM25)
- **Struggling with numbers/tables?** → Vector-SQL Hybrid RAG
- **Struggling with bad/irrelevant retrieval?** → Corrective RAG, Self-RAG
- **Struggling with multi-step research questions?** → Agentic RAG, Iterative RAG
- **Struggling with cost/latency at scale?** → Adaptive RAG, Speculative RAG
- **Struggling with images/video?** → Multimodal RAG
- **Struggling with live/real-time data?** → Streaming RAG

---

*End of Master Study Guide — ready for direct use in slide construction.*
