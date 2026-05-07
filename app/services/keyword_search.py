from flashtext import KeywordProcessor


def search_keywords(text: str, keywords: list[str], case_sensitive: bool = False) -> dict:
    processor = KeywordProcessor(case_sensitive=case_sensitive)
    processor.add_keywords_from_list(keywords)

    found_set = set(processor.extract_keywords(text))
    not_found_set = set(keywords) - found_set

    return {
        "found": sorted(found_set),
        "not_found": sorted(not_found_set),
        "match_count": len(found_set),
        "keyword_count": len(keywords),
    }
