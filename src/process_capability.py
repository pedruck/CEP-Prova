
from scipy import stats


class ProcessCapability:
    
    def __init__(self, sigma, lse=None, lie=None, target=None):

        self.sigma = sigma
        self.lse = lse
        self.lie = lie
        self.target = target
        
        
        self.rcp = None
        self.rcpk = None
        self.rcps = None  
        self.rcpi = None  
        self.process_mean = None
        
    def set_process_mean(self, mean):

        self.process_mean = mean
        
    def calculate_rcp(self):

        if self.lse is None or self.lie is None:
            print("[WARNING]: LSE e LIE não definidos. Não é possível calcular RCP.")
            return None
        
        if self.sigma == 0:
            print("[WARNING]: Sigma é zero. Não é possível calcular RCP.")
            return None

        self.rcp = abs((self.lse - self.lie) / (6 * self.sigma))
        return self.rcp
    
    def calculate_rcpk(self):
        
        if self.process_mean is None:
            print("[WARNING]: Média do processo não definida. Não é possível calcular RCPk.")
            return None
            
        if self.lse is None or self.lie is None:
            print("[WARNING]: LSE e LIE não definidos. Não é possível calcular RCPk.")
            return None
        
        if self.sigma == 0:
            print("[WARNING]: Sigma é zero. Não é possível calcular RCPk.")
            return None
        
        
        self.rcps = (self.lse - self.process_mean) / (3 * self.sigma)
        self.rcpi = (self.process_mean - self.lie) / (3 * self.sigma)


        self.rcpk = abs(min(self.rcps, self.rcpi))

        return self.rcpk
    
    def calculate_all(self):

        self.calculate_rcp()
        self.calculate_rcpk()
        
        return {
            'rcp': self.rcp,
            'rcpk': self.rcpk,
            'rcps': self.rcps,
            'rcpi': self.rcpi,
            'sigma': self.sigma,
            'mean': self.process_mean,
            'lse': self.lse,
            'lie': self.lie
        }
    
    def interpret_rcp(self):

        if self.rcp is None:
            return "Não calculado"
        
        if self.rcp >= 1.33:
            return "[INFO]: Processo CAPAZ (RCP ≥ 1.33)"
        elif self.rcp >= 1.00:
            return "[WARNING]:Processo ACEITÁVEL (1.00 ≤ RCP < 1.33)"
        else:
            return "[ERROR]: Processo INCAPAZ (RCP < 1.00)"

    def interpret_rcpk(self):

        if self.rcpk is None:
            return "Não calculado"
        
        centered = None
        if self.lse is not None and self.lie is not None and self.process_mean is not None:
            midpoint = (self.lse + self.lie) / 2
            spec_width = (self.lse - self.lie)
            if spec_width != 0:
                centered = abs(self.process_mean - midpoint) <= 0.1 * spec_width
        
        if self.rcpk >= 1.33:
            if centered is True:
                return "[INFO]: Processo CAPAZ e CENTRADO (RCPk ≥ 1.33)"
            elif centered is False:
                return "[INFO]: Processo CAPAZ porém DESCENTRADO (RCPk ≥ 1.33)"
            else:
                return "[INFO]: Processo CAPAZ (RCPk ≥ 1.33)"
        elif self.rcpk >= 1.00:
            if centered is False:
                return "[WARNING]: Processo ACEITÁVEL porém DESCENTRADO (1.00 ≤ RCPk < 1.33)"
            else:
                return "[WARNING]: Processo ACEITÁVEL (1.00 ≤ RCPk < 1.33)"
        else:
            return "[ERROR]: Processo INCAPAZ ou DESCENTRADO (RCPk < 1.00)"
    
    def calculate_success_probability(self):

        if self.process_mean is None or self.sigma is None or self.sigma == 0:
            return None
        
        if self.lse is None or self.lie is None:
            return None
        
        try:
            
            z_upper = (self.lse - self.process_mean) / self.sigma
            z_lower = (self.lie - self.process_mean) / self.sigma
            

            
            prob_upper = stats.norm.cdf(z_upper)
            prob_lower = stats.norm.cdf(z_lower)
            
            success_probability = (prob_upper - prob_lower) * 100
            return success_probability
        except Exception as e:
            print(f"[WARNING]: Erro ao calcular probabilidade de sucesso: {e}")
            return None


def calculate_capability(instance, lse, lie, target=None, type_chart="X-R"):

    capability = ProcessCapability(
        sigma=instance.sigma,
        lse=lse,
        lie=lie,
        target=target
    )
    
    
    if type_chart == "X-R":
        capability.set_process_mean(instance.x_double_mean)
    elif type_chart == "X":
        capability.set_process_mean(instance.x_mean)
    else:
        return None

    
    capability.calculate_all()
    
    
    
    return capability


def calculate_capability_x(x_instance, lse, lie, target=None):

    capability = ProcessCapability(
        sigma=x_instance.sigma,
        lse=lse,
        lie=lie,
        target=target
    )
    
    
    capability.set_process_mean(x_instance.x_mean)
    
    
    capability.calculate_all()
    
    
    
    return capability
