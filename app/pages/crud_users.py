import streamlit as st
import pandas as pd
from adapters.db.postgres_adapter import PostgresAdapter
from config.settings import CONFIG

# Funções para interagir com o banco de dados
def get_users():
    query = "SELECT id_usuario, nome, usuario, ativo, admin FROM usuarios"
    try:
        result = PostgresAdapter.execute_query(query, None, CONFIG["postgresql"])
        return pd.DataFrame(result, columns=["ID", "Nome", "Usuário", "Ativo", "Admin"])
    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")
        return pd.DataFrame()

def get_ceems():
    query = "SELECT id, codigo, nome_ceem FROM ceems"
    try:
        result = PostgresAdapter.execute_query(query, None, CONFIG["postgresql"])
        return pd.DataFrame(result, columns=["ID", "Código", "Nome CEEM"])
    except Exception as e:
        st.error(f"Erro ao carregar CEEMs: {e}")
        return pd.DataFrame()

def get_user_ceems(user_id):
    query = """
    SELECT codigo_ceem
    FROM acesso_ceem_usuario
    WHERE id_usuario = %s
    """
    try:
        result = PostgresAdapter.execute_query(query, (user_id,), CONFIG["postgresql"])
        return [row[0] for row in result]
    except Exception as e:
        st.error(f"Erro ao carregar os acessos de CEEMs do usuário: {e}")
        return []

def add_user(nome, usuario, senha, ativo, admin):
    query = """
    INSERT INTO usuarios (nome, usuario, senha, ativo, admin)
    VALUES (%s, %s, %s, %s, %s) RETURNING id_usuario
    """
    params = (nome, usuario, senha, ativo, admin)
    try:
        result = PostgresAdapter.execute_query(query, params, CONFIG["postgresql"])
        return result[0] if result else None
    except Exception as e:
        st.error(f"Erro ao adicionar usuário: {e}")
        return None

def add_user_ceem_access(user_id, ceem_codes):
    query = """
    INSERT INTO acesso_ceem_usuario (id_usuario, codigo_ceem)
    VALUES (%s, %s)
    """
    try:
        for ceem_code in ceem_codes:
            PostgresAdapter.execute_query(query, (user_id, ceem_code), CONFIG["postgresql"])
    except Exception as e:
        st.error(f"Erro ao configurar acesso aos CEEMs: {e}")

def update_user(user_id, nome, usuario, ativo, admin):
    query = """
    UPDATE usuarios
    SET nome = %s, usuario = %s, ativo = %s, admin = %s
    WHERE id_usuario = %s
    """
    params = (nome, usuario, ativo, admin, user_id)
    try:
        PostgresAdapter.execute_query(query, params, CONFIG["postgresql"])
    except Exception as e:
        st.error(f"Erro ao atualizar usuário: {e}")

def update_user_ceem_access(user_id, new_ceem_codes):
    try:
        current_ceems = get_user_ceems(user_id)
        ceems_to_add = set(new_ceem_codes) - set(current_ceems)
        ceems_to_remove = set(current_ceems) - set(new_ceem_codes)

        for ceem_code in ceems_to_add:
            PostgresAdapter.execute_query(
                "INSERT INTO acesso_ceem_usuario (id_usuario, codigo_ceem) VALUES (%s, %s)",
                (user_id, ceem_code),
                CONFIG["postgresql"]
            )
        for ceem_code in ceems_to_remove:
            PostgresAdapter.execute_query(
                "DELETE FROM acesso_ceem_usuario WHERE id_usuario = %s AND codigo_ceem = %s",
                (user_id, ceem_code),
                CONFIG["postgresql"]
            )
    except Exception as e:
        st.error(f"Erro ao atualizar acessos de CEEMs: {e}")

def delete_user(user_id):
    try:
        PostgresAdapter.execute_query("DELETE FROM acesso_ceem_usuario WHERE id_usuario = %s", (user_id,), CONFIG["postgresql"])
        PostgresAdapter.execute_query("DELETE FROM usuarios WHERE id_usuario = %s", (user_id,), CONFIG["postgresql"])
    except Exception as e:
        st.error(f"Erro ao excluir usuário: {e}")

# Função principal do CRUD
def crud_users():
    st.title("Gerenciamento de Usuários")

    # Verificar se o usuário está logado e é administrador
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("Você precisa estar logado para acessar esta página.")
        st.stop()

    if "is_admin" not in st.session_state or not st.session_state.is_admin:
        st.error("Você não tem permissão para acessar esta página.")
        st.stop()

    # Tabs para Create, Read, Update, Delete
    tab1, tab2, tab3, tab4 = st.tabs(["Adicionar Usuário", "Listar Usuários", "Editar Usuário", "Remover Usuário"])

    # Tab: Adicionar Usuário
    with tab1:
        st.header("Adicionar Usuário")
        with st.form("add_user_form"):
            nome = st.text_input("Nome")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            ativo = st.checkbox("Ativo", value=True)
            admin = st.checkbox("Admin")

            ceems = get_ceems()
            if ceems.empty:
                st.error("Nenhum CEEM encontrado.")
                return

            ceem_options = ceems["Nome CEEM"].tolist()
            selecionar_todas = st.checkbox("Selecionar Todas as CEEMs")
            if selecionar_todas:
                ceem_selecionadas = ceem_options
            else:
                ceem_selecionadas = st.multiselect("Selecione os CEEMs para acesso", options=ceem_options)

            submit = st.form_submit_button("Adicionar")

            if submit:
                if not nome or not usuario or not senha:
                    st.error("Todos os campos devem ser preenchidos.")
                elif not ceem_selecionadas:
                    st.error("Selecione pelo menos um CEEM.")
                else:
                    user_id = add_user(nome, usuario, senha, ativo, admin)
                    if user_id:
                        ceem_codes = ceems[ceems["Nome CEEM"].isin(ceem_selecionadas)]["Código"].tolist()
                        add_user_ceem_access(user_id, ceem_codes)
                        st.success(f"Usuário {nome} adicionado com sucesso!")

    # Tab: Listar Usuários
    with tab2:
        st.header("Lista de Usuários")
        users = get_users()
        st.dataframe(users, use_container_width=True)

    # Tab: Editar Usuário
    # Tab: Editar Usuário
    with tab3:
        st.header("Editar Usuário")
        users = get_users()
        user_id = st.selectbox("Selecione um Usuário para Editar", users["ID"])
        if user_id:
            selected_user = users[users["ID"] == user_id].iloc[0]
            with st.form("edit_user_form"):
                nome = st.text_input("Nome", value=selected_user["Nome"])
                usuario = st.text_input("Usuário", value=selected_user["Usuário"])
                ativo = st.checkbox("Ativo", value=selected_user["Ativo"])
                admin = st.checkbox("Admin", value=selected_user["Admin"])

                ceems = get_ceems()
                if ceems.empty:
                    st.error("Nenhum CEEM encontrado.")
                    return

                # Recuperar os CEEMs associados ao usuário
                user_ceems = get_user_ceems(user_id)
                user_ceem_names = ceems[ceems["Código"].isin(user_ceems)]["Nome CEEM"].tolist()

                # Checkbox para selecionar todas as CEEMs
                selecionar_todas = st.checkbox("Selecionar Todas as CEEMs")
                if selecionar_todas:
                    ceem_selecionadas = ceems["Nome CEEM"].tolist()  # Todas as CEEMs
                else:
                    # Multiselect com os nomes correspondentes como valores padrão
                    ceem_selecionadas = st.multiselect(
                        "Selecione os CEEMs para acesso",
                        options=ceems["Nome CEEM"].tolist(),
                        default=user_ceem_names  # Valores padrão correspondentes
                    )

                submit = st.form_submit_button("Atualizar")

                if submit:
                    update_user(user_id, nome, usuario, ativo, admin)
                    ceem_codes = ceems[ceems["Nome CEEM"].isin(ceem_selecionadas)]["Código"].tolist()
                    update_user_ceem_access(user_id, ceem_codes)
                    st.success(f"Usuário {nome} atualizado com sucesso!")
                    st.experimental_rerun()  # Recarrega a página


   
    # Tab: Remover Usuário
    with tab4:
        st.header("Remover Usuário")

        # Exibir lista de usuários
        st.subheader("Lista de Usuários")
        users = get_users()
        if users.empty:
            st.warning("Nenhum usuário disponível para exclusão.")
        else:
            # Exibe a tabela sem a coluna de índices
            st.dataframe(users.style.hide(axis='index'), use_container_width=True)

            # Selecionar usuário para remover
            user_id = st.selectbox("Selecione um Usuário para Remover", users["ID"])
            if user_id:
                if st.button("Remover Usuário"):
                    delete_user(user_id)
                    st.success(f"Usuário ID {user_id} removido com sucesso!")
                    st.experimental_rerun()  # Recarrega a página


if __name__ == "__main__":
    crud_users()
