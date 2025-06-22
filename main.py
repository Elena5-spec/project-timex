import streamlit as st
from load_data import load_data
from transform_data import transform_data
from analyze_data import analyze_data

def main() -> None:
    st.set_page_config(page_title="ВремяИКС", page_icon="📊", layout="wide")
    st.title("Прогноз успеваемости студентов")
    
    load_col, transform_col, analyze_col = st.columns([1.1, 1, 2], border=True)

    with load_col:
        load_data()

    with transform_col:
        transform_data(st.session_state.df)

    with analyze_col:
        if not st.session_state.df.empty:
            analyze_data(st.session_state.df)
        else:
            st.info("Пожалуйста, сначала загрузите данные")

    st.markdown(
        """
        <hr style='margin-top:2em;margin-bottom:0.5em;'>
        <div style='text-align:center; font-size: 1em;'>
            <a href="https://github.com/Elena5-spec" target="_blank" style="color: #6e5494; text-decoration: none; font-weight: bold;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" width="24" style="vertical-align:middle; margin-right:0.4em;">
                Аккаунт создателя Elen5-spec
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
