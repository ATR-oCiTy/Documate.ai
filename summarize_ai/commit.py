from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from summarize_ai.prompts import COMMIT_SUMMARY_TEMPLATE


class Commit:
    def __init__(self, repo: str, sha: str, diff: str):
        self.repo = repo
        self.sha = sha
        self.diff = diff

    def summarize(self, llm: ChatOpenAI, max_chars=3000) -> str:
        truncated_diff = self.diff[:max_chars]
        prompt = COMMIT_SUMMARY_TEMPLATE.format(diff=truncated_diff)
        return llm([HumanMessage(content=prompt)]).content