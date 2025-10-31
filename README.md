# CEP-Math

Sistema para Análise Estatística de Processos Industriais (CEP)

## OBSERVAÇÕES RELACIONADAS A PROVA:
- todos os htmls da resolução da prova estão dentro do /src
- resolução da questão 3: relatorio_problema_cep.html
- resolução da questão 2.3:
relatório_cep_xr(QUESTAO 2.3)
- resolução das demais questões: 
relatório_cep_xr(LIMITES DE ESPECIFICAÇÃO NORMAL)
- A resolução da 2.3 foi feita alterando os limites de especificação do grafico XR que são passados como parâmetros em xr.set_especification_limits()


## Funcionalidades Principais
- Geração de gráficos de controle X-barra, R, X (individuais), P e U
- Análise automática de estabilidade (Regras Western Electric)
- Cálculo de índices de capacidade do processo (RCP, RCPk, etc.)
- Geração de relatórios HTML detalhados e visualmente agradáveis
- Simulação de probabilidades e aceitação de amostras

## Pré-requisitos
- Python 3.8+
- Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Executar

1. **Clone o repositório e acesse a pasta:**
   ```bash
   cd CEP-Math/src
   ```

2. **Execute o arquivo principal:**
   ```bash
   python main.py
   ```

3. **Relatórios Gerados:**
   - O sistema irá gerar arquivos HTML de relatório na pasta `src/` (ex: `relatorio_cep_xr.html`, `relatorio_cep_x.html`, `relatorio_problemas_cep.html`).
   - Abra esses arquivos no navegador para visualizar os resultados.

## Como Usar as Funcionalidades

- **Gráficos de Controle X-R e X:**
  - Os dados de entrada estão em `src/json_files/`.
  - O script `main.py` já está configurado para gerar os gráficos e relatórios automaticamente.

- **Gráficos de Atributos (P e U):**
  - Edite o `main.py` para instanciar `PChart()` ou `UChart()` conforme necessário.

- **Simulação de Probabilidades:**
  - Use métodos da classe `CEP_Problems` para calcular probabilidades e gerar relatórios de simulação.

- **Limites de Especificação:**
  - Altere os valores de LSE/LIE no início do `main.py` para simular diferentes cenários.

## Sobre os Arquivos de Dados JSON

- `dados.json`: Usado para gráficos X-barra e R. Cada item representa uma amostra com uma lista de valores medidos (ex: 5 medições por amostra).
- `dados_individuais.json`: Usado para gráfico X (Individuais). Cada item é uma medição individual.
- `p_chart_data.json`: Usado para gráfico P (proporção de defeituosos). Cada item traz o número de itens inspecionados e quantos foram considerados defeituosos por amostra.
- `u_chart_data.json`: Usado para gráfico U (número de defeitos por unidade). Cada item traz o número de unidades inspecionadas e o total de defeitos encontrados por amostra.
- `constantes_cep.json`: Tabela de constantes estatísticas para cálculo dos limites de controle, indexada pelo tamanho da amostra.

## Observações
- Os relatórios são gerados automaticamente após a execução do `main.py`.
- Para personalizar os dados, edite os arquivos JSON em `src/json_files/`.
- Para dúvidas ou sugestões, consulte o código-fonte ou abra uma issue.

---

**Desenvolvido por: [Seu Nome/Equipe]**
