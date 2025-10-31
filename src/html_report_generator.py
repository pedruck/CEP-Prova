import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import base64


@dataclass
class ProcessInfo:
    n_samples: int
    sample_size: int
    sigma: float
    total_observations: int = 0
    


@dataclass
class ControlLimits:
    center_line: float
    upper_control_limit: float
    lower_control_limit: float
    center_line_label: str = "LC"
    ucl_label: str = "LSC"
    lcl_label: str = "LIC"


@dataclass
class WesternElectricResult:
    violations: Dict[str, List[Dict]] = field(default_factory=lambda: {
        'rule1': [], 'rule2': [], 'rule3': [], 'rule4': []
    })
    chart_name: str = ""
    state: str = ""


@dataclass
class CapabilityResult:
    lse: float
    lie: float
    process_mean: float
    sigma: float
    rcp: float
    rcpk: float
    rcps: float
    rcpi: float
    rcp_interpretation: str
    rcpk_interpretation: str
    centralization_pct: float
    is_centered: bool
    success_probability: float = 0.0


@dataclass
class XRReportData:
    df: pd.DataFrame
    x_mean: float
    r_mean: float
    sigma: float
    x_control_limits: ControlLimits
    r_control_limits: ControlLimits
    out_of_control_x: pd.DataFrame
    out_of_control_r: pd.DataFrame
    western_electric_x: WesternElectricResult
    western_electric_r: WesternElectricResult
    process_info: ProcessInfo
    capability: Optional[CapabilityResult] = None
    image_base64: str = ""


@dataclass
class XReportData:

    df: pd.DataFrame
    x_mean: float
    sigma: float
    x_control_limits: ControlLimits
    out_of_control_x: pd.DataFrame
    western_electric_x: WesternElectricResult
    process_info: ProcessInfo
    capability: Optional[CapabilityResult] = None
    image_base64: str = ""


class CEPReportGeneratorTailwind:
    
    def __init__(self, chart_type="XR"):
        self.chart_type = chart_type
        self.report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def encode_image(self, image_path):
        
        try:
            with open(image_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"[WARNING] Erro ao codificar imagem: {e}")
            return ""
    
    def _get_html_head(self, title: str) -> str:
        
        return f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{title}</title>
    <script src=\"https://cdn.tailwindcss.com\"></script>
    <style>
        .font-mono {{ font-family: monospace; }}
    </style>
</head>
<body class=\"bg-white text-gray-900 p-4\">
"""
    
    def _get_html_footer(self) -> str:
        
        return f"""
<footer class=\"mt-8 text-sm text-gray-600\">
    <p>Relatório CEP gerado automaticamente.</p>
</footer>
</body>
</html>
"""
    
    def _render_header(self, chart_type: str) -> str:
        
        chart_description = {
            "XR": "Gráficos de Controle X-barra e R",
            "X": "Gráficos de Controle X (Medidas Individuais)"
        }.get(chart_type, chart_type)
        
        return f"""
<div class=\"mb-8\">
    <h1 class=\"text-2xl font-bold\">Relatório de Controle Estatístico de Processo</h1>
    <h2 class=\"text-xl font-semibold\">{chart_description}</h2>
    <p class=\"text-gray-700\">Gerado em: {self.report_date}</p>
</div>
"""
    
    def _render_process_info(self, info: ProcessInfo) -> str:
        
        return f"""
<div class=\"mb-8 p-4 border rounded-lg shadow-sm bg-gray-50\">
    <h2 class=\"text-lg font-semibold mb-4\">Informações do Processo</h2>
    <div class=\"grid grid-cols-1 sm:grid-cols-2 gap-4\">
        <div>
            <strong>Número de Amostras:</strong> {info.n_samples}
        </div>
        <div>
            <strong>Tamanho da Amostra:</strong> {info.sample_size}
        </div>
        <div>
            <strong>Sigma (σ):</strong> {info.sigma:.4f}
        </div>
        
    </div>
</div>
"""
    
    def _render_control_limits(self, limits: ControlLimits, chart_name: str) -> str:
        
        return f"""
<div class=\"mb-4\">
    <h3 class=\"text-lg font-semibold mb-2\">{chart_name}</h3>
    <table class=\"min-w-full bg-white border rounded-lg overflow-hidden\">
        <thead>
            <tr class=\"text-gray-700 bg-gray-100\">
                <th class=\"py-2 px-4 border-b\">{limits.center_line_label}</th>
                <th class=\"py-2 px-4 border-b\">Valor</th>
                <th class=\"py-2 px-4 border-b\">Descrição</th>
            </tr>
        </thead>
        <tbody>
            <tr class=\"text-gray-700\">
                <td class=\"py-2 px-4 border-b\">{limits.center_line_label}</td>
                <td class=\"py-2 px-4 border-b font-mono\">{limits.center_line:.4f}</td>
                <td class=\"py-2 px-4 border-b\">Linha Central</td>
            </tr>
            <tr class=\"text-gray-700\">
                <td class=\"py-2 px-4 border-b\">{limits.ucl_label}</td>
                <td class=\"py-2 px-4 border-b font-mono\">{limits.upper_control_limit:.4f}</td>
                <td class=\"py-2 px-4 border-b\">Limite Superior de Controle</td>
            </tr>
            <tr class=\"text-gray-700\">
                <td class=\"py-2 px-4 border-b\">{limits.lcl_label}</td>
                <td class=\"py-2 px-4 border-b font-mono\">{limits.lower_control_limit:.4f}</td>
                <td class=\"py-2 px-4 border-b\">Limite Inferior de Controle</td>
            </tr>
        </tbody>
    </table>
</div>
"""
    
    def _render_chart_image(self, image_base64: str) -> str:
        
        if not image_base64:
            return '<div class="p-4 mb-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700" role="alert">Imagem do gráfico não disponível</div>'
        
        return f"""
<div class=\"mb-8\">
    <h2 class=\"text-lg font-semibold mb-4\">Gráficos de Controle</h2>
    <div class=\"flex justify-center\">\n        <img src=\"{image_base64}\" alt=\"Gráficos de Controle\" class=\"max-w-full h-auto border rounded-lg shadow-sm\">\n    </div>
</div>
"""
    
    def _render_western_electric_rules(self, result: WesternElectricResult) -> str:
       
        rule_names = {
            'rule1': 'Pontos além dos limites de controle (3σ)',
            'rule2': 'Dois de três pontos consecutivos além de 2σ',
            'rule3': 'Quatro de cinco pontos consecutivos além de 1σ',
            'rule4': 'Oito pontos consecutivos no mesmo lado da LC'
        }
        
        total_violations = sum(len(v) for v in result.violations.values())
        # Determine and show state prominently
        state_value = result.state if result.state else ("estavel" if total_violations == 0 else "instavel")
        is_stable = state_value == "estavel"
        state_bg = "bg-green-50" if is_stable else "bg-red-50"
        state_border = "border-green-400" if is_stable else "border-red-400"
        state_text = "text-green-700" if is_stable else "text-red-700"
        state_label = "Estado do processo: " + state_value
        
        html = f"""
<div class=\"mb-4\">
    <h3 class=\"text-lg font-semibold mb-2\">{result.chart_name}</h3>
    <div class=\"{state_bg} {state_text} border-l-4 {state_border} p-3 rounded mb-3\">{state_label}</div>
    <table class=\"min-w-full bg-white border overflow-hidden\">
        <thead>
            <tr class=\"text-gray-700 bg-gray-100\">\n                <th class=\"py-2 px-4 border-b\">Regra</th>
                <th class=\"py-2 px-4 border-b\">Status</th>
                <th class=\"py-2 px-4 border-b\">Violações</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for i, (rule_key, rule_name) in enumerate(rule_names.items(), 1):
            violations = result.violations.get(rule_key, [])
            status_text = 'FALHOU' if len(violations) > 0 else 'PASSOU'
            status_color = 'red' if len(violations) > 0 else 'green'
            row_bg = '#f9f9f9' if i % 2 == 0 else ''
            html += f"""
            <tr style=\"{row_bg};\" class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b\"><strong>Regra {i}:</strong> {rule_name}</td>
                <td class=\"py-2 px-4 border-b text-center\" style=\"color: {status_color}; font-weight: bold;\">{status_text}</td>
                <td class=\"py-2 px-4 border-b text-center font-mono\">{len(violations)}</td>
            </tr>
"""
        html += """
        </tbody>
    </table>
"""
        if total_violations == 0:
            html += f"""
    <div class=\"p-4 mt-4 bg-green-50 border-l-4 border-green-400 text-green-700\" role=\"alert\">\n        <p class=\"font-semibold\">Nenhuma violação detectada no {result.chart_name}</p>
    </div>
"""
        else:
            html += f"""
    <div class=\"p-4 mt-4 bg-red-50 border-l-4 border-red-400 text-red-700\" role=\"alert\">\n        <p class=\"font-semibold mb-2\">{total_violations} violação(ões) detectada(s) no {result.chart_name}</p>
        <ul class=\"list-disc pl-5\">
"""
            for rule_key, violations in result.violations.items():
                rule_number = rule_key.replace('rule', '')
                for v in violations:
                    html += f'            <li><strong>Regra {rule_number}:</strong> {v["description"]}</li>\n'
            html += """
        </ul>
    </div>
"""
        html += "</div>\n"
        return html
    
    def _render_capability_analysis(self, capability: CapabilityResult) -> str:
        cap_status_color = "green" if capability.rcpk >= 1.33 else "red"
        cap_status_bg = f"bg-{cap_status_color}-50"
        cap_status_border = f"border-{cap_status_color}-500"
        cap_status_text = f"text-{cap_status_color}-800"
        central_pct = abs(capability.centralization_pct)
        success_pct = abs(capability.success_probability)
        return f"""
<div class=\"mb-8 p-4 border rounded-lg shadow-sm bg-gray-50\">\n    <h2 class=\"text-lg font-semibold mb-4\">Análise de Capacidade do Processo (RCP)</h2>
    <h3 class=\"text-md font-semibold mb-2\">Parâmetros do Processo</h3>
    <table class=\"min-w-full bg-white border rounded-lg overflow-hidden\">\n        <thead>
            <tr class=\"text-gray-700 bg-gray-100\">\n                <th class=\"py-2 px-4 border-b\">Parâmetro</th>
                <th class=\"py-2 px-4 border-b\">Valor</th>
                <th class=\"py-2 px-4 border-b\">Interpretação</th>
            </tr>
        </thead>
        <tbody>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b\">LSE (Limite Superior de Especificação)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.lse:.6f}</td>
                <td class=\"py-2 px-4 border-b\">Especificação do cliente</td>
            </tr>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b\">LIE (Limite Inferior de Especificação)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.lie:.6f}</td>
                <td class=\"py-2 px-4 border-b\">Especificação do cliente</td>
            </tr>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b\">Média do Processo (μ)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.process_mean:.6f}</td>
                <td class=\"py-2 px-4 border-b\">Valor central do processo</td>
            </tr>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b\">Sigma (σ)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.sigma:.6f}</td>
                <td class=\"py-2 px-4 border-b\">Variabilidade do processo</td>
            </tr>
        </tbody>
    </table>
    <h3 class=\"text-md font-semibold mt-4 mb-2\">Índices de Capacidade</h3>
    <table class=\"min-w-full bg-white border rounded-lg overflow-hidden\">\n        <thead>
            <tr class=\"text-gray-700 bg-gray-100\">\n                <th class=\"py-2 px-4 border-b\">Índice</th>
                <th class=\"py-2 px-4 border-b\">Valor</th>
                <th class=\"py-2 px-4 border-b\">Status</th>
            </tr>
        </thead>
        <tbody>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b font-semibold\">RCP (Capacidade Potencial)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.rcp:.4f}</td>
                <td class=\"py-2 px-4 border-b\">{capability.rcp_interpretation}</td>
            </tr>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b font-semibold\">RCPk (Capacidade Real)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.rcpk:.4f}</td>
                <td class=\"py-2 px-4 border-b\">{capability.rcpk_interpretation}</td>
            </tr>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b font-semibold\">RCPs (Capacidade Superior)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.rcps:.4f}</td>
                <td class=\"py-2 px-4 border-b\">(LSE - μ) / (3σ)</td>
            </tr>
            <tr class=\"text-gray-700\">\n                <td class=\"py-2 px-4 border-b font-semibold\">RCPi (Capacidade Inferior)</td>
                <td class=\"py-2 px-4 border-b font-mono\">{capability.rcpi:.4f}</td>
                <td class=\"py-2 px-4 border-b\">(μ - LIE) / (3σ)</td>
            </tr>
        </tbody>
    </table>
    <div class=\"{cap_status_bg} {cap_status_border} p-4 rounded-lg mt-4\">\n        <h3 class=\"font-semibold {cap_status_text}\">Conclusão da Capacidade</h3>
        <p class=\"{cap_status_text} mb-2\"><strong>RCP:</strong> {capability.rcp_interpretation}</p>
        <p class=\"{cap_status_text} mb-2\"><strong>RCPk:</strong> {capability.rcpk_interpretation}</p>
        <p class=\"{cap_status_text} mb-2\">\n            <strong>Centralização:</strong> {central_pct:.1f}% 
            {'(Processo bem centrado)' if capability.is_centered else '(Processo descentrado)'}
        </p>
        <p class=\"{cap_status_text}\">\n            <strong>Probabilidade de Sucesso:</strong> {success_pct:.2f}% 
            (itens dentro dos limites de especificação)
        </p>
    </div>
</div>
"""
    
    def _render_data_table_xr(self, df: pd.DataFrame, lsc_x: float, lic_x: float, lsc_r: float) -> str:
        
        html = """
<div class=\"mb-8\">
    <h2 class=\"text-lg font-semibold mb-4\">Dados Completos</h2>
    <div class=\"overflow-x-auto\">
        <table class=\"min-w-full bg-white border rounded-lg overflow-hidden\">
            <thead>
                <tr class=\"text-gray-700 bg-gray-100\">
                    <th class=\"py-2 px-4 border-b\">Amostra</th>
                    <th class=\"py-2 px-4 border-b\">X̄ (Média)</th>
                    <th class=\"py-2 px-4 border-b\">R (Range)</th>
                    <th class=\"py-2 px-4 border-b\">Status X̄</th>
                    <th class=\"py-2 px-4 border-b\">Status R</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for idx, row in df.iterrows():
            x_out = row['X_bar'] > lsc_x or row['X_bar'] < lic_x
            r_out = row['R'] > lsc_r
            
            x_status = "Fora" if x_out else "OK"
            r_status = "Fora" if r_out else "OK"
            
            x_class = "bg-red-50 font-bold" if x_out else ""
            r_class = "bg-red-50 font-bold" if r_out else ""
            row_bg = "bg-gray-50" if idx % 2 == 0 else ""
            
            html += f"""
                <tr style=\"{row_bg}\" class=\"text-gray-700\">
                    <td class=\"py-2 px-4 border-b\">{row['Amostra']}</td>
                    <td class=\"py-2 px-4 border-b font-mono {x_class}\">{row['X_bar']:.4f}</td>
                    <td class=\"py-2 px-4 border-b font-mono {r_class}\">{row['R']:.4f}</td>
                    <td class=\"py-2 px-4 border-b text-center\">{x_status}</td>
                    <td class=\"py-2 px-4 border-b text-center\">{r_status}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</div>
"""
        return html
    
    def _render_data_table_x(self, df: pd.DataFrame, lsc_x: float, lic_x: float) -> str:
       
        id_column = "Medida" if "Medida" in df.columns else "Amostra"
        
        html = """
<div class=\"mb-8\">
    <h2 class=\"text-lg font-semibold mb-4\">Dados Completos</h2>
    <div class=\"overflow-x-auto\">
        <table class=\"min-w-full bg-white border rounded-lg overflow-hidden\">
            <thead>
                <tr class=\"text-gray-700 bg-gray-100\">
                    <th class=\"py-2 px-4 border-b\">Medida</th>
                    <th class=\"py-2 px-4 border-b\">Valor</th>
                    <th class=\"py-2 px-4 border-b\">Status</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for idx, row in df.iterrows():
            x_out = row['Valor'] > lsc_x or row['Valor'] < lic_x
            status = "Fora" if x_out else "OK"
            x_class = "bg-red-50 font-bold" if x_out else ""
            row_bg = "bg-gray-50" if idx % 2 == 0 else ""
            id_value = row[id_column]
            
            html += f"""
                <tr style=\"{row_bg}\" class=\"text-gray-700\">
                    <td class=\"py-2 px-4 border-b\">{id_value}</td>
                    <td class=\"py-2 px-4 border-b font-mono {x_class}\">{row['Valor']:.4f}</td>
                    <td class=\"py-2 px-4 border-b text-center\">{status}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</div>
"""
        return html
    
    def generate_xr_report(self, data: XRReportData, output_file: str = "relatorio_cep_xr.html") -> str:
        
        html = self._get_html_head("Relatório CEP - Gráficos X-R")
        html += '<div class="container">\n'
        
        # Header
        html += self._render_header("XR")
        
        # Process Info
        html += self._render_process_info(data.process_info)
        
        # Control Limits
        html += '<div class="mb-8">\n'
        html += '<h2 class="text-lg font-semibold mb-4">Limites de Controle</h2>\n'
        html += self._render_control_limits(data.x_control_limits, "Gráfico X-barra")
        html += self._render_control_limits(data.r_control_limits, "Gráfico R")
        html += '</div>\n'
        
        # Chart Image
        html += self._render_chart_image(data.image_base64)
        
        # Western Electric Rules (shows process state banner inside)
        html += '<div class="mb-8">\n'
        html += '<h2 class="text-lg font-semibold mb-4">Análise de Conformidade - Regras Western Electric</h2>\n'
        html += self._render_western_electric_rules(data.western_electric_x)
        html += self._render_western_electric_rules(data.western_electric_r)
        html += '</div>\n'
        
        # Capability Analysis
        if data.capability:
            html += self._render_capability_analysis(data.capability)
        
        # Data Table
        html += self._render_data_table_xr(
            data.df,
            data.x_control_limits.upper_control_limit,
            data.x_control_limits.lower_control_limit,
            data.r_control_limits.upper_control_limit
        )
        
        html += self._get_html_footer()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[INFO] Relatório HTML gerado: {output_file}")
        return output_file
    
    def generate_x_report(self, data: XReportData, output_file: str = "relatorio_cep_x.html") -> str:
        """Gera relatório HTML para gráficos X (individuais) usando dataclass"""
        html = self._get_html_head("Relatório CEP - Gráficos X")
        html += '<div class="container">\n'
        
        
        html += self._render_header("X")
        
       
        html += self._render_process_info(data.process_info)
        
        
        html += '<div class="mb-8">\n'
        html += '<h2 class="text-lg font-semibold mb-4">Limites de Controle</h2>\n'
        html += self._render_control_limits(data.x_control_limits, "Gráfico X")
        html += '</div>\n'
        
        
        html += self._render_chart_image(data.image_base64)
        
        
        html += '<div class="mb-8">\n'
        html += '<h2 class="text-lg font-semibold mb-4">Análise de Conformidade - Regras Western Electric</h2>\n'
        html += self._render_western_electric_rules(data.western_electric_x)
        html += '</div>\n'
        
        
        if data.capability:
            html += self._render_capability_analysis(data.capability)
        
        
        html += self._render_data_table_x(
            data.df,
            data.x_control_limits.upper_control_limit,
            data.x_control_limits.lower_control_limit
        )
        
        html += self._get_html_footer()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[INFO] Relatório HTML gerado: {output_file}")
        return output_file
