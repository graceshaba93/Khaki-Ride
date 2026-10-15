"""Global CSS. Kept small and restrained on purpose."""
import streamlit as st

_CSS = """
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
h1 { font-size: 1.6rem !important; font-weight: 650 !important; letter-spacing: -0.01em; }
h2 { font-size: 1.15rem !important; font-weight: 600 !important; }
h3 { font-size: 1rem !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { border-right: 1px solid #DAD7CE; }
.stButton > button, .stFormSubmitButton > button { border-radius: 4px; font-weight: 600; }

.page-title-row { display: flex; justify-content: space-between; align-items: flex-start;
                  gap: 1rem; flex-wrap: wrap; border-bottom: 1px solid #DAD7CE;
                  padding-bottom: 0.75rem; margin-bottom: 1.25rem; }
.page-title-row h1 { margin: 0; padding: 0; }
.page-sub { color: #5E656A; font-size: 0.9rem; margin-top: 0.2rem; }
.page-meta { text-align: right; font-size: 0.85rem; color: #5E656A; }
.demo-badge { display: inline-block; border: 1px solid #B7791F; color: #8A5A10;
              background: #FBF3E0; font-size: 0.7rem; font-weight: 700;
              letter-spacing: 0.06em; padding: 2px 8px; border-radius: 3px; }
.brand { font-size: 1.35rem; font-weight: 700; color: #1F4D3A; letter-spacing: -0.01em; }
.brand-sub { color: #5E656A; font-size: 0.85rem; margin-bottom: 1.25rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
