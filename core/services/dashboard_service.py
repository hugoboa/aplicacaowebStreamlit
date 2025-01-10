from adapters.db.csv_adapter import CSVAdapter
from adapters.db.postgres_adapter import PostgresAdapter
from config.settings import CONFIG

class DashboardService:
    """
    Lida com a lógica de negócios para o dashboard.
    """
    @staticmethod
    def get_dashboard_data_csv():
        """
        Carrega dados de um arquivo CSV.
        """
        return CSVAdapter.load_csv(CONFIG["csv_file_path"])

    @staticmethod
    def get_dashboard_data_postgres(query: str):
        """
        Executa uma consulta no PostgreSQL e retorna os resultados.
        """
        connection_params = CONFIG["postgresql"]
        return PostgresAdapter.execute_query(query, connection_params)

    @staticmethod
    def calculate_metrics(data):
        """
        Calcula métricas básicas, como o número de passagens e o valor total pago.
        """
        qtd_passagens = data["Id"].nunique()
        valor_total_pago = data["ValorTotalPago"].sum()
        return {"qtd_passagens": qtd_passagens, "valor_total_pago": valor_total_pago}
