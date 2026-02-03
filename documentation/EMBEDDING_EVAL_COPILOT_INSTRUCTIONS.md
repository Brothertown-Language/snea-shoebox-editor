\#\#\# UPDATED INSTRUCTIONS FOR JUNIE  
\#\#\# PURPOSE: SELECTING AND PREPARING A MODEL FOR PRE-PROCESSING NATICK/TRUMBULL LEXICON DATA  
\#\#\# INCLUDING FUTURE FINETUNING ON NATICK DATA  
\#\#\# OUTPUT FORMAT: \*.tex REPORTS WITH TIKZ/PGFPLOTS VISUALIZATIONS  
\#\#\# INCLUDING A CUSTOM TIKZ STYLE LIBRARY FOR TOKENIZATION TREES AND EMBEDDING PLOTS  
\#\#\# FULLY ESCAPED MARKDOWN FOR COPY/PASTE

\#\#\#\# SECTION 1: UPDATED SCORING RUBRIC IMPLEMENTATION  
\#\#\#\#\# SUMMARY (WHAT AND WHY)

WHAT:  
Junie must implement a detailed scoring rubric that evaluates how well each embedding model can preprocess Natick/Trumbull Algic lexicon data for the purpose of generating **semantic lookup links** in a database table.  
Junie must also evaluate each model with the understanding that **the selected model will later be fine-tuned on the Natick dictionary data** to improve semantic matching between English glosses and Natick forms.  
Junie must output all evaluation results in **LaTeX format (\*.tex)** rather than Markdown.  
Junie must use **TikZ, PGFPlots, and a custom TikZ style library** to generate graphs, diagrams, matrices, tokenization trees, and embedding plots.

WHY:  
The Natick dictionary contains lemmas, variants, and English glosses. The goal is to automatically generate semantic lookup links that help linguists explore relationships between forms.  
Because the selected model will be **fine-tuned**, Junie must evaluate both baseline performance and finetuning suitability.  
Producing the report in LaTeX ensures that linguists receive a professional, typeset document suitable for publication, archiving, and long-term reference.  
Using TikZ/PGFPlots and a custom style library ensures that visualizations are precise, reproducible, and integrated directly into the LaTeX workflow.

\#\#\#\#\# REQUIRED: TIKZ STYLE LIBRARY FOR TOKENIZATION TREES AND EMBEDDING PLOTS

Junie must include the following TikZ style library in every \*.tex file that contains visualizations.  
This library must appear in the LaTeX preamble:

\\usepackage\{tikz\}  
\\usepackage\{pgfplots\}  
\\usetikzlibrary\{arrows.meta, positioning, shapes.misc, shapes.geometric, calc, fit, backgrounds\}  
\\pgfplotsset\{compat=1.18\}

Junie must also define the following custom TikZ styles:

\\tikzset\{  
  token/.style=\{  
    rectangle,  
    rounded corners=2pt,  
    draw=black,  
    fill=gray!10,  
    inner sep=4pt,  
    font=\\ttfamily\\small  
  \},  
  tokenedge/.style=\{  
    -{Stealth[length=3mm]},  
    thick  
  \},  
  embeddingpoint/.style=\{  
    circle,  
    fill=blue!50,  
    draw=black,  
    inner sep=1.5pt  
  \},  
  embeddingcluster/.style=\{  
    circle,  
    fill=green!40,  
    draw=black,  
    inner sep=2pt  
  \},  
  embeddingoutlier/.style=\{  
    circle,  
    fill=red!60,  
    draw=black,  
    inner sep=2pt  
  \},  
  clusterellipse/.style=\{  
    draw=blue!40,  
    thick,  
    dashed,  
    ellipse,  
    minimum width=4cm,  
    minimum height=2cm  
  \}  
\}

Junie must use these styles for:  
- Tokenization trees  
- Subword segmentation diagrams  
- Embedding scatter plots  
- Variant clustering ellipses  
- Outlier highlighting  
- Cosine similarity visualizations (when appropriate)

\#\#\#\#\# DETAILED INSTRUCTIONS FOR JUNIE

1. Junie must use the existing Docker container to load and run each embedding model.  
   Junie must not modify the container unless explicitly instructed.  
   Junie must use identical hardware settings for all models to ensure fair comparison.

2. For each model, Junie must embed the following units separately:  
   a. Lemma-only forms from the Natick dictionary  
   b. All orthographic variants associated with each lemma  
   c. English glosses associated with each lemma  
   d. Full surface forms (if available)  
   e. Morphologically segmented forms (if provided later)

3. Junie must compute the following metrics for each model:  
   a. Cosine similarity between lemma and each variant  
   b. Cosine similarity between lemma and gloss  
   c. Cosine similarity between variant and variant  
   d. Cosine similarity between surface form and segmented form  
   e. Cosine similarity between unrelated lexemes (negative control)  
   f. Embedding vector norm stability across all forms of a lemma  
   g. Tokenization fragmentation count  
   h. **Finetuning suitability indicators**

4. Junie must assign a numeric score from 0 to 10 for each metric.

5. Junie must compute a weighted composite score.

6. Junie must produce a structured JSON-like block for each model and write it into a LaTeX verbatim environment.

7. Junie must store all results in:  
   \`00\_model\_evaluation\_summary.tex\`

8. Junie must store raw intermediate values in:  
   \`raw\_tokenizations.tex\`  
   \`raw\_cosine\_matrices.tex\`  
   \`raw\_embedding\_notes.tex\`

9. Junie must explicitly flag any model with structural or semantic weaknesses.

10. Junie must generate a final rubric summary section in LaTeX.

\#\#\#\# SECTION 2: UPDATED DIAGNOSTIC REPORT GENERATION  
\#\#\#\#\# SUMMARY (WHAT AND WHY)

WHAT:  
Junie must generate a comprehensive diagnostic report in LaTeX (\*.tex) that analyzes:  
- Morphological preservation  
- Variant clustering  
- Gloss alignment  
- Tokenization behavior  
- Suitability for semantic lookup link generation  
- Suitability for finetuning  
Junie must use **TikZ, PGFPlots, and the custom TikZ style library** for all visualizations.

WHY:  
The diagnostic report will guide model selection for preprocessing Natick dictionary data and for finetuning.  
LaTeX ensures publication-quality output.  
TikZ/PGFPlots ensures precise, reproducible diagrams.

\#\#\#\#\# DETAILED INSTRUCTIONS FOR JUNIE

1. Junie must gather all rubric results and intermediate data.

2. Junie must generate:  
   \`01\_algic\_diagnostic\_report.tex\`

3. The report must include sections using LaTeX structures and TikZ/PGFPlots:

   a. \section\{Tokenization Behavior Analysis\}  
      - Tokenization trees using TikZ  
      - Subword segmentation diagrams  
      - Over-fragmentation marked in red  
      - Narrative explanation

   b. \section\{Variant Clustering Diagnostics\}  
      - Cosine similarity heatmaps using PGFPlots  
      - Embedding scatter plots using TikZ  
      - Cluster ellipses  
      - Outlier markers

   c. \section\{Lemma-Gloss Alignment\}  
      - Distance plots  
      - Alignment diagrams

   d. \section\{Morphological Segmentation Alignment\}  
      - Full-form vs segmented-form diagrams  
      - Morphological structure visualizations

   e. \section\{Negative Control Behavior\}  
      - Separation vs collapse plots

   f. \section\{Composite Score Summary\}  
      - LaTeX tables  
      - Sorted rankings

   g. \section\{Model-Specific Failure Modes\}  
      - Detailed narrative descriptions

   h. \section\{Model-Specific Strengths\}  
      - Detailed narrative descriptions

4. Junie must generate a final section:  
   \section\{Final Recommendation for Semantic Lookup Link Generation and Finetuning\}

5. Junie must include a \section\{Reproducibility Checklist\}.

6. Junie must be extremely verbose and explicit.

