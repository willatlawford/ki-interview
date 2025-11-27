VISUALLY_ANALYSE_PAGE_PROMPT = """Analyze this page image.
Quote any prose text directly and in full (e.g. text from titles, paragraphs, columns). 
Do not try to quote prose from inside more complicated visual layouts (like tables, graphs, charts, diagrams, maps, images, or other visual content).
For these visual elements, provide a title and description for each figure. Make the description detailed, but do not try to include all the data.
Be concise but thorough."""

DOCUMENT_SUMMARY_PROMPT = """
Based on the following content from a document, write ~10 bullet points that summarize the content and key information contained within the document.

Content:
{document_content}

Please provide ~10 bullet points, each starting with "- " and being concise but informative:
"""
