import streamlit as st
from adapters.db.postgres_adapter import PostgresAdapter
from config.settings import CONFIG

def login_page():
    st.title("Login")
    

    # Formulário de Login
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Entrar")
    
    if submit_button:
        if not username or not password:
            st.warning("Por favor, preencha todos os campos.")
        else:
            try:
                query = """
                    SELECT * 
                    FROM usuarios 
                    WHERE ativo = true AND usuario = %s AND senha = %s
                """
                connection_params = CONFIG["postgresql"]
                user = PostgresAdapter.execute_query(query, (username, password), connection_params)

                if user and len(user) > 0:
                    user = user[0]  # Pegamos o primeiro registro retornado
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[2]
                    st.session_state.is_admin = user[5]
                    st.session_state.logged_in = True
                    st.session_state.current_page = "Home"  # Redirecionar para a Home
                else:
                    st.error("Usuário ou senha inválidos!")
            except Exception as e:
                st.error(f"Erro ao validar usuário: {e}")
    st.markdown("Por favor, insira suas credenciais para acessar o sistema.")
if __name__ == "__main__":
    login_page()
