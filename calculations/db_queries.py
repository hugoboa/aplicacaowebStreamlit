import pandas as pd
import mysql.connector
from mysql.connector import Error
import streamlit as st

@st.cache_data
def executar_consulta(query, params=None, config=None):
    """
    Executa uma consulta SQL no MySQL e retorna os resultados como um DataFrame.
    """
    if config is None:
        raise ValueError("Configuração do banco de dados não fornecida.")
    
    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            port=config["port"]
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        resultado = cursor.fetchall()
        return pd.DataFrame(resultado)
    except Error as e:
        st.error(f"Erro ao executar consulta: {e}")
        return pd.DataFrame()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_dados_base(config):
    """
    Executa a consulta base e retorna os dados necessários.
    """
    query = """
    SELECT DISTINCT pa.Id, pa.Venda, pa.Viagem, pa.SitBilh, pa.TipoBilh, TRIM(pa.modelo) AS modelo,
                            pa.CodLin, pa.CodAgExt, pc.ValorTotalPago, ceem.Codigo AS ceem_codigo
,CONCAT(ceem.Codigo, '-', ceem.Descricao) codigo_nome_ceem 
,pc.ValorTotalPago
FROM myads.msgpa50 pa 
JOIN myads.msgpa50complemento pc ON pa.Id = pc.MSGPA50_Id
JOIN sge.seccionamento s ON pa.CodAgExt = s.Codigo
JOIN sge.poloseccionamento ps ON s.id = ps.Seccionamento_Id
JOIN sge.polo p ON ps.Polo_Id = p.Id
JOIN sge.ceem ceem ON p.CEEM_Id = ceem.Id
WHERE pa.Venda = CURDATE() AND pa.Modelo = '   VOUCHER'
AND NOT EXISTS(SELECT VoucherEmitido.Id FROM SGE.PassagemVinculo 
       JOIN MyADS.MSGPA50 AS VoucherEmitido ON VoucherEmitido.Id = PassagemVinculo.Passagem_Id_Principal 
        WHERE PassagemVinculo.Passagem_Id_Vinculada = pa.Id
          AND PassagemVinculo.Tipo = 3
          AND VoucherEmitido.SitBilh IN ("D", "S")
        LIMIT 1)
    """
    return executar_consulta(query, config=config)
