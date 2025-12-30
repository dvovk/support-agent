# ageant is responsible in help of creating AI support tool
This support tool is aim to help answer questions in Erigon Discord server. Usually people ask questions about setting up an Erigon node or they have some issues and they share some logs and ask for help.
The main idea is to gather all knowladge from discord as well as access to code and documentation, in theory it could help to answer for most of the users questions.

## Conversation Summary (2025-12-29)

- **Objective:** Improve the support AI's ability to answer questions by using the knowledge from Discord.
- **Problem:** The AI was not providing correct answers to questions, even when the answer was present in the Discord history.
- **Actions Taken:**
    1.  **Increased Document Retrieval:** The number of documents retrieved from the Discord vector store was increased from 2 to 6 to improve the chances of finding the relevant information.
    2.  **Prompt Engineering:** The prompt used to generate the answer was significantly improved to guide the LLM to act as a senior support engineer and provide a clear, actionable answer.
    3.  **Environment Fix:** A `requirements.txt` file was created to ensure a repeatable and stable development environment, which resolved a `Segmentation fault` issue.
    4.  **Logging:** A feature to log all queries and answers to a file was implemented.
    5.  **Git Commit:** The progress was saved to a local git commit.
- **Current Status:** The support AI is now able to answer the user's question correctly by using the information from the Discord history. The project is in a stable state with a repeatable environment.