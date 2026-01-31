import streamlit as st
from data_loader import load_network_data
from dashboard_view import render_dashboard
from replay_view import render_replay

st.set_page_config(page_title="IoT Tank Sentinel", layout="wide")

def main():
    """
    App entry point.
    """
    # cache dataset in session (so I don't always have to reload all the ~500 files)
    if "df" not in st.session_state:
        with st.spinner("Loading network logs..."):
            st.session_state.df = load_network_data()
    
    df_all = st.session_state.df
    df_all["date"] = df_all["time"].dt.date

    st.sidebar.title("Network Console")
    st.sidebar.markdown("---")

    page = st.sidebar.radio("Module", ["Fleet Dashboard", "Forensic Replay"])
    st.sidebar.markdown("---")

    if page == "Fleet Dashboard":
        render_dashboard(df_all)
    else:
        render_replay(df_all)


if __name__ == "__main__":
    main()