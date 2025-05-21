from typing import List

from langchain_core.messages import HumanMessage

from summarize_ai import Card # Updated import
from summarize_ai.prompts import EPIC_SUMMARY_TEMPLATE
from common import get_logger # Updated import

# Initialize logger
logger = get_logger(__name__)


class Epic:
    def __init__(self, epic_id: str, title: str, description: str, cards: List[Card]):
        logger.debug(f"Initializing Epic: {epic_id} - {title}")
        self.id = epic_id
        self.title = title
        self.description = description
        self.cards = cards
        logger.debug(f"Epic initialized with {len(cards)} cards")

    def summarize(self, llm) -> str:
        logger.info(f"Summarizing Epic: {self.id} - {self.title}")

        logger.debug(f"Generating summaries for {len(self.cards)} cards")
        card_summaries = []
        for i, card in enumerate(self.cards):
            logger.debug(f"Summarizing card {i+1}/{len(self.cards)}: {card.id}")
            card_summary = card.summarize(llm)
            card_summaries.append(card_summary)

        logger.debug("Joining card summaries")
        joined = "\n\n\n".join([
            f"### {card.id} - {card.title}\n{summary}"
            for card, summary in zip(self.cards, card_summaries)
        ])

        logger.debug("Creating prompt for epic summary")
        prompt = EPIC_SUMMARY_TEMPLATE.format(
            epic_title=self.title,
            epic_description=self.description,
            card_summaries=joined
        )

        logger.info("Generating epic summary with LLM")
        try:
            epic_summary = llm([HumanMessage(content=prompt)]).content
            logger.debug(f"Generated epic summary of length: {len(epic_summary)} characters")

            logger.info("Epic summarization completed successfully")
            return epic_summary
        except Exception as e:
            logger.error(f"Error generating epic summary: {e}")
            raise
