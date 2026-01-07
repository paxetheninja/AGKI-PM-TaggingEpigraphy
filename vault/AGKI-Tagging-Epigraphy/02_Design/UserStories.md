User Stories, filtered into categories based on the [[UserPersonas]] needs.
## Search & Filtering (The "Precision" Layer)
- **Hierarchical Search:** As **Gregor**, I want to filter inscriptions by top-level domains (e.g., "Economic") so that I can broaden my research scope beyond specific keywords like "drachma".
- **Sub-Category Drill-down:** As **Gregor**, I want to select specific sub-categories (e.g., "Economic > Tax > Harbour Dues") to find highly specific evidence for my paper on Aegean trade.
- **Boolean Tagging:** As **Gregor**, I want to search for inscriptions tagged with "Religious" AND "Political" to study the intersection of sacred and civic administration in my datasets.
- **Negative Filtering:** As **Gregor**, I want to exclude inscriptions tagged as "Funerary" so that I can clean my dataset and focus solely on public decrees.
- **Region & Time Intersection:** As **Gregor**, I want to filter by "Attica" + "4th Century BC" + Tag: "Finance" to isolate the Athenian financial administration of a specific era.
- **Confidence Threshold:** As **Herbert**, I want to filter out AI tags with a  low confidence to ensure I am analyzing only high-probability matches and not wasting time on hallucinations.
- **Fragmentary Status:** As **Matthias**, I want to filter out texts with fewer than 50 legible characters so I don't present useless fragments to my students.
- **Text Length Filter:** As **Matthias**, I want to set a minimum character count (e.g., >1000) to find substantial decrees that are suitable for a 90-minute seminar discussion.
- **Entity Role Search:** As **Gregor**, I want to search for inscriptions where a "Woman" plays the role of "Priestess" to visualize gender roles in cult practice across the islands.
- **Publication Reference:** As **Herbert**, I want to search by standard corpus ID (e.g., IG II²) to cross-reference the digital text with the physical volumes on my desk.
- **Keyword in Context:** As **Gregor**, I want to search for a specific Greek lemma (e.g., _agora_) strictly within "Legal" tagged texts to analyze semantic shifts.
- **Datable vs. Undated:** As **Gregor**, I want to toggle between "Precisely Dated," "Circa," and "Undated" inscriptions to build a chronological timeline of tax reforms.
## Visualization & Exploration (The "Macro" Layer)
- **Geospatial Heatmap:** As **Gregor**, I want to see a map showing the density of "Military" inscriptions to visualize conflict zones in the Hellenistic period.
- **Temporal Histogram:** As **Gregor**, I want a timeline bar chart showing the frequency of the tag "Manumission" over centuries to see when the practice peaked.
- **Sunburst Diagram:** As **Stephan-Felix**, I want to interact with a sunburst chart of the taxonomy to visually understand how "Religious" texts are divided into sub-topics like "Sacrifice" or "Dedication."
- **Network Graph (Prosopography):** As **Gregor**, I want to view a node-link diagram connecting people mentioned in the same texts to identify social networks of elites.
- **Tag Co-occurrence Matrix:** As **Florian**, I want a visual matrix showing which tags appear together most often to verify if the model is learning logical correlations.
- **Regional Comparison:** As **Gregor**, I want to view two regions side-by-side (e.g., Athens vs. Delphi) comparing their thematic distribution charts for a comparative study.
- **Drill-down Map:** As **Stephan-Felix**, I want to click on a region (e.g., Crete) on the map and have the text list update immediately so I can explore local history visually.
- **Confidence Visualization:** As **Herbert**, I want the UI to color-code tags (Green/Yellow/Red) based on the AI’s confidence level so I can instantly judge the reliability of an entry.
## Reading & Text Analysis (The "Micro" Layer)
- **Highlighted Evidence:** As **Stephan-Felix**, I want the specific Greek phrase that triggered a tag (e.g., "Religious") to be highlighted in the text so I can learn to identify these formulas myself.
- **Polytonic Support:** As **Herbert**, I need the Greek text to be rendered in a clear, high-quality polytonic font (like New Athena Unicode) because accurate accentuation is non-negotiable for my work.
- **Tag Rationale:** As **Stephan-Felix**, I want to click an "Info" icon next to a tag to read the AI's explanation of _why_ it applied that category, to help me write my essay arguments.
- **Entity Extraction:** As **Stephan-Felix**, I want names of people and places to be underlined, so I can distinguish them from regular vocabulary words.
- **Line Numbering:** As **Herbert**, I need standard line numbering (5, 10, 15) to cite the text accurately in my forthcoming publication.
- **Critical Signs:** As **Herbert**, I need the text to accurately render Leiden Conventions (brackets, dots) to understand the preservation state without consulting the book.
- **Interactive Translation:** As **Stephan-Felix**, I want to see a fluent English or German translation side-by-side with the Greek text, and when I hover over a word in the translation, I want the corresponding Greek word to highlight so I can learn the vocabulary in context.
- **Split View:** As **Matthias**, I want to see the Greek text on the left and the extracted Metadata/Tags on the right to project this view during my lecture.
## Data Management & Export (The "Fair" Layer)
- **Citation Generator:** As **Stephan-Felix**, I want a button to copy a permanent citation for the current inscription, including the date accessed, for my bibliography.
- **Bulk JSON Export:** As **Gregor**, I want to download my filtered search results as a JSON file to analyze the metadata in Python.
- **CSV Export:** As **Gregor**, I want to export the metadata and tags of my search results into a CSV to share a dataset with a colleague who uses Excel.
- **"My Collection":** As **Matthias**, I want to "star" interesting inscriptions to a personal list called "Seminar Week 4" so I have them ready for class.
- **Search History:** As **Gregor**, I want to access my recent search queries so I don't have to reconstruct complex Boolean filter chains every time I log in.
- **API Access:** As **Florian**, I want an API endpoint to fetch data by ID so I can test if the external integrations are working correctly.
- **Persistent URLs:** As **Herbert**, I want each inscription view to have a stable URL so I can link to it in a footnote and know it will still work in 10 years.
## Validation & Trust (The "Scientific" Layer)
- **Flag Error:** As **Herbert**, I want a button to "Report Incorrect Tag" so I can use my expertise to correct the AI's mistakes.
- **Model Version Display:** As **Florian**, I want to see which version of the LLM/Prompt (e.g., "v1.2") generated the tags to ensure reproducibility of the experiment.
- **Ambiguity Note:** As **Herbert**, I want the system to display "Ambiguous" if the AI provided two conflicting potential categories, rather than forcing a false certainty.
- **Source Link:** As **Herbert**, I want a direct link back to the original PHI database entry to verify the raw data against the source of truth.
## Entities & Linked Open Data (The "Context" Layer)
- **Pleiades Linking:** As **Gregor**, I want place names to link to their Pleiades ID so I can map them accurately in my GIS software.
- **LGPN Connection:** As **Gregor**, I want personal names to suggest potential matches in the _Lexicon of Greek Personal Names_ to aid my prosopographical research.
- **Institution Filtering:** As **Matthias**, I want to filter by specific institutions (e.g., "The Boule") to show my students how different city-states organized their councils.
- **Deity Index:** As **Gregor**, I want a browseable index of all deities mentioned across the corpus to quantify the popularity of specific cults.
## UX & Accessibility (The "Usability" Layer)
- **Dark Mode:** As **Florian**, I want a dark mode because I often debug the application late at night and want to reduce eye strain. Also dark mode is "Der Shit" and therfore non negotionable.
- **Responsive Mobile View:** As **Stephan-Felix**, I want to look up an inscription on my phone while I'm at the library stacks without the layout breaking.
- **Font Size Control:** As **Herbert**, I want to increase the font size of the Greek text independently of the UI, as I find small digital fonts hard to read.
- **Onboarding/Tour:** As **Stephan-Felix**, I want a guided tutorial explaining what the hierarchical tags mean so I don't feel lost when I first open the tool.
- **Query Explanation:** As **Stephan-Felix**, I want my complex filter selection to be translated into a natural language sentence (e.g., "Showing all Religious texts...") to confirm I searched for the right thing.