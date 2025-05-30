import arxiv
import re

# Common English stop words
STOP_WORDS = set(
    [
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "can",
        "could",
        "may",
        "might",
        "must",
        "and",
        "but",
        "or",
        "nor",
        "for",
        "so",
        "yet",
        "in",
        "on",
        "at",
        "by",
        "from",
        "to",
        "with",
        "about",
        "above",
        "after",
        "again",
        "against",
        "all",
        "am",
        "as",
        "because",
        "before",
        "below",
        "between",
        "both",
        "during",
        "each",
        "few",
        "further",
        "here",
        "how",
        "i",
        "if",
        "into",
        "it",
        "its",
        "itself",
        "just",
        "me",
        "more",
        "most",
        "my",
        "myself",
        "no",
        "not",
        "now",
        "of",
        "off",
        "once",
        "only",
        "other",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "same",
        "she",
        "he",
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
        "then",
        "there",
        "these",
        "this",
        "those",
        "through",
        "too",
        "under",
        "until",
        "up",
        "very",
        "we",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
    ]
)


def _extract_arxiv_id(id_or_url: str) -> str | None:
    """
    Extracts arXiv ID from a string (ID or URL).
    Handles formats like: 1234.5678, 2303.10130v1, hep-th/0101001
    """
    # Regex to find arXiv ID patterns (e.g., 1234.5678, 2303.10130v1, hep-th/0101001)
    # Updated regex to be more robust for various ID formats including older ones
    match = re.search(r"(\d{4}\.\d{4,5}(v\d+)?|[a-zA-Z.-]+/\d{7}(v\d+)?)", id_or_url)
    if match:
        # Further check if it's part of a URL and extract the core ID
        core_id_match = re.search(
            r"([a-zA-Z.-]*\d{4}\.\d{4,5}(v\d)?|[a-zA-Z.-]+/\d{7}(v\d)?)", match.group(0)
        )
        if core_id_match:
            return core_id_match.group(0)
        return match.group(
            0
        )  # Fallback to the broader match if specific sub-match fails
    return None


def search_arxiv_papers(query: str) -> dict:
    """
    Searches arXiv for papers matching the query.

    Args:
        query: The search query string.

    Returns:
        A dictionary containing the search results or an error message.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=5,  # Limit to 5 results
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers_list = []
        for result in search.results():
            paper_details = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "published_date": result.published.strftime("%Y-%m-%d"),
                "summary": result.summary,
                "arxiv_id": result.entry_id.split("/")[
                    -1
                ],  # Extract ID like '2303.10130'
                "primary_category": result.primary_category,
                "pdf_link": result.pdf_url,
            }
            papers_list.append(paper_details)

        if not papers_list:
            return {
                "status": "success",
                "papers": [],
                "message": "No papers found matching your query.",
            }

        return {"status": "success", "papers": papers_list}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def summarize_arxiv_paper(arxiv_id_or_url: str) -> dict:
    """
    Fetches and summarizes a specific arXiv paper by its ID or URL.

    Args:
        arxiv_id_or_url: The arXiv ID (e.g., "2303.10130") or URL
                         (e.g., "https://arxiv.org/abs/2303.10130").

    Returns:
        A dictionary containing the paper's details or an error message.
    """
    try:
        arxiv_id = _extract_arxiv_id(arxiv_id_or_url)
        if not arxiv_id:
            return {"status": "error", "message": "Invalid arXiv ID or URL format."}

        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results(), None)

        if paper:
            paper_details = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published_date": paper.published.strftime("%Y-%m-%d"),
                "summary": paper.summary,  # This is the abstract
                "arxiv_id": paper.entry_id.split("/")[-1],
                "primary_category": paper.primary_category,
                "pdf_link": paper.pdf_url,
            }
            return {"status": "success", "paper": paper_details}
        else:
            return {"status": "error", "message": "Paper not found or invalid ID."}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def answer_paper_question(arxiv_id_or_url: str, question: str) -> dict:
    """
    Answers a question about an arXiv paper based on its abstract.

    Args:
        arxiv_id_or_url: The arXiv ID or URL of the paper.
        question: The question to answer.

    Returns:
        A dictionary with the answer or an error message.
    """
    try:
        arxiv_id = _extract_arxiv_id(arxiv_id_or_url)
        if not arxiv_id:
            return {"status": "error", "message": "Invalid arXiv ID or URL format."}

        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results(), None)

        if not paper:
            return {
                "status": "error",
                "message": f"Paper with ID '{arxiv_id}' not found.",
            }

        abstract = paper.summary
        title = paper.title

        # Tokenize question and remove stop words
        question_words = [
            word
            for word in re.split(r"\W+", question.lower())
            if word and word not in STOP_WORDS
        ]

        if not question_words:
            return {
                "status": "success",
                "answer_type": "not_enough_keywords",
                "message": "Your question did not contain enough significant keywords after removing common words. Please try a more specific question.",
                "abstract": abstract,
                "title": title,
            }

        # Basic keyword matching in abstract
        found_keywords = 0
        abstract_lower = abstract.lower()
        for word in question_words:
            if word in abstract_lower:
                found_keywords += 1

        # Consider it a match if more than half of the significant keywords are found
        # This threshold can be adjusted.
        if found_keywords > len(question_words) / 2:
            return {
                "status": "success",
                "answer_type": "found_in_abstract",
                "message": "The abstract may contain information relevant to your question. Please review it.",
                "abstract": abstract,
                "title": title,
            }
        else:
            return {
                "status": "success",
                "answer_type": "not_found_in_abstract",
                "message": "I could not find specific information for your question in the paper's abstract.",
                "abstract": abstract,
                "title": title,
            }

    except Exception as e:
        # Log the exception e for debugging in a real application
        return {"status": "error", "message": f"An error occurred: {str(e)}"}
