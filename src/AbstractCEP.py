from abc import ABC, abstractmethod
import json
import pandas as pd

class AbstractControlChart(ABC):
    def __init__(self, data_url, constants_url):
         # List, array, or DataFrame
        self.sample_size = 0
        self.num_samples = 0
        self.LC = None
        self.LSC = None
        self.LIC = None
        self.data = self.json_to_data(data_url)
        self.constants_table = self.json_to_data(constants_url)



    @staticmethod
    def json_to_data(url):
        try:
            
            with open(url, 'r') as f:
                json_data = json.load(f)
            
           
            if isinstance(json_data, list):
                return pd.DataFrame(json_data)
            # Se for um dicionário (como constantes_cep.json), retorna como está
            elif isinstance(json_data, dict):
                return json_data
            else:
                # Fallback para pd.read_json
                return pd.read_json(url)
        except Exception as e:
            print(f"Erro ao ler {url}: {e}")
            # Fallback para pd.read_json
            return pd.read_json(url)
        
