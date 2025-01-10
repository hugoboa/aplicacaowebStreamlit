from adapters.db.postgres_adapter import PostgresAdapter
from config.settings import CONFIG

class AuthService:
    """
    Serviço de autenticação de usuários.
    """
    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """
        Verifica se o usuário e senha existem no banco de dados PostgreSQL.
        """
        query = """
            SELECT * 
            FROM usuarios 
            WHERE ativo = true AND usuario = %s AND senha = %s
        """
        connection_params = CONFIG["postgresql"]
        result = PostgresAdapter.execute_query(query, (username, password), connection_params)
        return result is not None
