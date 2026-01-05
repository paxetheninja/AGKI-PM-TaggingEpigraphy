## 1. Gregor – The Digital Epigrapher
**"I want to see the patterns that are invisible when reading inscriptions one by one."**
- **Role:** Post-Doc Researcher / Digital Humanist
- **Age:** 30
- **Domain Focus:** Social and Religious History (Non-Military)
- **Tech Literacy:** High. Uses Python for basic data analysis; eager to adopt new tools.
- **Background:** Gregor is researching the financing of cults in the Aegean. He is tired of manually sifting through the PHI database and wants to automate the categorization of "economic" vs. "religious" texts.
- **Goals:**
    - Perform complex, multi-layered queries (e.g., "Economic > Finance" AND "Religious > Cult" AND NOT "Military").
    - Export large datasets (JSON/CSV) to visualize networks of cult officials.
    - Discover "serendipitous" connections—texts he wouldn't have found through keyword search alone.
- **Frustrations:**
    - Keyword searches (e.g., "money") return too many irrelevant military decrees.
    - Standard databases lack hierarchical metadata (they have dates/places, but not "topics").
- **Key User Story:** _As Gregor, I want to filter the corpus for 'Sacred Manumission' in Central Greece to analyze the cost variations of buying freedom, without seeing thousands of military pay lists._
---
## 2. Matthias – The Pragmatic Lecturer
**"I need clear, representative examples for my seminar, and I need them quickly."**
- **Role:** University Lecturer
- **Age:** 35
- **Domain Focus:** Teaching (Military History & Administration)
- **Tech Literacy:** Medium. Uses digital tools to prepare slides and handouts.
- **Background:** Matthias teaches "Introduction to Greek Epigraphy." He needs to find "study-friendly" inscriptions—texts that are well-preserved, have clear context, and illustrate specific historical concepts for his students.
- **Goals:**
    - Quickly find "clean" examples of specific types (e.g., a "Proxeny Decree") that are complete enough for students to read.
    - Access reliable metadata to explain the context to students.
    - Save time on lesson preparation.
- **Frustrations:**
    - Wasting time clicking through fragmentary or damaged inscriptions that are useless for teaching.
    - Difficulty finding texts that clearly exemplify a specific legal or administrative category.
- **Key User Story:** _As Matthias, I want to filter by 'Text Completeness' and 'Category: Judicial' so I can find a well-preserved law code to discuss in next week's class._
---
## 3. Stephan-Felix – The Ancient History Student
**"I need to understand what this text is about so I can cite it in my paper."**
- **Role:** Master's Student
- **Age:** 24-27
- **Domain Focus:** General Ancient History
- **Tech Literacy:** Digital Native, but relies on Google/Wikipedia for context.
- **Background:** Stephan-Felix is writing a paper on "Honors for Foreigners." He can read Greek but struggles with the technical jargon of epigraphy. He needs the tool to guide him toward relevant sources and explain _why_ they are relevant.
- **Goals:**
    - Find primary sources for his essays without reading the entire corpus.
    - Understand the "Tags" – why is this text classified as "Political"?
    - Get correct citation formats (PHI ID, Corpus reference).
- **Frustrations:**
    - Feeling overwhelmed by the sheer volume of raw Greek text in PHI.
    - Unsure if he has translated a technical term correctly; needs context.
- **Key User Story:** _As Stephan-Felix, I want to click on a 'Rationale' button next to a tag to understand why the AI classified this fragment as an 'Honorary Decree', so I can argue my point in my essay._
---
## 4. Herbert – The Critical Expert
**"Just give me the text. I don't trust the machine, but I need the reference."**
- **Role:** Professor of Ancient History
- **Age:** 58
- **Domain Focus:** Classical Epigraphy & Political History
- **Tech Literacy:** Low/Skeptical. prefers printed corpora (IG, SEG) but uses PHI for speed.
- **Background:** Herbert knows the corpus inside out. He uses the tool to verify readings or look up specific references. He is highly critical of AI "hallucinations" and fears the tool might mislead students.
- **Goals:**
    - Direct access: Enter a reference (e.g., "IG II² 123") and go straight to the text.
    - Verify the AI: He wants to see the confidence score to know if he should trust the classification.
    - Flag errors: He wants to correct the system when the AI is wrong.
- **Frustrations:**
    - "Black Box" algorithms that hide how a conclusion was reached.
    - Slow interfaces or "wizards" that prevent him from just getting the text.
    - Inaccurate classifications that muddle diplomatic categories.
- **Key User Story:** _As Herbert, I want to search directly by 'IG II²' reference and see the confidence score of the AI tags, so I can quickly dismiss low-confidence guesses and focus on the philological text._
---
## 5. Florian – The Developer & AI Researcher
**"I need to know where the pipeline breaks and how to optimize the prompts."**
- **Role:** Project Developer / Computational Linguist
- **Age:** 26
- **Domain Focus:** NLP, LLMs, Data Engineering
- **Tech Literacy:** Expert.
- **Background:** Florian is building the "Tagging Epigraphy" platform. He is less interested in the history and more in the performance of the model (Precision/Recall), the validity of the JSON output, and the system architecture.
- **Goals:**
    - Monitor the pipeline: Ensure batch processing of PHI JSONs doesn't crash.
    - Optimize Costs/Tokens: efficient prompting.
    - Debug: See the "Raw Output" of the LLM to understand why a specific tag was generated.
- **Frustrations:**
    - Inconsistent JSON outputs from the LLM (Schema violations).
    - Ambiguous edge cases where the taxonomy isn't clear, causing model confusion.
- **Key User Story:** _As Florian, I want to view a log of 'Validation Errors' where the LLM output didn't match the JSON Schema, so I can tweak the system prompt to be more strict._