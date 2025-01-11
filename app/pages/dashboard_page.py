import streamlit as st
import plotly.express as px
import pandas as pd
from adapters.db.postgres_adapter import PostgresAdapter
from config.settings import CONFIG

def load_csv(file_path):
    try:
        return pd.read_csv(file_path, sep=";")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

def get_user_ceems(user_id):
    """
    Recupera os códigos das CEEMs vinculadas ao usuário logado.
    """
    query = """
    SELECT codigo_ceem
    FROM acesso_ceem_usuario
    WHERE id_usuario = %s
    """
    try:
        result = PostgresAdapter.execute_query(query, (user_id,), CONFIG["postgresql"])
        return [row[0] for row in result]
    except Exception as e:
        st.error(f"Erro ao carregar CEEMs do usuário: {e}")
        return []

def Performance_comercial():
    # Verificar se o usuário está logado
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()

    st.title("Performance Comercial")
    st.sidebar.success(f"Bem-vindo, {st.session_state.username}!")

    # Adicionar botão de logout
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.is_admin = None
        st.session_state.current_page = "Login"
        st.experimental_rerun()

    # Recuperar as CEEMs vinculadas ao usuário
    user_ceems = get_user_ceems(st.session_state.user_id)
    if not user_ceems:
        st.warning("Você não tem acesso a nenhuma CEEM.")
        st.stop()

    # Carregar o CSV
    file_path = r"C:\Users\hugo\Downloads\dados_concatenados.csv"
    data = load_csv(file_path)

    if data is not None:
        # Garantir que 'codigo_ceem' seja string
        if "codigo_ceem" in data.columns:
            data["codigo_ceem"] = data["codigo_ceem"].astype(str)
        else:
            st.error("A coluna 'codigo_ceem' não está presente no CSV.")
            return

        # Filtrar os dados com base nas CEEMs vinculadas ao usuário
        data = data[data["codigo_ceem"].isin(map(str, user_ceems))]

        # Verificar se o DataFrame está vazio após o filtro
        if data.empty:
            st.warning("Nenhum dado encontrado para as CEEMs atribuídas ao seu usuário.")
            return

        # Criar campo combinado para o filtro de CEEM
        if "nome_ceem" in data.columns:
            data["codigo_nome_ceem"] = data["codigo_ceem"] + " - " + data["nome_ceem"]
        else:
            st.error("A coluna 'nome_ceem' não está presente no CSV.")
            return

        # Barra lateral para filtros
        st.sidebar.header("Filtros")

        # Filtro de CEEM
        ceem_opcoes = data["codigo_nome_ceem"].unique().tolist()
        ceem_opcoes.insert(0, "Todos")
        ceem_selecionado = st.sidebar.selectbox("Selecione o CEEM", ceem_opcoes)

        # Filtrar os dados com base no CEEM selecionado
        if ceem_selecionado != "Todos":
            codigo_ceem_selecionado = ceem_selecionado.split(" - ")[0]
            data = data[data["codigo_ceem"] == codigo_ceem_selecionado]

        # Filtro de Data
        if "Venda" in data.columns:
            data["Venda"] = pd.to_datetime(data["Venda"], errors="coerce")
            data = data.dropna(subset=["Venda"])
            if not data.empty:
                st.sidebar.subheader("Filtro por Data")
                min_date = data["Venda"].min().date()
                max_date = data["Venda"].max().date()
                selected_dates = st.sidebar.date_input(
                    "Intervalo de datas",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
                if len(selected_dates) == 2:
                    start_date, end_date = selected_dates
                    data = data[(data["Venda"] >= pd.Timestamp(start_date)) & (data["Venda"] <= pd.Timestamp(end_date))]

        # Verificar se o DataFrame está vazio após os filtros
        if data.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
            return

        # Métricas
        st.header("Métricas")
        col1, col2, col3 = st.columns(3)
        qtd_passagens = data["Id"].nunique()
        valor_total_pago = data["ValorTotalPago"].sum()
        qtdCEEM = data["codigo_ceem"].nunique()
        col1.metric("Quantidade de Passagens", qtd_passagens)
        col2.metric("Valor Total Pago (R$)", f"R$ {valor_total_pago:,.2f}")
        col3.metric("Quantidade de CEEM", qtdCEEM)

        ceem_consolidated = data.groupby("codigo_nome_ceem").agg(
            qtd_passagens=("Id", "nunique"),
            valor_total=("ValorTotalPago", "sum")
        ).reset_index()

        # Exibir a tabela consolidada
        st.header("Consolidado por CEEM")
        st.dataframe(ceem_consolidated, height=500)

        # Gráfico de Linha
        st.header("Performance Comercial")
        st.write("Evolução do valor total pago ao longo do tempo.")
        if "Venda" in data.columns and "ValorTotalPago" in data.columns:
            df_line = data.groupby("Venda")["ValorTotalPago"].sum().reset_index()
            fig = px.line(
                df_line,
                x="Venda",
                y="ValorTotalPago",
                title="Valor Total Pago por Data de Venda",
                labels={"Venda": "Data de Venda", "ValorTotalPago": "Valor Total Pago (R$)"},
                markers=True,
                template="plotly_white"
            )
            fig.update_layout(xaxis_title="Data de Venda", yaxis_title="Valor Total Pago (R$)")
            st.plotly_chart(fig)
        # Exibir a tabela com paginação
        st.header("Tabela de Dados Filtrados")
        rows_per_page = 100
        total_rows = len(data)
        total_pages = (total_rows - 1) // rows_per_page + 1

        page_number = st.number_input(
            label="Número da página",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1
        )

        start_idx = (page_number - 1) * rows_per_page
        end_idx = start_idx + rows_per_page

        st.write(f"Mostrando linhas {start_idx + 1} a {min(end_idx, total_rows)} de {total_rows}")
        st.dataframe(data.iloc[start_idx:end_idx])

        
        # Baixar dados filtrados
        st.download_button(
            label="Baixar Dados Filtrados",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name="dados_filtrados.csv",
            mime="text/csv"
)


    else:
        st.error("Falha ao carregar o CSV. Verifique o caminho e o formato do arquivo.")

if __name__ == "__main__":
    Performance_comercial()
