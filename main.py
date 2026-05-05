import streamlit as st
from pymongo import MongoClient
import io, json, os, re, base64
from pathlib import Path
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
LOGO_PATH = Path("/Users/haritshah/Documents/GitHub/LLMChat/Symbrosia Logo Black Vertical.png")

def get_base64_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="Seagraze Brain | Symbrosia",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, .block-container {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
header[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    border-bottom: 1px solid rgba(0,0,0,0.06) !important;
}
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
[data-testid="stBottom"],
[data-testid="stChatInput"],
.stChatFloatingInputContainer,
[data-testid="stBottomBlockContainer"] {
    background-color: #FFFFFF !important;
    border-top: 1px solid rgba(0,0,0,0.06) !important;
}
.stChatInput > div > div > textarea,
[data-testid="stChatInput"] textarea {
    border-radius: 20px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    padding: 12px 18px !important;
    font-size: 14px !important;
    background: #FAFAFA !important;
    color: #1A1A1A !important;
    box-shadow: none !important;
    transition: all 0.2s ease;
}
.stChatInput > div > div > textarea:focus {
    border-color: rgba(0,0,0,0.22) !important;
    background: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}
.stChatInput > div > div > textarea::placeholder { color: #AAAAAA !important; }
[data-baseweb="select"] > div,
[data-baseweb="select"] input,
[data-baseweb="multi-select"] > div {
    background-color: #FFFFFF !important;
    border-color: rgba(0,0,0,0.12) !important;
    color: #1A1A1A !important;
    border-radius: 10px !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.10) !important;
    color: #1A1A1A !important;
}
[role="option"], li[role="option"] {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
    font-size: 13px !important;
}
[role="option"]:hover, li[role="option"]:hover { background-color: #F5F5F7 !important; }
[data-baseweb="tag"] {
    background-color: #F0F0F2 !important;
    color: #1A1A1A !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: #1A1A1A !important; }
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: #FAFAFA !important;
    border-right: 1px solid rgba(0,0,0,0.06) !important;
}
[data-testid="stSidebar"] * { color: #1A1A1A !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #767676 !important; font-size: 13px !important; }
[data-testid="stSidebar"] h3 {
    font-size: 13px !important; font-weight: 600 !important;
    color: #1A1A1A !important; text-transform: uppercase !important;
    letter-spacing: 0.3px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    color: #1A1A1A !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #F5F5F7 !important;
    border-color: rgba(0,0,0,0.18) !important;
}
.sidebar-logo-container {
    display: flex; align-items: center; gap: 10px;
    padding: 0.75rem 0 0.5rem 0;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    margin-bottom: 0.75rem;
}
.sidebar-logo-container img { height: 36px; object-fit: contain; }
.sidebar-brand-name {
    font-size: 15px; font-weight: 600;
    color: #1A1A1A !important; letter-spacing: -0.3px;
}
.sidebar-brand-sub { font-size: 11px; color: #999 !important; margin-top: -2px; }
[data-testid="stChatMessage"] { background: transparent !important; padding: 0.5rem 0 !important; }
[data-testid="stChatMessageContent"],
[data-testid="stMarkdownContainer"] {
    font-size: 15px !important; line-height: 1.65 !important; color: #1A1A1A !important;
}
[data-testid="stExpander"],
[data-testid="stExpanderDetails"] {
    background: #FAFAFA !important;
    border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 10px !important;
}
.streamlit-expanderHeader {
    font-size: 12px !important; font-weight: 500 !important;
    color: #999 !important; background: transparent !important;
}
.stButton > button {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    color: #1A1A1A !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    padding: 0.65rem 1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #F5F5F7 !important;
    border-color: rgba(0,0,0,0.15) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
}
.main-header-container {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 3rem 0 1.5rem 0; gap: 0.75rem;
}
.main-logo     { height: 72px; opacity: 0.92; }
.main-title    { font-size: 26px; font-weight: 400; color: #1A1A1A; letter-spacing: -0.5px; margin: 0; }
.main-subtitle { font-size: 14px; color: #999; margin-top: -0.25rem; }
.chip-section-label {
    font-size: 12px; font-weight: 500; color: #AAAAAA;
    text-transform: uppercase; letter-spacing: 0.6px;
    text-align: center; margin: 2rem 0 0.75rem 0;
}
.status-dot {
    display: inline-block; width: 7px; height: 7px;
    background: #34C759; border-radius: 50%;
    margin-right: 5px; vertical-align: middle;
}
.status-label { font-size: 12px; color: #767676; vertical-align: middle; }
.block-container {
    max-width: 780px !important;
    margin: 0 auto !important;
    padding-top: 1.5rem !important;
    padding-bottom: 5rem !important;
}
html { scroll-behavior: smooth; }
</style>
""", unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
google_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
if not google_api_key:
    st.error("Missing GOOGLE_API_KEY.")
    st.stop()

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    google_api_key=google_api_key,
)

# ── MongoDB ───────────────────────────────────────────────────────────────────
mongo_uri = os.getenv("MONGO_URI") or st.secrets.get("MONGO_URI", "")
if not mongo_uri:
    st.error("Missing MONGO_URI.")
    st.stop()
if isinstance(mongo_uri, str) and mongo_uri.startswith('"'):
    mongo_uri = mongo_uri.strip('"')

client = MongoClient(mongo_uri)
db     = client["v6"]

# ── Collections ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_available_collections() -> list[str]:
    return sorted(db.list_collection_names())

# ── Field Schemas ─────────────────────────────────────────────────────────────
FIELD_SCHEMAS = {

    "OC-WI-14.01 Culture Transfer": """
## VERIFIED FIELD SCHEMA — Culture Transfer (OC-WI-14.01)
CRITICAL FACTS ABOUT THIS COLLECTION:
1. NO form_name field — NEVER filter on form_name.
2. NO CalcDate field — NEVER filter or sort on CalcDate.
3. ALL numeric-looking fields are stored as STRINGS (e.g. Biomassg="4200", NewVesselSize="1350").
4. Use _id: -1 for all recency sorting — ObjectId encodes insertion time.
5. For any numeric sort/compare, ALWAYS use $toDouble to convert the string first.
6. NEVER mix inclusion and exclusion in $project. Use $unset to remove helper fields before $project.

| Raw MongoDB Field Name  | Type            | Notes                                                                  |
|-------------------------|-----------------|------------------------------------------------------------------------|
| _id                     | ObjectId        | Always present — sort _id: -1 for most recent records                 |
| BatchNum                | String          | Destination batch ID, format YYMMDD-LocationCode-Strain                |
| SourceBatchNum          | String          | Source batch ID                                                        |
| DateInoculation         | String          | Transfer date as MM/DD/YYYY — do NOT sort by this                      |
| Name                    | String          | Technician name                                                        |
| Strain                  | String          | Seaweed strain code e.g. "05", "11"                                    |
| Organic                 | String          | "Organic" or "NotOrganic" — String, NOT boolean                        |
| TransferTable           | String          | Transfer type e.g. "Transfer1", "Transfer2", "Transfer3"               |
| NewLocationCode         | String          | Destination vessel location code e.g. "A01", "X03"                    |
| NewVesselSize           | String          | Destination vessel size as string e.g. "1350", "250", "12000"          |
| SourceLocationCode      | String          | Source vessel location code e.g. "C05"                                 |
| SourceVesselSize        | String          | Source vessel size as string e.g. "220", "1350"                        |
| SourceInoculation       | String          | Source inoculation date YYMMDD e.g. "251014"                           |
| Biomassg                | String (number) | Biomass grams stored as string e.g. "4200" — use $toDouble to sort     |
| NNutrientConcentration  | String          | Nitrogen formula code — often null                                     |
| PNutrientConcentration  | String          | Phosphorus formula code — often null                                   |
| BatchNumMediaN          | String          | Nitrogen media batch — often null                                      |
| BatchNumMediaP          | String          | Phosphorus media batch — often null                                    |
| BatchNumMediaMetals     | String          | Trace metals media batch — often null                                  |
| lastUpdateDate          | String          | ISO timestamp e.g. "2025-11-20T15:55:58.911-05:00"                    |
| originalDocId           | String          | Internal GoFormz document UUID                                         |
| BatchTrackingAdded      | Boolean         | true if added to batch tracking                                        |
| Comments                | String          | Free text notes — often null                                           |
""",

    "OC-WI-11.01 Outdoor Harvest": """
## VERIFIED FIELD SCHEMA — Outdoor Harvest (OC-WI-11.01)
CRITICAL: No form_name, no CalcDate. All numeric fields stored as Strings.
Use _id: -1 for recency. Use $toDouble before any numeric sort.
NEVER mix inclusion and exclusion in $project — use $unset to remove helper fields first.

| Raw MongoDB Field Name  | Type            | Notes                                                   |
|-------------------------|-----------------|---------------------------------------------------------|
| _id                     | ObjectId        | Sort _id: -1 for most recent                            |
| BatchNum                | String          | Batch ID, format YYMMDD-LocationCode-Strain             |
| SourceBatchNum          | String          | Source batch ID                                         |
| DateHarvest             | String          | Harvest date MM/DD/YYYY — do NOT sort                   |
| Name                    | String          | Technician name                                         |
| Strain                  | String          | Strain code e.g. "05"                                   |
| WetWeightg              | String (number) | Wet weight grams as string — use $toDouble to sort      |
| DryWeightg              | String (number) | Dry weight grams as string — use $toDouble to sort      |
| WetWeightgL             | String (number) | Wet weight g/L as string                                |
| DryWeightgL             | String (number) | Dry weight g/L as string                                |
| HarvestVolML            | String (number) | Volume harvested mL as string                           |
| Organic                 | String          | "Organic" or "NotOrganic"                               |
| lastUpdateDate          | String          | ISO timestamp                                           |
| Comments                | String          | Often null                                              |
""",
}

DEFAULT_SCHEMA = """
## FIELD SCHEMA — Not yet defined for this collection
CRITICAL ASSUMPTIONS for all collections in this database:
- No form_name field — do NOT filter on it.
- No CalcDate field — do NOT sort on it.
- Numeric fields may be stored as Strings — always use $toDouble before numeric sort/compare.
- Use _id: -1 for all recency sorting.
- NEVER mix inclusion and exclusion in $project — use $unset to remove helper fields first.
- Common fields: BatchNum, Name, Strain, DateInoculation, lastUpdateDate, Comments
- Use $limit 3 with no filter to discover available fields first.
"""

def get_schema(col: str) -> str:
    return FIELD_SCHEMAS.get(col, DEFAULT_SCHEMA)

# ── Date Context ──────────────────────────────────────────────────────────────
def get_date_context() -> str:
    today        = datetime.utcnow()
    three_months = today - timedelta(days=90)
    return (
        "## TODAY'S DATE CONTEXT\n"
        f"- Today: {today.strftime('%B %d, %Y')}\n"
        f"- 3 months ago: {three_months.strftime('%B %d, %Y')}\n"
        "- For lastUpdateDate range filtering: use ISO string $gte/$lte lexicographically.\n"
        f"- For SourceInoculation range (YYMMDD): gte={three_months.strftime('%y%m%d')}, lte={today.strftime('%y%m%d')}\n"
        "- NEVER sort by DateInoculation or DateHarvest — MM/DD/YYYY strings sort incorrectly.\n"
        "- ALWAYS use _id: -1 for recency sorting.\n"
    )

# ── Sample Queries — auto-escape braces for PromptTemplate ───────────────────
with io.open("sample.txt", "r", encoding="utf-8") as f:
    _raw_sample = f.read()

sample = re.sub(r'(?<!\{)\{(?!\{)', '{{', _raw_sample)
sample = re.sub(r'(?<!\})\}(?!\})', '}}', sample)

# ── Prompt Template ───────────────────────────────────────────────────────────
prompt_template = """
You are a very intelligent AI assistant expert in converting natural language questions
into MongoDB aggregation pipeline queries.

{field_schema}

{date_context}

## CRITICAL RULES
- Return ONLY a valid JSON array for the aggregation pipeline.
- No explanation, no markdown, no backticks, no extra text — just the raw JSON array.
- Always use the EXACT Raw MongoDB Field Name from the schema above.
- NEVER filter on form_name — it does not exist in these collections.
- NEVER filter or sort on CalcDate — it does not exist in these collections.
- ALL numeric-looking fields are stored as STRINGS (Biomassg, WetWeightg, NewVesselSize, etc.)
  ALWAYS use $toDouble to convert before any numeric sort or numeric comparison.

- $project RULE — CRITICAL: MongoDB forbids mixing inclusion (field:1) and exclusion (field:0)
  in the same $project stage (except _id:0 which is always allowed).
  ALWAYS remove helper fields like _sortVal using a $unset stage BEFORE the $project stage.
  CORRECT order: $addFields → $sort → $limit → $unset "_sortVal" → $project (inclusion only)
  WRONG: {{"$project": {{"BatchNum": 1, "_sortVal": 0}}}}  ← NEVER DO THIS

- For ALL "last N", "most recent N", "latest N" queries:
    1. {{"$sort": {{"_id": -1}}}}
    2. {{"$limit": N}}
    3. {{"$project": {{"BatchNum": 1, "DateInoculation": 1, "Name": 1, "Strain": 1, "NewLocationCode": 1, "NewVesselSize": 1}}}}

- For "highest N biomass" / "top N biomass weights" (Biomassg):
    1. {{"$match": {{"Biomassg": {{"$ne": null, "$gt": "0"}}}}}}
    2. {{"$addFields": {{"_sortVal": {{"$toDouble": "$Biomassg"}}}}}}
    3. {{"$sort": {{"_sortVal": -1}}}}
    4. {{"$limit": N}}
    5. {{"$unset": "_sortVal"}}
    6. {{"$project": {{"BatchNum": 1, "Biomassg": 1, "DateInoculation": 1, "Name": 1, "Strain": 1, "NewVesselSize": 1, "NewLocationCode": 1}}}}

- For "highest N wet/dry weights" (WetWeightg / DryWeightg):
    1. {{"$match": {{"WetWeightg": {{"$ne": null, "$gt": "0"}}}}}}
    2. {{"$addFields": {{"_sortVal": {{"$toDouble": "$WetWeightg"}}}}}}
    3. {{"$sort": {{"_sortVal": -1}}}}
    4. {{"$limit": N}}
    5. {{"$unset": "_sortVal"}}
    6. {{"$project": {{"BatchNum": 1, "WetWeightg": 1, "DateHarvest": 1, "Name": 1, "Strain": 1}}}}

- For vessel size filter: NewVesselSize is a String — match as {{"NewVesselSize": "1350"}}.
- For Organic filter: match as {{"Organic": "Organic"}} — String, not boolean.
- For nullable fields: add {{"$ne": null}} in $match before using them.
- BatchNum partial match: {{"BatchNum": {{"$regex": "251026", "$options": "i"}}}}.
- Always include BatchNum in $project output.

## SAMPLE QUESTIONS AND QUERIES
{sample}

REMINDER: Return ONLY a valid JSON array. No markdown, no explanation.
input: {question}
output:
"""

nl_prompt_template = """
You are a helpful AI assistant answering questions about algae culture data.
Answer accurately and concisely in natural language.
Do not mention JSON, MongoDB, or database internals.
Round numeric values to 2 decimal places.
If you see MM/DD/YYYY dates, display them as-is (e.g. 10/26/2025).
If you see ISO timestamps, show only the date part.
Always include the BatchNum when presenting results.

User Question: {question}
Database Results: {json_data}
Answer:
"""

prompt    = PromptTemplate(template=prompt_template,    input_variables=["question", "sample", "field_schema", "date_context"])
nl_prompt = PromptTemplate(template=nl_prompt_template, input_variables=["question", "json_data"])
chain     = prompt    | llm | StrOutputParser()
nl_chain  = nl_prompt | llm | StrOutputParser()

# ── Session State ─────────────────────────────────────────────────────────────
if "messages"             not in st.session_state: st.session_state.messages             = []
if "show_suggestions"     not in st.session_state: st.session_state.show_suggestions     = True
if "selected_collections" not in st.session_state: st.session_state.selected_collections = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    if LOGO_PATH.exists():
        logo_b64 = get_base64_image(str(LOGO_PATH))
        st.markdown(f"""
        <div class="sidebar-logo-container">
            <img src="data:image/png;base64,{logo_b64}" alt="Symbrosia">
            <div>
                <div class="sidebar-brand-name">Seagraze Brain</div>
                <div class="sidebar-brand-sub">by Symbrosia</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-logo-container">
            <span style="font-size:22px">🌿</span>
            <div>
                <div class="sidebar-brand-name">Seagraze Brain</div>
                <div class="sidebar-brand-sub">by Symbrosia</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Settings")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages         = []
        st.session_state.show_suggestions = True
        st.rerun()

    st.markdown("### Collections")
    if st.button("↻  Refresh List", use_container_width=True):
        load_available_collections.clear()
        st.rerun()

    try:
        available_collections = load_available_collections()
    except Exception as e:
        st.warning(f"Could not load collections: {e}")
        available_collections = ["OC-WI-14.01 Culture Transfer"]

    selected_collections = st.multiselect(
        "Select collections to search",
        options=available_collections,
        default=st.session_state.selected_collections,
        placeholder="Choose one or more…",
        help="The chatbot will query the selected collections.",
    )
    st.session_state.selected_collections = selected_collections

    st.markdown("---")
    n = len(selected_collections)
    st.markdown(f"""
    <span class="status-dot"></span>
    <span class="status-label">Connected · v6</span><br>
    <span class="status-label" style="margin-left:12px">
        {n} collection{'s' if n != 1 else ''} selected
    </span>""", unsafe_allow_html=True)

    if selected_collections:
        st.markdown("### Schema")
        for col in selected_collections[:3]:
            with st.expander(f"📋 {col}", expanded=False):
                st.markdown(get_schema(col))

# ── Welcome Screen ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    if LOGO_PATH.exists():
        logo_b64 = get_base64_image(str(LOGO_PATH))
        st.markdown(f"""
        <div class="main-header-container">
            <img src="data:image/png;base64,{logo_b64}" class="main-logo" alt="Symbrosia">
            <div class="main-title">Seagraze Brain</div>
            <div class="main-subtitle">Ask anything about your algae culture data</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-header-container">
            <div style="font-size:48px">🌿</div>
            <div class="main-title">Seagraze Brain</div>
            <div class="main-subtitle">Ask anything about your algae culture data</div>
        </div>""", unsafe_allow_html=True)

    SUGGESTIONS = {
        "OC-WI-14.01 Culture Transfer": [
            "📋  Last 5 batch entries",
            "⚖️  Top 5 highest biomass weights",
            "🌿  Show all organic transfers",
            "🔬  Transfers for strain 05",
        ],
        "OC-WI-11.01 Outdoor Harvest": [
            "📋  Last 5 harvest batches",
            "⚖️  Top 5 highest wet weights",
            "🌿  Show organic harvests only",
            "📅  Most recent 3 harvests",
        ],
    }
    default_suggestions = [
        "📋  Show me the last 5 records",
        "🔍  Show me 3 sample records",
        "📊  Count total records",
        "🌿  Most recent 10 entries",
    ]

    chips = default_suggestions
    for col in selected_collections:
        chips = SUGGESTIONS.get(col, default_suggestions)
        break

    st.markdown('<div class="chip-section-label">Try asking</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for i, chip in enumerate(chips):
        with (col1 if i % 2 == 0 else col2):
            clean_chip = re.sub(r"^[^\w]+\s+", "", chip).strip()
            if st.button(chip, key=f"chip_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": clean_chip})
                st.session_state.show_suggestions = False
                st.rerun()

# ── Chat History ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🌿" if msg["role"] == "assistant" else None):
        content = msg["content"]
        if isinstance(content, dict):
            st.markdown(content.get("answer", ""))
            if content.get("query"):
                with st.expander("View query", expanded=False):
                    st.code(json.dumps(content["query"], indent=2), language="json")
            if content.get("raw"):
                with st.expander("View raw results", expanded=False):
                    st.json(content["raw"])
        else:
            st.markdown(content)

# ── Process pending user message ─────────────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_input = st.session_state.messages[-1]["content"]

    if not selected_collections:
        with st.chat_message("assistant", avatar="🌿"):
            st.markdown("Please select at least one collection from the sidebar to get started.")
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Please select at least one collection from the sidebar to get started."
        })
    else:
        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner(""):
                try:
                    active_col    = selected_collections[0]
                    active_schema = get_schema(active_col)
                    collection    = db[active_col]

                    raw_response = chain.invoke({
                        "question":     user_input,
                        "sample":       sample,
                        "field_schema": active_schema,
                        "date_context": get_date_context(),
                    })

                    clean = raw_response.strip()
                    if clean.startswith("```"):
                        clean = re.sub(r"^```[a-z]*\n?", "", clean)
                        clean = re.sub(r"\n?```$",        "", clean)
                        clean = clean.strip()

                    query   = json.loads(clean)
                    results = list(collection.aggregate(query))

                    if results:
                        nl_response = nl_chain.invoke({
                            "question":  user_input,
                            "json_data": json.dumps(results, default=str),
                        })
                        st.markdown(nl_response)
                        with st.expander("View query", expanded=False):
                            st.code(json.dumps(query, indent=2), language="json")
                        with st.expander("View raw results", expanded=False):
                            st.json(results)
                        answer = {"answer": nl_response, "query": query, "raw": results}
                    else:
                        msg = "No results found. Try rephrasing or check if the collection has matching data."
                        st.markdown(msg)
                        answer = {"answer": msg, "query": query, "raw": []}

                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except json.JSONDecodeError as e:
                    err = f"⚠️ Could not parse the generated query: {e}"
                    st.markdown(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})
                except Exception as e:
                    err = f"⚠️ An error occurred: {e}"
                    st.markdown(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})

    st.rerun()

# ── Chat Input ────────────────────────────────────────────────────────────────
placeholder = (
    f"Ask about {selected_collections}…"
    if selected_collections else
    "Select a collection first, then ask a question…"
)
if user_input := st.chat_input(placeholder):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.show_suggestions = False
    st.rerun()