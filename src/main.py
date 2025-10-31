from x_r_graphs import XR_graph
from x_graph import X_graph
from attributes_charts import PChart, UChart
from process_capability import calculate_capability
from CEP_Problems import CEP_Problems
if __name__ == "__main__":
    
    LSE_XR = 4.94
    LIE_XR = 4.952

    xr = XR_graph()
   
    xr.set_specification_limits(LSE_XR, LIE_XR)
    xr.analyze_control_status()  
    
    calculate_capability(xr, lse=LSE_XR, lie=LIE_XR, type_chart="X-R")
    
   # x = X_graph()
    
   # x.set_specification_limits(LSE_X, LIE_X)
   # x.analyze_control_status() 
   # calculate_capability(x, lse=LSE_X, lie=LIE_X, type_chart="X")

   # p = PChart()
   # u = UChart()

        

    p_aceitacao, p_aproveitar = CEP_Problems.cep_probabilidade(
        sigma_xbar=1,
        sigma=1.5, 
        n=9, 
        k_lim=3, 
        N=10, 
        minimo_aceitos=8
    )
    
    
    html_problems = CEP_Problems.generate_problems_report(
        p_aceitacao=p_aceitacao,
        p_aproveitar=p_aproveitar,
        sigma_deslocamento=1.5, 
        n=9, 
        k_lim=3, 
        N=10, 
        minimo_aceitos=8
    )
    
    with open('relatorio_problemas_cep.html', 'w', encoding='utf-8') as f:
        f.write(html_problems)
    
    print("[INFO]: Relatório de Problemas CEP gerado: relatorio_problemas_cep.html")

    #@staticmethod
    #def rcp(lse, lie, qualidade_sigma, variancia):
    #    return (lse - lie) / (qualidade_sigma * variancia)

   # @staticmethod
    #def rcp_k(lse, lie, qualidade_sigma, x_barrabarra, variancia):
    #    return [(lse - x_barrabarra) / (qualidade_sigma  * variancia), (x_barrabarra - lie) / (qualidade_sigma * variancia)]
    