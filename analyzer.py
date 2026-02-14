"""
analyzer.py

Analyzes the translated article headers to find words
that appear more than twice across all of them.

Pretty straightforward - tokenize, lowercase, filter stop words,
count occurrences, show the repeated ones.
"""

import re
from collections import Counter


# common english words we want to ignore in our analysis
# (articles, prepositions, pronouns, etc)
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "as", "are", "was",
    "were", "be", "been", "has", "have", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall", "can",
    "this", "that", "these", "those", "not", "no", "nor", "so", "if",
    "than", "too", "very", "just", "about", "up", "out", "into", "over",
    "after", "before", "between", "under", "above", "such", "each",
    "which", "who", "whom", "what", "when", "where", "why", "how",
    "all", "both", "few", "more", "most", "other", "some", "any",
    "he", "she", "they", "we", "you", "i", "me", "him", "her", "us",
    "them", "my", "your", "his", "our", "their",
}


def find_repeated_words(headers):
    """
    Given a list of translated (English) headers, find words that
    appear more than 2 times across all of them combined.
    
    Returns a dict like {"word": count, ...}
    """
    # put all headers together
    all_text = " ".join(headers).lower()
    
    # remove punctuation, keep only letters and spaces
    clean_text = re.sub(r"[^a-zA-Z\s]", "", all_text)
    words = clean_text.split()

    # filter out stop words and single-character words
    meaningful_words = [w for w in words if w not in STOP_WORDS and len(w) > 1]

    # count em up
    counts = Counter(meaningful_words)

    # only keep words that appear more than twice
    repeated = {word: cnt for word, cnt in counts.items() if cnt > 2}
    
    return repeated


def print_repeated_words(repeated):
    """Print out the repeated word analysis in a nice format."""
    if repeated:
        print("\nRepeated words (appearing more than twice):")
        print("-" * 40)
        for word, count in sorted(repeated.items(), key=lambda x: x[1], reverse=True):
            print(f"   '{word}' - {count} occurrences")
    else:
        print("\nNo words appear more than twice across the headers.")
    
    return repeated
