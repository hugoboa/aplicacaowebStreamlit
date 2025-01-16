from db import get_mongodb_connection
import pandas as pd

# Obter a conexão com o MongoDB
mongo_db = get_mongodb_connection()

# Nome da coleção no MongoDB
mongo_collection = mongo_db["pessoas"]
"""try:
    filtro = {"Id": {"$gte": 1000}}  # Excluir documentos com Id >= 5
    resultado = mongo_collection.delete_many(filtro)
    print(f"Documentos excluídos: {resultado.deleted_count}")
except Exception as e:
    print(f"Erro ao excluir os documentos: {e}")
"""

try:
    filtro = {"Id": 1, "viagens.Codigo": "V003"}  # Localiza o documento e a viagem pelo código
    atualizacao = {"$set": {"viagens.$.Status": "Cancelada"}}  # Atualiza o status da viagem
    resultado = mongo_collection.update_one(filtro, atualizacao)

    if resultado.modified_count > 0:
        print("Status da viagem atualizado com sucesso.")
    else:
        print("Nenhum documento foi atualizado. Verifique o filtro.")
except Exception as e:
    print(f"Erro ao atualizar o status: {e}")
try:

    qtd = mongo_collection.count_documents({"Id": {"exists": True}})
    print("Quantidade de documentos  {qtd}")

except Exception as e:    
    print("Erro seu burro")


# Recuperar todos os documentos
try:
    # Buscar todos os documentos na coleção
    documentos = mongo_collection.find()

    # Converter os documentos para uma lista de dicionários
    registros = list(documentos)

    # Exibir os documentos no console
    print("Documentos recuperados da coleção 'pessoas':")
    for registro in registros:
        print(registro)

    # Opcional: Converter para DataFrame do Pandas para manipulação
    df = pd.DataFrame(registros)

    # Exibir os primeiros registros no DataFrame
    print("\nPrimeiros registros como DataFrame:")
    print(df.head())

    # Salvar os dados em um arquivo CSV, se necessário
    df.to_csv("pessoas_recuperadas.csv", index=False, encoding="utf-8")
    print("\nDados salvos em 'pessoas_recuperadas.csv'.")
except Exception as e:
    print(f"Erro ao recuperar documentos: {e}")
