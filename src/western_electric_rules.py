import pandas as pd
import numpy as np
from typing import List, Tuple, Dict


class WesternElectricAnalyzer:

    
    def __init__(self, data: pd.Series, lc: float, lsc: float, lic: float, chart_name: str = "Gráfico"):

        self.data = data
        self.lc = lc
        self.lsc = lsc
        self.lic = lic
        self.chart_name = chart_name
        
       
        self.sigma = (lsc - lc) / 3  
        
        
        self.zone_a_upper = lc + 2 * self.sigma  
        self.zone_a_lower = lc - 2 * self.sigma  
        self.zone_b_upper = lc + self.sigma      
        self.zone_b_lower = lc - self.sigma      
        
        self.violations = {
            'rule1': [],
            'rule2': [],
            'rule3': [],
            'rule4': []
        }
        self.state = "estavel"
    
    def analyze_all_rules(self) -> Dict:

        self.rule1_one_point_beyond_3sigma()
        self.rule2_two_of_three_beyond_2sigma()
        self.rule3_four_of_five_beyond_1sigma()
        self.rule4_eight_consecutive_same_side()
        
        total_violations = sum(len(v) for v in self.violations.values())
        self.state = "estavel" if total_violations == 0 else "instavel"
        return self.violations
    
    def rule1_one_point_beyond_3sigma(self):

        for idx, value in enumerate(self.data):
            if value > self.lsc or value < self.lic:
                position = idx + 1 if hasattr(self.data, 'index') else idx
                side = "acima do LSC" if value > self.lsc else "abaixo do LIC"
                self.violations['rule1'].append({
                    'position': position,
                    'value': value,
                    'description': f"Ponto {position}: {value:.4f} ({side})"
                })
    
    def rule2_two_of_three_beyond_2sigma(self):

        for i in range(len(self.data) - 2):
            window = self.data.iloc[i:i+3] if hasattr(self.data, 'iloc') else self.data[i:i+3]
            
            
            upper_violations = sum(1 for v in window if v > self.zone_a_upper)
            if upper_violations >= 2:
                positions = [i+1+j for j, v in enumerate(window) if v > self.zone_a_upper]
                self.violations['rule2'].append({
                    'positions': positions,
                    'description': f"Pontos {positions}: 2 de 3 pontos consecutivos acima de +2σ ({self.zone_a_upper:.4f})"
                })
            
            
            lower_violations = sum(1 for v in window if v < self.zone_a_lower)
            if lower_violations >= 2:
                positions = [i+1+j for j, v in enumerate(window) if v < self.zone_a_lower]
                self.violations['rule2'].append({
                    'positions': positions,
                    'description': f"Pontos {positions}: 2 de 3 pontos consecutivos abaixo de -2σ ({self.zone_a_lower:.4f})"
                })
    
    def rule3_four_of_five_beyond_1sigma(self):
        
        for i in range(len(self.data) - 4):
            window = self.data.iloc[i:i+5] if hasattr(self.data, 'iloc') else self.data[i:i+5]
            
            
            upper_violations = sum(1 for v in window if v > self.zone_b_upper)
            if upper_violations >= 4:
                positions = [i+1+j for j, v in enumerate(window) if v > self.zone_b_upper]
                self.violations['rule3'].append({
                    'positions': positions,
                    'description': f"Pontos {positions}: 4 de 5 pontos consecutivos acima de +1σ ({self.zone_b_upper:.4f})"
                })
            
           
            lower_violations = sum(1 for v in window if v < self.zone_b_lower)
            if lower_violations >= 4:
                positions = [i+1+j for j, v in enumerate(window) if v < self.zone_b_lower]
                self.violations['rule3'].append({
                    'positions': positions,
                    'description': f"Pontos {positions}: 4 de 5 pontos consecutivos abaixo de -1σ ({self.zone_b_lower:.4f})"
                })
    
    def rule4_eight_consecutive_same_side(self):
        
        for i in range(len(self.data) - 7):
            window = self.data.iloc[i:i+8] if hasattr(self.data, 'iloc') else self.data[i:i+8]
            
            
            all_above = all(v > self.lc for v in window)
            if all_above:
                positions = list(range(i+1, i+9))
                self.violations['rule4'].append({
                    'positions': positions,
                    'description': f"Pontos {positions[0]}-{positions[-1]}: 8 pontos consecutivos acima da LC ({self.lc:.4f})"
                })
            
            
            all_below = all(v < self.lc for v in window)
            if all_below:
                positions = list(range(i+1, i+9))
                self.violations['rule4'].append({
                    'positions': positions,
                    'description': f"Pontos {positions[0]}-{positions[-1]}: 8 pontos consecutivos abaixo da LC ({self.lc:.4f})"
                })
    
def analyze_xr_chart(xr_graph_instance):
    
    analyzer_x = WesternElectricAnalyzer(
        data=xr_graph_instance.df['X_bar'],
        lc=xr_graph_instance.x_double_mean,
        lsc=xr_graph_instance.lsc_x_bar_graph,
        lic=xr_graph_instance.lic_x_bar_graph,
        chart_name="Gráfico X-barra"
    )
    analyzer_x.analyze_all_rules()

    analyzer_r = WesternElectricAnalyzer(
        data=xr_graph_instance.df['R'],
        lc=xr_graph_instance.r_mean,
        lsc=xr_graph_instance.lsc_r_bar_graph,
        lic=xr_graph_instance.lic_r_bar_graph,
        chart_name="Gráfico R"
    )
    analyzer_r.analyze_all_rules()



def analyze_x_chart(x_graph_instance):

    analyzer_x = WesternElectricAnalyzer(
        data=x_graph_instance.df['Valor'],
        lc=x_graph_instance.x_mean,
        lsc=x_graph_instance.lsc_x_graph,
        lic=x_graph_instance.lic_x_graph,
        chart_name="Gráfico X (Medidas Individuais)"
    )
    analyzer_x.analyze_all_rules()

