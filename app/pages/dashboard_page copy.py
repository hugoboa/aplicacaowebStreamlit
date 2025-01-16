import streamlit as st
import plotly.express as px
import pandas as pd
from adapters.db.postgres_adapter import PostgresAdapter
from config.settings import CONFIG
import os
import plotly.express as px


def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    else:
        st.error(f"Arquivo CSS não encontrado: {css_file_path}")

        
st.header("Métricas")
# Carregar o CSS
css_path = "assets/style.css"
load_css(css_path)

@st.cache_data
def load_csv(file_path):
    try:
        return pd.read_csv(file_path, sep=";")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None
    

#if st.button("Limpar Cache"):
#    st.cache_data.clear()
#    st.success("Cache limpo!")

# buscar dados de ceem
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
    file_path = r"C:\Users\hugo\Downloads\dados_concatenados - Copia.csv"
    
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

        # Filtrar os dados com base na CEEM selecionada
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
        st.header("Informações totalizadoras")
        #col1, col2, col3, col4 = st.columns(4)
        qtd_passagens = data["Id"].nunique()
        valor_total_pago = data["ValorTotalPago"].sum()
        #qtdCEEM = data["codigo_ceem"].nunique()
        #Soma_id_Passagem = data["Id"].sum()
        #col1.metric("Quantidade de Passagens", qtd_passagens)
        #col2.metric("Valor Total Pago (R$)", f"R$ {valor_total_pago:,.2f}")
        #col3.metric("Quantidade de CEEM", qtdCEEM)
        #col4.metric(" SOMA ID PASSAGEM",Soma_id_Passagem)
        ValorPago = format(valor_total_pago, ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.')
        ceem_consolidated = data.groupby("codigo_nome_ceem").agg(
            qtd_passagens=("Id", "nunique"),
            valor_total=("ValorTotalPago", "sum")
        ).reset_index()


        st.markdown(
            f"""
                <div class="metric-container">
                    <div class="metric-box metric-passagens ">
                        <h2>Quantidade de Passagens</h2>
                        <p>{qtd_passagens}</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>Valor Total Pago</h2>
                        <p> R$: {ValorPago}</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>Proprias</h2>
                        <p> valor a ser ajustado</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>Terceiras</h2>
                        <p> valor a ser ajustado</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>Site Eucatur</h2>
                        <p> valor a ser ajustado</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>Portais</h2>
                        <p> valor a ser ajustado</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>EU + Parceiros</h2>
                        <p> valor a ser ajustado</p>
                    </div>
                    <div class="metric-box metric-valor_venda">
                        <h2>Link de pagamento</h2>
                        <p> valor a ser ajustado</p>
                    </div>

                </div>
            """,
            unsafe_allow_html=True
        )
      

        # Gráfico de Linha
        st.write("Evolução do valor total pago ao longo do tempo.")
        if "Venda" in data.columns and "ValorTotalPago" in data.columns:
            # Agrupar os dados por data de venda
            df_line = data.groupby("Venda")["ValorTotalPago"].sum().reset_index()

            # Criar o gráfico de linha
            fig = px.line(
                df_line,
                x="Venda",
                y="ValorTotalPago",
                title="Valor Total Pago por Data de Venda",
                labels={"Venda": "Data de Venda", "ValorTotalPago": "Valor Total Pago (R$)"},
                markers=True,
                template="plotly_white"
            )

            # Adicionar rótulos nos pontos
             # Adicionar rótulos nos pontos
            fig.update_traces(
                text=df_line["ValorTotalPago"].map(lambda x: f"R$ {x:,.2f}"),  # Formatar rótulos no estilo brasileiro
                textposition="top center"  # Posicionar rótulos acima dos pontos
            )
            # Remover o título do eixo Y
            fig.update_layout(
                xaxis_title="Data de Venda",  # Título do eixo X
                yaxis_title=None,  # Sem título no eixo Y
                xaxis=dict(
                tickformat="%d %b %Y"  # Formato de data: 01 Jan 2023
                )
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig)
        
       #Layout com duas colunas: tabela à esquerda e gráfico à direita
        col1, col2 = st.columns([2,1])
        with col1:
            # Exibir a tabela consolidada por CEEM
            st.header("Consolidado por CEEM")
            st.dataframe(ceem_consolidated, height=500)
        with col2:
            st.header("Distribuição por Categoria")
            fig = px.pie(
                data,
                values="ValorTotalPago",
                names="nome_ceem",
                title="Distribuição de Categorias",
                hole=0.4  # Gráfico de pizza tipo donut
            )
            fig.update_traces(textinfo="percent+label")  # Mostra porcentagem e rótulo
            st.plotly_chart(fig, use_container_width=True)

        # Baixar dados filtrados
        st.write("Será listados dados de CEEM")
        st.download_button(
            label="Baixar Dados Filtrados",
            data=ceem_consolidated.to_csv(index=False,sep=";").encode("utf-8"),
            file_name="consolidado_ceem.csv",
            mime="text/csv"
        )


    else:
        st.error("Falha ao carregar o CSV. Verifique o caminho e o formato do arquivo.")

if __name__ == "__main__":
    Performance_comercial()
