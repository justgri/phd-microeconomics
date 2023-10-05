import streamlit as st


def local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def external_css(file_url):
    st.markdown(
        f'<link href="{file_url}" rel="stylesheet">', unsafe_allow_html=True
    )


def micro_page_config():
    st.set_page_config(
        page_title="PhD Microeconomics",
        page_icon="🍎",
        layout="wide",
    )


def wide_col():
    return st.columns((0.01, 1, 0.01))


def narrow_col():
    return st.columns((0.35, 1, 0.35))


# This is narrow_col_intro - not sure why Streamlit doesn't find it
def narrow_col_intro():
    return st.columns((0.1, 1, 0.1))


def two_cols():
    return st.columns((0.1, 1, 0.2, 1, 0.1))
