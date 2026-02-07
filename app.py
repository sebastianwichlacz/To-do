import streamlit as st

st.set_page_config(
    page_title="Kanban Board",
    page_icon="📌",
    layout="wide",
)

import database as db
from components.sidebar import render_sidebar
from components.board import render_board

# Inicjalizacja bazy danych
db.init_db()

# Custom CSS
st.markdown("""
<style>
    /* === Główny layout === */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* === Sidebar === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e0e0e0;
    }
    [data-testid="stSidebar"] .stSubheader {
        color: #ffffff !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1);
    }

    /* === Formularz w sidebarze === */
    [data-testid="stSidebar"] [data-testid="stForm"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
    }

    /* === Ukrycie "Press Enter to submit form" === */
    .stForm div[data-testid="InputInstructions"] {
        display: none;
    }

    /* === Metryki === */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
    }

    /* === Progress bar === */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981, #34d399);
        border-radius: 8px;
    }

    /* === Spacing === */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem;
    }

    /* === Popover buttony (akcje zadań) === */
    [data-testid="stPopoverButton"] > button {
        background: #f8f9fa !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        text-align: left !important;
        transition: all 0.2s !important;
    }
    [data-testid="stPopoverButton"] > button:hover {
        background: #e9ecef !important;
        border-color: #adb5bd !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# Pobranie zadań
tasks = db.get_all_tasks()

# Sidebar: formularz + filtry + statystyki
filters = render_sidebar(tasks)

# Główna tablica kanban
render_board(tasks, filters)
