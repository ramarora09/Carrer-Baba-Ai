import json
import math
import os
import re
from collections import Counter
from functools import lru_cache


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge", "career_knowledge.json")


def retrieve_career_context(query="", profile=None, top_k=5):
    profile = profile or {}
    documents = _load_knowledge()
    if not documents:
        return []

    search_text = _search_text(query, profile)
    query_vector = _tfidf_vector(search_text, documents)
    ranked = []

    for document in documents:
        doc_text = _document_text(document)
        score = _cosine(query_vector, _tfidf_vector(doc_text, documents))
        score += _metadata_bonus(search_text, document)
        if score > 0:
            ranked.append(
                {
                    "id": document["id"],
                    "title": document["title"],
                    "category": document["category"],
                    "content": document["content"],
                    "score": round(score, 4),
                }
            )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def rag_status():
    documents = _load_knowledge()
    return {
        "enabled": True,
        "knowledge_chunks": len(documents),
        "retriever": "tfidf_vector_retrieval",
    }


def format_rag_context(contexts):
    if not contexts:
        return "No retrieved career knowledge was available."

    blocks = []
    for index, item in enumerate(contexts, start=1):
        blocks.append(
            f"[{index}] {item['title']} ({item['category']})\n"
            f"{item['content']}"
        )
    return "\n\n".join(blocks)


@lru_cache(maxsize=1)
def _load_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE):
        return []

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as knowledge_file:
        documents = json.load(knowledge_file)

    return [
        document
        for document in documents
        if document.get("id") and document.get("title") and document.get("content")
    ]


def _search_text(query, profile):
    fields = [
        query,
        profile.get("resume_text", ""),
        profile.get("interest", ""),
        profile.get("experience", ""),
        profile.get("goal", ""),
        profile.get("time_plan", ""),
        profile.get("target_role", ""),
        profile.get("skills", ""),
        profile.get("background", ""),
    ]
    return " ".join(str(field) for field in fields if field).lower()


def _document_text(document):
    fields = [
        document.get("title", ""),
        document.get("category", ""),
        " ".join(document.get("roles", [])),
        " ".join(document.get("skills", [])),
        document.get("content", ""),
    ]
    return " ".join(fields).lower()


def _tfidf_vector(text, documents):
    tokens = _tokens(text)
    counts = Counter(tokens)
    vector = {}
    total_documents = len(documents)

    for token, count in counts.items():
        containing = sum(
            1
            for document in documents
            if token in set(_tokens(_document_text(document)))
        )
        idf = math.log((1 + total_documents) / (1 + containing)) + 1
        vector[token] = count * idf

    return vector


def _tokens(text):
    return [
        token
        for token in re.findall(r"[a-z0-9+#.]+", text.lower())
        if len(token) > 2
    ]


def _cosine(left, right):
    common = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0
    return numerator / (left_norm * right_norm)


def _metadata_bonus(search_text, document):
    bonus = 0
    normalized = search_text.lower()

    for role in document.get("roles", []):
        if role.lower() != "all" and role.lower() in normalized:
            bonus += 0.15

    for skill in document.get("skills", []):
        if skill.lower() in normalized:
            bonus += 0.05

    if document.get("category", "").replace("_", " ") in normalized:
        bonus += 0.08

    return min(bonus, 0.35)
