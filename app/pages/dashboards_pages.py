import streamlit as st

def dashboards_page():
    st.title("Painel de Dashboards")
    st.markdown("Selecione um dos dashboards disponíveis abaixo:")

    # Botões para acessar diferentes dashboards
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Performance Comercial"):
            st.session_state.current_page = "Performance_comercial"  # Atualiza o estado da página

    with col2:
        if st.button("Finanças"):
            st.session_state.current_page = "Financas"  # Atualiza o estado da página

    st.write("---")
    st.info("Mais dashboards estarão disponíveis em breve!")
