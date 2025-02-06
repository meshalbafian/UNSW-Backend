from dataclasses import dataclass
from datetime import date
from typing import List, Any

@dataclass
class PubmedRequest:
    start_date: str
    end_date: str
    query: str


class Article:
    def __init__(self, pubmed_id, title, abstract, journal, date):
        self.pubmed_id = pubmed_id
        self.title = title
        self.abstract = abstract
        self.journal = journal
        self.date = date

    def to_dict(self):
        return {
            "pubmed_id": self.pubmed_id,
            "title": self.title,
            "abstract": self.abstract,
            "journal": self.journal,
            "date": self.date
        }


class FilterResult:
    def __init__(self, articles, count):
        """
        :param articles: a list of `Article` objects
        :param count: integer representing the number of articles
        """
        self.articles = articles
        self.count = count

    def to_dict(self):
        return {
            "articles": [article.to_dict() for article in self.articles],
            "count": self.count,
        }