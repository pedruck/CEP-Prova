from abc import ABC
import math
from scipy.stats import norm, binom

class CEP_Problems(ABC):
    
    def cep_probabilidade(sigma_xbar, sigma, n, k_lim, N, minimo_aceitos):
        
        mu0 = 0
        mu1 = mu0 + sigma
        
        LCL = mu0 - k_lim * sigma_xbar
        UCL = mu0 + k_lim * sigma_xbar
        Z_LCL = (LCL - mu1) / sigma_xbar
        Z_UCL = (UCL - mu1) / sigma_xbar
        p_aceitacao = norm.cdf(Z_UCL) - norm.cdf(Z_LCL)
        p_aproveitar = 1 - binom.cdf(minimo_aceitos - 1, N, p_aceitacao)
        return p_aceitacao, p_aproveitar

    @staticmethod
    def generate_problems_report( p_aceitacao=None, p_aproveitar=None, sigma_deslocamento=None, n=None, k_lim=None, N=None, minimo_aceitos=None):
        from datetime import datetime
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Problemas CEP</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body class="bg-gray-50 text-gray-900">
<div class="container mx-auto px-4 py-8 max-w-6xl">

    <div class="bg-white shadow-md rounded-lg p-6 mb-6">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-2">
            Relatório de Problemas - Controle Estatístico de Processo
        </h1>
        <p class="text-center text-sm text-gray-500">Gerado em: {report_date}</p>
    </div>
"""

        if p_aceitacao is not None and p_aproveitar is not None:
            p_aceitacao_pct = p_aceitacao * 100
            p_aproveitar_pct = p_aproveitar * 100
            html_content += f"""
    <div class="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4 border-b pb-2">
            Probabilidade de Aproveitar Amostras
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Parâmetros do Processo</h3>
                <div class="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Deslocamento (σ):</span>
                        <span class="font-mono font-bold">{sigma_deslocamento}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Tamanho da Amostra (n):</span>
                        <span class="font-mono font-bold">{n}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Limite de Controle (k):</span>
                        <span class="font-mono font-bold">{k_lim}σ</span>
                    </div>
                    <div class="flex justify-between border-t pt-2">
                        <span class="text-gray-600">Total de Amostras (N):</span>
                        <span class="font-mono font-bold text-purple-600">{N}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Mínimo Desejado:</span>
                        <span class="font-mono font-bold text-purple-600">{minimo_aceitos}</span>
                    </div>
                </div>
            </div>
            <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Resultados</h3>
                <div class="space-y-3">
                    <div class="bg-blue-50 border-l-4 border-blue-600 rounded-lg p-4">
                        <p class="text-blue-800 text-sm mb-1">Probabilidade de Aceitação por Amostra:</p>
                        <p class="text-3xl font-bold text-blue-600">{p_aceitacao_pct:.2f}%</p>
                    </div>
                    <div class="bg-green-50 border-l-4 border-green-600 rounded-lg p-4">
                        <p class="text-green-800 text-sm mb-1">Probabilidade de Aproveitar ≥ {minimo_aceitos} de {N}:</p>
                        <p class="text-3xl font-bold text-green-600">{p_aproveitar_pct:.2f}%</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
"""
        html_content += """
    <div class="text-center text-gray-500 text-sm mt-8 py-4 border-t">
        <p>Relatório gerado automaticamente pelo Sistema CEP-Math</p>
        <p class="text-xs mt-1">© 2025 - Controle Estatístico de Processo</p>
    </div>

</div>

</body>
</html>
"""
        return html_content

