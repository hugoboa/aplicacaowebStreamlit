import streamlit as st
from app.pages.home_page import home_page
from app.pages.login_page import login_page
from app.pages.dashboards_pages import dashboards_page

def initialize_session_state():
    """
    Inicializa as variáveis de estado da sessão.
    """
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Login"  # Página inicial padrão
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

def render_current_page():
    """
    Renderiza a página atual com base no estado da sessão.
    """
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Dashboards":
        dashboards_page()
    elif st.session_state.current_page == "Login":
        login_page()

def main():
    """
    Define o fluxo principal da aplicação Streamlit.
    """
    # Inicializar o estado de sessão
    initialize_session_state()

    # Menu de navegação
    st.sidebar.title("Navegação")

    # Exibir botão de logout se o usuário estiver logado
    if st.session_state.logged_in:
        st.sidebar.write(f"Bem-vindo, {st.session_state.username}!")
        if st.sidebar.button("Sair"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.current_page = "Login"

    # Controle de navegação
    if st.session_state.logged_in:
        menu_options = ["Home", "Dashboards"]
    else:
        menu_options = ["Login"]

    # Garantir que current_page seja uma das opções válidas
    if st.session_state.current_page not in menu_options:
        st.session_state.current_page = menu_options[0]

    # Renderizar menu de navegação
    menu = st.sidebar.radio(
        "Selecione uma página",
        menu_options,
        index=menu_options.index(st.session_state.current_page)  # Garante o índice correto
    )

    # Atualizar página atual no estado da sessão
    st.session_state.current_page = menu

    # Renderizar a página correspondente
    render_current_page()

if __name__ == "__main__":
    main()

