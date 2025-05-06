from langchain.prompts import PromptTemplate


# ---------------------- Prompt Templates ----------------------
COMMIT_SUMMARY_TEMPLATE = PromptTemplate.from_template("""
Summarize the following Git commit diff for a technical audience:

{diff}

Explain what changed, which files or modules were affected, and the purpose of the change.
Keep track of toggles, api interfaces(differentiate between create/update/usage), repository name and other relevant information in a tabular format.
""")

CARD_SUMMARY_TEMPLATE = PromptTemplate.from_template("""
You are generating a changelog entry for a technical story card.

Card title: {card_title}
Description: {card_description}

Here are summaries of the code commits:

{commit_summaries}

Write a concise changelog entry retaining all important information that connects the business need with code changes.
Make sure that the response is well-formatted and wrapped, use bullet points, tables and subtitles.
Keep the summaries in the format,
<Repository_Name (Always use actual repository name and not a logical name>
<Business logic>
<Code Changelog>
<API Endpoints Created or Updated>
<Toggles Added or Modified>
Group changes by repository, DO NOT list changes per commit, only cumulative changes.
Ensure that the overall structure stays consistent and follows the given format.
""")

EPIC_SUMMARY_TEMPLATE = PromptTemplate.from_template("""
You are an engineering technical note generator.

Epic title: {epic_title}
Description: {epic_description}

Here are summaries of the individual cards:

{card_summaries}

Write a high-level changelog entry (5-7 sentences), followed by a tabular overview of toggles (toggle name, actual repository name, description) 
and all API endpoints created or modified (api endpoint, created/modified/used, actual repository name, description), 
followed by the detailed summaries of the individual cards.
Keep the detailed summaries per card in the format,

<CARD_ID> - <CARD_TITLE>
<Repository_Name>
<Business logic>
<Code Changelog in bullet points>

Group changes by repository, DO NOT list changes per commit, only cumulative changes.
Generate the output in an xhtml format.
Make sure that the html is well-formatted and wrapped, spaced, use bullet points, tables and subtitles.
Ensure that the overall structure strictly follows the given format.
""")