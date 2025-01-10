import psycopg2

class PostgresAdapter:
    @staticmethod
    def execute_query(query, params, connection_params):
        try:
            with psycopg2.connect(**connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if query.strip().lower().startswith("select"):
                        # Apenas para consultas SELECT
                        return cur.fetchall()
                    else:
                        # Para operações que não retornam resultados (INSERT, UPDATE, DELETE)
                        conn.commit()
                        return None
        except Exception as e:
            raise RuntimeError(f"Erro ao executar a consulta no PostgreSQL: {e}")
