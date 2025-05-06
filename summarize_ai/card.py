from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from summarize_ai import Commit # Updated import
from summarize_ai.prompts import CARD_SUMMARY_TEMPLATE
from common import get_logger # Updated import

# Initialize logger
logger = get_logger(__name__)


class Card:
    def __init__(self, card_id: str, title: str, description: str, commits: List[Commit]):
        self.id = card_id
        self.title = title
        self.description = description
        self.commits = commits

    def summarize(self, llm: ChatOpenAI) -> str:
        commit_summaries = [commit.summarize(llm) for commit in self.commits]
        joined = "\n\n".join([
            f"- Repo: {c.repo}, SHA: {c.sha}\n{summary}"
            for c, summary in zip(self.commits, commit_summaries)
        ])
        prompt = CARD_SUMMARY_TEMPLATE.format(
            card_title=self.title,
            card_description=self.description,
            commit_summaries=joined
        )
        return llm([HumanMessage(content=prompt)]).content
