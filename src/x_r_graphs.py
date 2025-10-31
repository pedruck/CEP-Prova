from abc import ABC
import AbstractCEP as AbstractCEP
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import western_electric_rules as wer
import report_bridge as rg


class XR_graph(AbstractCEP.AbstractControlChart):
    df: DataFrame
    x_data: list
    sigma: float
    r_mean: float
    x_double_mean: float
    lsc_x_bar_graph: float
    lic_x_bar_graph: float
    lsc_r_bar_graph: float
    lic_r_bar_graph: float
    lse: float = None
    lie: float = None

    def __init__(self, data_url="json_files/dados.json", constants_url="json_files/constantes_cep.json"):
        super().__init__(data_url, constants_url)
        self.normalize_data()

    def normalize_data(self):
        self.df = pd.DataFrame(self.data)
        data_columns = self.df["Dados"].apply(pd.Series)
        data_columns = data_columns.rename(columns=lambda x: f'X{x+1}')
        self.df = pd.concat([self.df.drop(columns=["Dados"], axis=1), data_columns], axis=1)
        print("DataFrame completo:")
        print(self.df)
        self.calculate_xbar_and_r()

    def calculate_xbar_and_r(self):
        x_columns = [col for col in self.df.columns if col.startswith('X')]
        self.df["X_bar"] = self.df[x_columns].mean(axis=1)
        self.df["R"] = self.df[x_columns].max(axis=1) - self.df[x_columns].min(axis=1)
        print("Tabela X-R completa:")
        print(self.df)
        self.calculate_internal_metrics()

    def calculate_internal_metrics(self):
        self.r_mean = self.df["R"].mean()
        print(f"R_BAR: {self.r_mean}")
        n_size = len([col for col in self.df.columns if col.startswith('X')])
        d2_value = self.constants_table[str(n_size)]["d2"]
        self.sigma = self.r_mean / d2_value
        print(f"SIGMA: {self.sigma}")
        self.x_double_mean = self.df["X_bar"].mean()
        print(f"X_DOUBLE_BAR: {self.x_double_mean}")
        self.limits_calculation_x_bar_graph()

    def limits_calculation_x_bar_graph(self):
        n_size = len([col for col in self.df.columns if col.startswith('X')])
        a2_value = self.constants_table[str(n_size)]["A2"]
        self.lsc_x_bar_graph = self.x_double_mean + (a2_value * self.r_mean)
        self.lic_x_bar_graph = self.x_double_mean - (a2_value * self.r_mean)
        print(f"LIC (X_BAR): {self.lic_x_bar_graph}")
        print(f"LC (X_BAR): {self.x_double_mean}")
        print(f"LSC (X_BAR): {self.lsc_x_bar_graph}")
        self.limits_calculation_r_graph()

    def limits_calculation_r_graph(self):
        n_size = len([col for col in self.df.columns if col.startswith('X')])
        d3_value = self.constants_table[str(n_size)]["D3"]
        d4_value = self.constants_table[str(n_size)]["D4"]
        self.lsc_r_bar_graph = self.r_mean * d4_value
        self.lic_r_bar_graph = self.r_mean * d3_value
        print(f"LIC (R): {self.lic_r_bar_graph}")
        print(f"LC (R): {self.r_mean}")
        print(f"LSC (R): {self.lsc_r_bar_graph}")
        self.plot_control_charts()

    def plot_control_charts(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        x_bar_min = min(self.df['X_bar'].min(), self.lic_x_bar_graph)
        x_bar_max = max(self.df['X_bar'].max(), self.lsc_x_bar_graph)
        x_bar_margin = (x_bar_max - x_bar_min) * 0.1
        r_min = min(self.df['R'].min(), self.lic_r_bar_graph)
        r_max = max(self.df['R'].max(), self.lsc_r_bar_graph)
        r_margin = (r_max - r_min) * 0.1
        ax1.plot(self.df['Amostra'], self.df['X_bar'], 'bo-', linewidth=2, markersize=6, label='X̄')
        ax1.axhline(y=self.x_double_mean, color='green', linestyle='-', linewidth=2, label=f'LC = {self.x_double_mean:.4f}')
        ax1.axhline(y=self.lsc_x_bar_graph, color='red', linestyle='--', linewidth=2, label=f'LSC = {self.lsc_x_bar_graph:.4f}')
        ax1.axhline(y=self.lic_x_bar_graph, color='red', linestyle='--', linewidth=2, label=f'LIC = {self.lic_x_bar_graph:.4f}')
        ax1.set_xlabel('Número da Amostra', fontsize=12)
        ax1.set_ylabel('X̄', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.set_ylim(x_bar_min - x_bar_margin, x_bar_max + x_bar_margin)
        ax2.plot(self.df['Amostra'], self.df['R'], 'ro-', linewidth=2, markersize=6, label='R')
        ax2.axhline(y=self.r_mean, color='green', linestyle='-', linewidth=2, label=f'LC = {self.r_mean:.4f}')
        ax2.axhline(y=self.lsc_r_bar_graph, color='red', linestyle='--', linewidth=2, label=f'LSC = {self.lsc_r_bar_graph:.4f}')
        ax2.axhline(y=self.lic_r_bar_graph, color='red', linestyle='--', linewidth=2, label=f'LIC = {self.lic_r_bar_graph:.4f}')
        ax2.set_ylabel('R', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.set_ylim(max(0, r_min - r_margin), r_max + r_margin)
        plt.subplots_adjust(hspace=0.4)
        plt.tight_layout()
        plt.savefig('grafico_controle_xr.png', dpi=300, bbox_inches='tight')
        print("Gráfico salvo como 'grafico_controle_xr.png'")
        plt.close(fig)

    def analyze_control_status(self):
        out_of_control_x = self.df[(self.df['X_bar'] > self.lsc_x_bar_graph) | (self.df['X_bar'] < self.lic_x_bar_graph)]
        out_of_control_r = self.df[self.df['R'] > self.lsc_r_bar_graph]
        total_out_of_control = len(out_of_control_x) + len(out_of_control_r)
        print(f"Quantidade de termos fora dos limites de controle (X-barra): {len(out_of_control_x)}")
        print(f"Quantidade de termos fora dos limites de controle (R): {len(out_of_control_r)}")
        print(f"Total de termos fora dos limites de controle: {total_out_of_control}")
        if self.lse is not None and self.lie is not None:
            from process_capability import ProcessCapability
            capability = ProcessCapability(
                sigma=self.sigma,
                lse=self.lse,
                lie=self.lie
            )
            capability.set_process_mean(self.x_double_mean)
            capability.calculate_all()
            self.capability = capability
        wer.analyze_xr_chart(self)
        rg.generate_report_from_instance(self, chart_type="XR")

    def set_default_specification_limits(self):
        import pandas as pd
        temp_df = pd.DataFrame(self.data)
        temp_data_columns = temp_df["Dados"].apply(pd.Series)
        temp_data_columns = temp_data_columns.rename(columns=lambda x: f'X{x+1}')
        temp_complete_df = pd.concat([temp_df.drop(columns=["Dados"], axis=1), temp_data_columns], axis=1)
        x_columns = [col for col in temp_complete_df.columns if col.startswith('X')]
        temp_x_bar = temp_complete_df[x_columns].mean(axis=1).mean()
        temp_std = temp_complete_df[x_columns].values.flatten().std()
        self.lse = temp_x_bar + (3 * temp_std)
        self.lie = temp_x_bar - (3 * temp_std)
        print(f"📊 Limites de especificação padrão definidos:")
        print(f"   LSE (Limite Superior): {self.lse:.4f}")
        print(f"   LIE (Limite Inferior): {self.lie:.4f}")

    def set_specification_limits(self, lse: float, lie: float):
        self.lse = lse
        self.lie = lie
        print(f"[INFO] Limites de especificação definidos:")
        print(f"   LSE (Limite Superior): {self.lse:.4f}")
        print(f"   LIE (Limite Inferior): {self.lie:.4f}")