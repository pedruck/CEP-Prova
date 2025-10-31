import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import base64
import AbstractCEP as AbstractCEP


def _detect_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"Coluna não encontrada. Esperado uma entre: {candidates}")


def _encode_image(image_path):
    try:
        with open(image_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return ""


class PChart(AbstractCEP.AbstractControlChart):
    def __init__(self, df: pd.DataFrame | None = None, data_url: str = "json_files/p_chart_data.json", constants_url: str = "json_files/constantes_cep.json", output_png: str = 'grafico_controle_p.png', output_html: str = 'relatorio_cep_p.html'):
        super().__init__(data_url=data_url, constants_url=constants_url)
        self.output_png = output_png
        self.output_html = output_html
        self.df = df.copy() if df is not None else (self.data.copy() if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data))
        if 'Amostra' not in self.df.columns:
            self.df['Amostra'] = np.arange(1, len(self.df) + 1)
        self.defects_col = _detect_column(self.df, ['Defeituosos', 'Defeitos'])
        self.n_col = _detect_column(self.df, ['Inspecionados', 'Tamanho', 'Unidades'])
        self.pbar = None

        self.process()
        self.png_path = self.plot(self.output_png)
        self.generate_html(self.png_path, self.output_html)


    def compute_proportions(self):
        self.df['p'] = self.df[self.defects_col] / self.df[self.n_col]

    def compute_center(self):
        total_defects = self.df[self.defects_col].sum()
        total_units = self.df[self.n_col].sum()
        self.pbar = (total_defects / total_units) if total_units > 0 else 0.0

    def compute_limits(self):
        if 'p' not in self.df.columns:
            self.compute_proportions()
        if self.pbar is None:
            self.compute_center()
        n_i = self.df[self.n_col].to_numpy(dtype=float)
        sigma_pi = np.sqrt(np.maximum(self.pbar * (1 - self.pbar) / np.maximum(n_i, 1.0), 0.0))
        self.df['UCL'] = self.pbar + 3 * sigma_pi
        self.df['LCL'] = np.maximum(self.pbar - 3 * sigma_pi, 0.0)
        self.df['LC'] = self.pbar

    def analyze_control_status(self):
        if 'UCL' not in self.df.columns or 'LCL' not in self.df.columns:
            self.compute_limits()
        self.df['Fora'] = (self.df['p'] > self.df['UCL']) | (self.df['p'] < self.df['LCL'])
        out = self.df[self.df['Fora']]
        return {
            'total': len(self.df),
            'out_of_control': len(out),
            'indices': out['Amostra'].tolist(),
            'pbar': self.pbar if self.pbar is not None else 0.0
        }
        

    def process(self):
        self.compute_proportions()
        self.compute_center()
        self.compute_limits()
        return self.analyze_control_status()

    def plot(self, output_png: str = 'grafico_controle_p.png'):
        if 'UCL' not in self.df.columns:
            self.compute_limits()
        x = self.df['Amostra']
        plt.figure(figsize=(16, 8))
        plt.plot(x, self.df['p'], 'bo-', linewidth=2, markersize=6, label='p')
        plt.plot(x, self.df['LC'], color='green', linestyle='-', linewidth=2, label=f'LC = {self.pbar:.4f}')
        plt.plot(x, self.df['UCL'], color='red', linestyle='--', linewidth=2, label='LSC')
        plt.plot(x, self.df['LCL'], color='red', linestyle='--', linewidth=2, label='LIC')
        plt.xlabel('Amostra', fontsize=12)
        plt.ylabel('Proporção defeituosa (p)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper right', fontsize=10)
        plt.tight_layout()
        plt.savefig(output_png, dpi=300, bbox_inches='tight')
        plt.close()
        return output_png

    def analyze(self):
        return self.analyze_control_status()

    def generate_html(self, image_path: str, output_file: str = 'relatorio_cep_p.html'):
        analysis = self.analyze_control_status()
        img_b64 = _encode_image(image_path)
        report_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        html = f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>Relatório CEP - Gráfico P</title>
<script src=\"https://cdn.tailwindcss.com\"></script>
</head>
<body class=\"bg-white text-gray-900 p-4\">
<div class=\"mb-8\">
  <h1 class=\"text-2xl font-bold\">Relatório CEP - Gráfico P</h1>
  <p class=\"text-gray-700\">Gerado em: {report_date}</p>
</div>
<div class=\"mb-8 p-4 border rounded-lg bg-gray-50\">
  <h2 class=\"text-lg font-semibold mb-2\">Resumo</h2>
  <p><strong>p̄:</strong> {self.pbar:.6f}</p>
  <p><strong>Total de amostras:</strong> {analysis['total']}</p>
  <p><strong>Fora de controle:</strong> {analysis['out_of_control']}</p>
</div>
<div class=\"mb-8\">
  <h2 class=\"text-lg font-semibold mb-4\">Gráfico de Controle P</h2>
  {f'<img src="{img_b64}" alt="Gráfico P" class="max-w-full h-auto border rounded"/>' if img_b64 else f'<img src="{image_path}" alt="Gráfico P" class="max-w-full h-auto border rounded"/>'}
</div>
<div class=\"mb-8\">
  <h2 class=\"text-lg font-semibold mb-2\">Dados</h2>
  <div class=\"overflow-x-auto\">
    <table class=\"min-w-full bg-white border rounded\">
      <thead>
        <tr class=\"bg-gray-100 text-gray-700\">
          <th class=\"py-2 px-4 border-b\">Amostra</th>
          <th class=\"py-2 px-4 border-b\">Inspecionados</th>
          <th class=\"py-2 px-4 border-b\">Defeituosos</th>
          <th class=\"py-2 px-4 border-b\">p</th>
          <th class=\"py-2 px-4 border-b\">LSC</th>
          <th class=\"py-2 px-4 border-b\">LC</th>
          <th class=\"py-2 px-4 border-b\">LIC</th>
          <th class=\"py-2 px-4 border-b\">Status</th>
        </tr>
      </thead>
      <tbody>
"""
        for _, row in self.df.iterrows():
            status = 'Fora' if row['Fora'] else 'OK'
            html += f"""
        <tr class=\"text-gray-700\">
          <td class=\"py-2 px-4 border-b\">{int(row['Amostra'])}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{int(row[self.n_col])}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{int(row[self.defects_col])}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['p']:.6f}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['UCL']:.6f}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['LC']:.6f}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['LCL']:.6f}</td>
          <td class=\"py-2 px-4 border-b text-center\">{status}</td>
        </tr>
"""
        html += """
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_file


class UChart(AbstractCEP.AbstractControlChart):
    def __init__(self, df: pd.DataFrame | None = None, data_url: str = "json_files/u_chart_data.json", constants_url: str = "json_files/constantes_cep.json", output_png: str = 'grafico_controle_u.png', output_html: str = 'relatorio_cep_u.html'):
        super().__init__(data_url=data_url, constants_url=constants_url)
        self.output_png = output_png
        self.output_html = output_html
        self.df = df.copy() if df is not None else (self.data.copy() if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data))
        if 'Amostra' not in self.df.columns:
            self.df['Amostra'] = np.arange(1, len(self.df) + 1)
        self.defects_col = _detect_column(self.df, ['Defeitos', 'Não Conformidades', 'NaoConformidades'])
        self.n_col = _detect_column(self.df, ['Inspecionados', 'Unidades', 'Tamanho'])
        self.ubar = None

        self.process()
        self.png_path = self.plot(self.output_png)
        self.generate_html(self.png_path, self.output_html)

    def compute_rates(self):
        self.df['u'] = self.df[self.defects_col] / self.df[self.n_col]

    def compute_center(self):
        total_defects = self.df[self.defects_col].sum()
        total_units = self.df[self.n_col].sum()
        self.ubar = (total_defects / total_units) if total_units > 0 else 0.0

    def compute_limits(self):
        if 'u' not in self.df.columns:
            self.compute_rates()
        if self.ubar is None:
            self.compute_center()
        n_i = self.df[self.n_col].to_numpy(dtype=float)
        sigma_ui = np.sqrt(np.maximum(self.ubar / np.maximum(n_i, 1.0), 0.0))
        self.df['UCL'] = self.ubar + 3 * sigma_ui
        self.df['LCL'] = np.maximum(self.ubar - 3 * sigma_ui, 0.0)
        self.df['LC'] = self.ubar

    def analyze_control_status(self):
        if 'UCL' not in self.df.columns or 'LCL' not in self.df.columns:
            self.compute_limits()
        self.df['Fora'] = (self.df['u'] > self.df['UCL']) | (self.df['u'] < self.df['LCL'])
        out = self.df[self.df['Fora']]
        return {
            'total': len(self.df),
            'out_of_control': len(out),
            'indices': out['Amostra'].tolist(),
            'ubar': self.ubar if self.ubar is not None else 0.0
        }

    def process(self):
        self.compute_rates()
        self.compute_center()
        self.compute_limits()
        return self.analyze_control_status()

    def plot(self, output_png: str = 'grafico_controle_u.png'):
        if 'UCL' not in self.df.columns:
            self.compute_limits()
        x = self.df['Amostra']
        plt.figure(figsize=(16, 8))
        plt.plot(x, self.df['u'], 'bo-', linewidth=2, markersize=6, label='u')
        plt.plot(x, self.df['LC'], color='green', linestyle='-', linewidth=2, label=f'LC = {self.ubar:.4f}')
        plt.plot(x, self.df['UCL'], color='red', linestyle='--', linewidth=2, label='LSC')
        plt.plot(x, self.df['LCL'], color='red', linestyle='--', linewidth=2, label='LIC')
        plt.xlabel('Amostra', fontsize=12)
        plt.ylabel('Não conformidades por unidade (u)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper right', fontsize=10)
        plt.tight_layout()
        plt.savefig(output_png, dpi=300, bbox_inches='tight')
        plt.close()
        return output_png

    def analyze(self):
        return self.analyze_control_status()

    def generate_html(self, image_path: str, output_file: str = 'relatorio_cep_u.html'):
        analysis = self.analyze_control_status()
        img_b64 = _encode_image(image_path)
        report_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        html = f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>Relatório CEP - Gráfico U</title>
<script src=\"https://cdn.tailwindcss.com\"></script>
</head>
<body class=\"bg-white text-gray-900 p-4\">
<div class=\"mb-8\">
  <h1 class=\"text-2xl font-bold\">Relatório CEP - Gráfico U</h1>
  <p class=\"text-gray-700\">Gerado em: {report_date}</p>
</div>
<div class=\"mb-8 p-4 border rounded-lg bg-gray-50\">
  <h2 class=\"text-lg font-semibold mb-2\">Resumo</h2>
  <p><strong>ū:</strong> {self.ubar:.6f}</p>
  <p><strong>Total de amostras:</strong> {analysis['total']}</p>
  <p><strong>Fora de controle:</strong> {analysis['out_of_control']}</p>
</div>
<div class=\"mb-8\">
  <h2 class=\"text-lg font-semibold mb-4\">Gráfico de Controle U</h2>
  {f'<img src="{img_b64}" alt="Gráfico U" class="max-w-full h-auto border rounded"/>' if img_b64 else f'<img src="{image_path}" alt="Gráfico U" class="max-w-full h-auto border rounded"/>'}
</div>
<div class=\"mb-8\">
  <h2 class=\"text-lg font-semibold mb-2\">Dados</h2>
  <div class=\"overflow-x-auto\">
    <table class=\"min-w-full bg-white border rounded\">
      <thead>
        <tr class=\"bg-gray-100 text-gray-700\">
          <th class=\"py-2 px-4 border-b\">Amostra</th>
          <th class=\"py-2 px-4 border-b\">Unidades</th>
          <th class=\"py-2 px-4 border-b\">Não Conformidades</th>
          <th class=\"py-2 px-4 border-b\">u</th>
          <th class=\"py-2 px-4 border-b\">LSC</th>
          <th class=\"py-2 px-4 border-b\">LC</th>
          <th class=\"py-2 px-4 border-b\">LIC</th>
          <th class=\"py-2 px-4 border-b\">Status</th>
        </tr>
      </thead>
      <tbody>
"""
        for _, row in self.df.iterrows():
            status = 'Fora' if row['Fora'] else 'OK'
            html += f"""
        <tr class=\"text-gray-700\">
          <td class=\"py-2 px-4 border-b\">{int(row['Amostra'])}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{int(row[self.n_col])}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{int(row[self.defects_col])}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['u']:.6f}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['UCL']:.6f}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['LC']:.6f}</td>
          <td class=\"py-2 px-4 border-b font-mono\">{row['LCL']:.6f}</td>
          <td class=\"py-2 px-4 border-b text-center\">{status}</td>
        </tr>
"""
        html += """
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_file
