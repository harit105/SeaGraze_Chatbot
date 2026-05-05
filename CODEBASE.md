# CODEBASE.md

## Overview
This repository contains a small Streamlit app that accepts a natural-language question, converts it into a MongoDB aggregation pipeline via a generative model (Google Gemini through LangChain), runs that pipeline against a MongoDB collection, and shows the results in the Streamlit UI.

Purpose: let users ask questions about recorded form submissions and receive aggregation queries/results without writing MongoDB queries by hand.

## Key files
- `main.py` — The Streamlit application and the core logic. Responsibilities:
  - Load environment variables and secrets (via `python-dotenv` and Streamlit secrets).
  - Initialize a LangChain LLM client using Google Gemini (`langchain_google_genai.ChatGoogleGenerativeAI`).
  - Build a `PromptTemplate` and `LLMChain` to ask the model to return MongoDB aggregation pipelines (JSON).
  - Connect to MongoDB using `pymongo` and run aggregation pipelines returned by the model.
  - Render results in the Streamlit UI.

- `requirements.txt` — Python dependencies needed to run the app.
- `.env` (not committed) — local environment variables (example in `.env.example`).
- `.env.example` — placeholders for required secrets:
  - `GOOGLE_API_KEY`
  - `MONGO_USERNAME`
  - `MONGO_PASSWORD`
- `.gitignore` — ignores `.env` and `__pycache__/`.
- `sample.txt` — sample examples included in the prompt template (read into `sample` and passed to the LLM as `sample`).
- `prompt.txt`, `qsn.txt` — present but currently unused by main runtime (may be authoring artifacts).
- `test.py` — placeholder/test script (may be empty in this repo).

## Data model / Schema
`main.py` includes a long schema description used by the prompt. That schema describes the structure of documents stored in the target MongoDB collection (fields, nested objects, arrays). The LLM is expected to output a JSON array representing a MongoDB aggregation pipeline that matches this schema.

## How it works (flow)
1. App start: `main.py` loads `.env` (via `python-dotenv`) and Streamlit secrets.
2. Service initialization: the app constructs a `ChatGoogleGenerativeAI` LLM instance using `GOOGLE_API_KEY` and a chosen Gemini model.
3. User interaction: the user types a natural-language question into the Streamlit text area and clicks Submit.
4. LLM prompt: the app builds a `PromptTemplate` (containing the schema and examples) and runs an `LLMChain` to ask the model for a MongoDB aggregation pipeline (JSON only).
5. Execution: the app parses the model response as JSON and feeds it to `collection.aggregate()`.
6. Output: results are written back to the Streamlit UI.

## Environment variables / secrets
- `GOOGLE_API_KEY` — Google API key for Gemini (also accepted from Streamlit secrets).
- `MONGO_USERNAME` — MongoDB username.
- `MONGO_PASSWORD` — MongoDB password.

Place secrets in a local `.env` file (copy `.env.example`) or use Streamlit secrets for deployment. `.env` is ignored by git.

## Dependencies
Install dependencies with:

```bash
pip install -r requirements.txt
```

Core libraries:
- `streamlit` — UI
- `pymongo` — MongoDB client
- `langchain` & `langchain-google-genai` — LLM integration with Gemini
- `python-dotenv` — load local `.env`

## Running locally
1. Copy secrets:

```bash
cp .env.example .env
# Edit .env with your real credentials
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run main.py
```

Open the URL printed by Streamlit in the browser.

## Security notes
- Do NOT commit `.env` or secrets to version control. Use `.env` locally and Streamlit secrets or a secret manager in production.
- The app executes aggregation pipelines returned by the LLM. Treat model outputs as untrusted; validate or sanitize them if you deploy to production.

## Suggestions / Next steps
- Add validation for the returned aggregation pipeline (ensure it's an array, allowed stages only, max pipeline length).
- Add unit tests for pipeline parsing and for safe execution behavior.
- Make the Gemini model name configurable through the UI or config file.
- Consider using a secrets manager (e.g., Azure Key Vault, AWS Secrets Manager, or GCP Secret Manager) for production deployments.

## Contact / Maintenance
- Author: repository owner
- To update the prompt, edit the prompt text in `main.py` or move it to a dedicated prompt file and load it dynamically.



