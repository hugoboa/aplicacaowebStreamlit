import streamlit as st
from app.pages.dashboard_page import Performance_comercial
def dashboards_page():
    st.title("Painel de Dashboards")
    st.markdown("Selecione um dos dashboards disponíveis abaixo:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Performance Comercial", key="performance_button"):
        # Atualiza o estado da página atual
            st.session_state.current_page = "comercial"
            st.experimental_rerun()  # Redireciona para a página correspondente

    with col2:
        if st.button("Finanças", key="financas_button"):
            st.session_state.current_page = "Financas"
            st.experimental_rerun()

    st.write("---")
    st.info("Mais dashboards estarão disponíveis em breve!")
