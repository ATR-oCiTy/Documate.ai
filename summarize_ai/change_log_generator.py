from langchain_community.chat_models import ChatOpenAI
from summarize_ai.epic import Epic

from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class ChangeLogGenerator:
    def __init__(self, llm: ChatOpenAI):
        logger.debug("Initializing ChangeLogGenerator")
        self.llm = llm
        logger.debug(f"ChangeLogGenerator initialized with LLM: {type(llm).__name__}")

    def generate(self, epic: Epic, output_path: str):
        logger.info(f"Generating changelog for epic: {epic.id} - {epic.title}")
        logger.debug(f"Epic contains {len(epic.cards)} cards")

        logger.info("Summarizing epic with LLM")
        summary = epic.summarize(self.llm)
        logger.debug(f"Generated summary of length: {len(summary)} characters")

        logger.info(f"Writing changelog to: {output_path}")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            logger.info(f"Changelog successfully saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving changelog to {output_path}: {e}")
            raise
