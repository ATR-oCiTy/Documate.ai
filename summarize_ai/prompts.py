from langchain.prompts import PromptTemplate


# ---------------------- Prompt Templates ----------------------
COMMIT_SUMMARY_TEMPLATE = PromptTemplate.from_template("""
Summarize the following Git commit diff for a technical audience:

{diff}

Explain what changed, which files or modules were affected, and the purpose of the change.
Keep track of toggles, api interfaces(differentiate between api call and definition), repository name and other relevant information.
""")

CARD_SUMMARY_TEMPLATE = PromptTemplate.from_template("""
You are generating a changelog entry for a technical story card.

Card title: {card_title}
Description: {card_description}

Here are summaries of the code commits:

{commit_summaries}

Write a concise changelog entry retaining all important information that connects the business need with code changes.
Keep the summaries in the format,
<Repository>
<Changelog>
Keep toggles, api references etc as a seperate section.
""")

EPIC_SUMMARY_TEMPLATE = PromptTemplate.from_template("""
You are an engineering technical note generator.

Epic title: {epic_title}
Description: {epic_description}

Here are summaries of the individual cards:

{card_summaries}

Write a high-level changelog entry (4-5 sentences) followed by the detailed summaries of the individual cards.
Keep the detailed summaries in the format,
<CARD_ID> - <CARD_TITLE>
<Repository>
<Changelog>
Keep toggles, api references etc as a seperate section.
Make sure that the markdown is well-formatted and wrapped, use bullet points, subtitles etc..
Focus on business value and system changes.
""")