import pandas as pd

class CSVAdapter:
    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """
        Carrega um arquivo CSV e retorna como um DataFrame do pandas.
        """
        try:
            return pd.read_csv(file_path, sep=";")
        except FileNotFoundError:
            raise RuntimeError(f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar o CSV: {e}")
