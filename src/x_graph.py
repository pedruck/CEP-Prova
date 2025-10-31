from abc import ABC
import AbstractCEP as AbstractCEP
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import western_electric_rules as wer
import report_bridge as rg


class X_graph(AbstractCEP.AbstractControlChart):
    df: DataFrame
    sigma: float
    x_mean: float
    lsc_x_graph: float
    lic_x_graph: float
    lse: float = None
    lie: float = None

    def __init__(self, data_url="json_files/dados_individuais.json", constants_url="json_files/constantes_cep.json"):
        super().__init__(data_url, constants_url)
        self.normalize_data()

    def normalize_data(self):
        self.df = pd.DataFrame(self.data)
        print("DataFrame de medidas individuais:")
        print(self.df)
        self.calculate_internal_metrics()

    def calculate_internal_metrics(self):
       
        self.x_mean = self.df["Valor"].mean()
        print(f"X_BAR (média): {self.x_mean}")
        
        self.sigma = self.df["Valor"].std()
        print(f"SIGMA: {self.sigma}")

        self.limits_calculation_x_graph()

    def limits_calculation_x_graph(self):

        self.lsc_x_graph = self.x_mean + (3 * self.sigma)
        self.lic_x_graph = self.x_mean - (3 * self.sigma)
        
        print(f"LIC (X): {self.lic_x_graph}")
        print(f"LC (X): {self.x_mean}")
        print(f"LSC (X): {self.lsc_x_graph}")
        self.plot_control_charts()

    def plot_control_charts(self):

       
        fig, ax1 = plt.subplots(1, 1, figsize=(16, 8))
        
        x_min = min(self.df['Valor'].min(), self.lic_x_graph)
        x_max = max(self.df['Valor'].max(), self.lsc_x_graph)
        x_margin = (x_max - x_min) * 0.15
        
        
        ax1.plot(self.df['Medida'], self.df['Valor'], 'bo-', linewidth=2, markersize=6, label='X (Medidas Individuais)')
        ax1.axhline(y=self.x_mean, color='green', linestyle='-', linewidth=2, label=f'LC = {self.x_mean:.4f}')
        ax1.axhline(y=self.lsc_x_graph, color='red', linestyle='--', linewidth=2, label=f'LSC = {self.lsc_x_graph:.4f}')
        ax1.axhline(y=self.lic_x_graph, color='red', linestyle='--', linewidth=2, label=f'LIC = {self.lic_x_graph:.4f}')
        
        ax1.set_title('Gráfico de Controle X (Medidas Individuais)', fontsize=14, fontweight='bold', pad=20)
        ax1.set_xlabel('Número da Medida', fontsize=12)
        ax1.set_ylabel('Valor (X)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.set_ylim(x_min - x_margin, x_max + x_margin)
        
        
        out_of_control_x = self.df[(self.df['Valor'] > self.lsc_x_graph) | (self.df['Valor'] < self.lic_x_graph)]
        if not out_of_control_x.empty:
            ax1.scatter(out_of_control_x['Medida'], out_of_control_x['Valor'], 
                       color='red', s=100, marker='o', facecolors='none', edgecolors='red', linewidth=3)
        
        
        plt.tight_layout()
        
        
        plt.savefig('grafico_controle_x.png', dpi=300, bbox_inches='tight')
        print("Gráfico salvo como 'grafico_controle_x.png'")
        
       
        plt.close(fig)
        
       
    def analyze_control_status(self):
     
        
        out_of_control_x = self.df[(self.df['Valor'] > self.lsc_x_graph) | (self.df['Valor'] < self.lic_x_graph)]
        
        print(f"Quantidade de termos fora dos limites de controle: {len(out_of_control_x)}")
        
        
        if self.lse is not None and self.lie is not None:
            from process_capability import ProcessCapability
            capability = ProcessCapability(
                sigma=self.sigma,
                lse=self.lse,
                lie=self.lie
            )
            capability.set_process_mean(self.x_mean)
            capability.calculate_all()
            
            
            self.capability = capability
            
        

        wer.analyze_x_chart(self)
        
        
        rg.generate_report_from_instance(self, chart_type="X")

    def set_specification_limits(self, lse: float, lie: float):

        self.lse = lse
        self.lie = lie
        print(f"[INFO]: Limites de especificação atualizados:")
        print(f"   LSE (Limite Superior): {self.lse:.4f}")
        print(f"   LIE (Limite Inferior): {self.lie:.4f}")
