from db import get_mysql_connection, get_mongodb_connection
import pandas as pd
from datetime import datetime, date  # Importação de datetime e date

# Obter conexões com o MySQL e o MongoDB
mysql_conn = get_mysql_connection()
mongo_db = get_mongodb_connection()

# Nome da coleção no MongoDB
mongo_collection = mongo_db["pessoas"]

# SQL para buscar os dados no MySQL
sql_query = """
SELECT 
    p.Id,
    p.Nome,
    p.eMail,
    pf.DataNascimento,
    pa.Id AS Viagem_Id,
    TRIM(pa.Modelo) AS Modelo,
    pa.Venda,
    pa.Viagem,
    pa.Poltrona,
    pa.SitBilh,
    pa.TipoBilh,
    pa.CodEmb,
    pa.Desemb,
    pa.Linha,
    pa.CodAgExt,
    pa.Operador,
    pc.ValorTotalPago,
    pc.IntermediacaoValor
FROM 
    sge.pessoa p 
LEFT JOIN 
    sge.pessoafisica pf ON p.Id = pf.Pessoa_Id
JOIN myads.msgpa50complemento pc ON p.Id = pc.Pessoa_Id
JOIN myads.msgpa50 pa ON pc.MSGPA50_Id = pa.Id
WHERE p.Nome LIKE 'MIRIA FREDERICO%' AND pa.Modelo = '   VOUCHER'
"""

# Função para tratar campos de datas e valores
def convert_fields(record):
    # Campos de data para converter
    date_fields = ["DataNascimento", "Venda", "Viagem"]

    for field in date_fields:
        if field in record and record[field] is not None:
            if isinstance(record[field], date):
                record[field] = datetime.combine(record[field], datetime.min.time())
    
    # Campos de valor float para converter
    float_fields = ["ValorTotalPago", "IntermediacaoValor"]

    for field in float_fields:
        if field in record and record[field] is not None:
            record[field] = float(record[field])
    
    return record

# Executar o SQL e processar os resultados
try:
    # Executar a consulta no MySQL
    with mysql_conn.cursor() as cursor:
        cursor.execute(sql_query)
        results = cursor.fetchall()

        # Obter os nomes das colunas
        column_names = [desc[0] for desc in cursor.description]

    # Converter os resultados para um DataFrame do pandas
    df = pd.DataFrame(results, columns=column_names)

    # Converter os resultados para uma lista de dicionários
    registros = df.to_dict(orient="records")

    # Converter campos de datas e valores
    registros = [convert_fields(record) for record in registros]

    # Separar informações da pessoa e das viagens
    if registros:
        pessoa_info = {
            "Id": registros[0]["Id"],
            "Nome": registros[0]["Nome"],
            "eMail": registros[0]["eMail"],
            "DataNascimento": registros[0]["DataNascimento"],
            "viagens": []
        }

        # Adicionar as viagens ao array
        for record in registros:
            viagem = {
                "Viagem_Id": record["Viagem_Id"],
                "Modelo": record["Modelo"],
                "Venda": record["Venda"],
                "Viagem": record["Viagem"],
                "Poltrona": record["Poltrona"],
                "SitBilh": record["SitBilh"],
                "TipoBilh": record["TipoBilh"],
                "CodEmb": record["CodEmb"],
                "Desemb": record["Desemb"],
                "Linha": record["Linha"],
                "CodAgExt": record["CodAgExt"],
                "Operador": record["Operador"],
                "ValorTotalPago": record["ValorTotalPago"],
                "IntermediacaoValor": record["IntermediacaoValor"]
            }
            pessoa_info["viagens"].append(viagem)

        # Inserir ou atualizar o documento no MongoDB
        filtro = {"Id": pessoa_info["Id"]}
        atualizacao = {"$set": pessoa_info}
        mongo_collection.update_one(filtro, atualizacao, upsert=True)
        print("Documento da pessoa inserido/atualizado no MongoDB.")
    else:
        print("Nenhum registro encontrado para processar.")
finally:
    # Fechar a conexão com o MySQL
    mysql_conn.close()
