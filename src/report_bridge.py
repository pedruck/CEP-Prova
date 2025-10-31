from html_report_generator import CEPReportGeneratorTailwind, XRReportData, ProcessInfo, ControlLimits, WesternElectricResult, CapabilityResult
from process_capability import ProcessCapability
import pandas as pd


def generate_report_from_instance(instance, chart_type):
    try:
        # Debug: print control values at report time
        if hasattr(instance, 'x_mean') and hasattr(instance, 'sigma') and hasattr(instance, 'lsc_x_graph') and hasattr(instance, 'lic_x_graph'):
            print("[DEBUG] Controle X - No momento do relatório:")
            print(f"  x_mean: {instance.x_mean}")
            print(f"  sigma: {instance.sigma}")
            print(f"  LSC (X): {instance.lsc_x_graph}")
            print(f"  LIC (X): {instance.lic_x_graph}")
       
        generator = CEPReportGeneratorTailwind(chart_type=chart_type)

        
        if chart_type == "XR":
            image_base64 = generator.encode_image('grafico_controle_xr.png')
        elif chart_type == "X":
            image_base64 = generator.encode_image('grafico_controle_x.png')
        else:
            image_base64 = ""

        
        if chart_type == "XR":
            n_size = len([col for col in instance.df.columns if col.startswith('X')])
            process_info = ProcessInfo(
                n_samples=len(instance.df),
                sample_size=n_size,
                sigma=instance.sigma,
                total_observations=len(instance.df) * n_size
            )
        else:
            process_info = ProcessInfo(
                n_samples=len(instance.df),
                sample_size=1,
                sigma=instance.sigma,
                total_observations=len(instance.df)
            )

        
        if chart_type == "XR":
            x_control_limits = ControlLimits(
                center_line=instance.x_double_mean,
                upper_control_limit=instance.lsc_x_bar_graph,
                lower_control_limit=instance.lic_x_bar_graph,
                center_line_label="X̄̄",
                ucl_label="LSC",
                lcl_label="LIC"
            )
            r_control_limits = ControlLimits(
                center_line=instance.r_mean,
                upper_control_limit=instance.lsc_r_bar_graph,
                lower_control_limit=instance.lic_r_bar_graph,
                center_line_label="R̄",
                ucl_label="LSC",
                lcl_label="LIC"
            )
        else:
            x_control_limits = ControlLimits(
                center_line=instance.x_mean,
                upper_control_limit=instance.lsc_x_graph,
                lower_control_limit=instance.lic_x_graph,
                center_line_label="X̄",
                ucl_label="LSC",
                lcl_label="LIC"
            )
            r_control_limits = None

        
        if chart_type == "XR":
            out_of_control_x = instance.df[
                (instance.df['X_bar'] > instance.lsc_x_bar_graph) |
                (instance.df['X_bar'] < instance.lic_x_bar_graph)
            ]
            out_of_control_r = instance.df[instance.df['R'] > instance.lsc_r_bar_graph]
        else:
            out_of_control_x = instance.df[
                (instance.df['Valor'] > instance.lsc_x_graph) |
                (instance.df['Valor'] < instance.lic_x_graph)
            ]
            out_of_control_r = None

        
        from western_electric_rules import WesternElectricAnalyzer
        if chart_type == "XR":
            analyzer_x = WesternElectricAnalyzer(
                data=instance.df['X_bar'],
                lc=instance.x_double_mean,
                lsc=instance.lsc_x_bar_graph,
                lic=instance.lic_x_bar_graph,
                chart_name="X-barra"
            )
            x_violations = analyzer_x.analyze_all_rules()
            western_electric_x = WesternElectricResult(
                violations=x_violations,
                chart_name="X-barra",
                state=analyzer_x.state
            )
            analyzer_r = WesternElectricAnalyzer(
                data=instance.df['R'],
                lc=instance.r_mean,
                lsc=instance.lsc_r_bar_graph,
                lic=instance.lic_r_bar_graph,
                chart_name="R"
            )
            r_violations = analyzer_r.analyze_all_rules()
            western_electric_r = WesternElectricResult(
                violations=r_violations,
                chart_name="R",
                state=analyzer_r.state
            )
        else:
            analyzer_x = WesternElectricAnalyzer(
                data=instance.df['Valor'],
                lc=instance.x_mean,
                lsc=instance.lsc_x_graph,
                lic=instance.lic_x_graph,
                chart_name="X (Individuais)"
            )
            x_violations = analyzer_x.analyze_all_rules()
            western_electric_x = WesternElectricResult(
                violations=x_violations,
                chart_name="X (Individuais)",
                state=analyzer_x.state
            )
            western_electric_r = None

       
        capability_result = None
        if hasattr(instance, 'capability') and instance.capability is not None:
            cap_analyzer = instance.capability
            success_prob = cap_analyzer.calculate_success_probability()
            capability_result = CapabilityResult(
                lse=cap_analyzer.lse,
                lie=cap_analyzer.lie,
                process_mean=cap_analyzer.process_mean,
                sigma=cap_analyzer.sigma,
                rcp=cap_analyzer.rcp if cap_analyzer.rcp is not None else 0.0,
                rcpk=cap_analyzer.rcpk if cap_analyzer.rcpk is not None else 0.0,
                rcps=cap_analyzer.rcps if cap_analyzer.rcps is not None else 0.0,
                rcpi=cap_analyzer.rcpi if cap_analyzer.rcpi is not None else 0.0,
                rcp_interpretation=cap_analyzer.interpret_rcp(),
                rcpk_interpretation=cap_analyzer.interpret_rcpk(),
                centralization_pct=abs(cap_analyzer.process_mean - (cap_analyzer.lse + cap_analyzer.lie) / 2) / ((cap_analyzer.lse - cap_analyzer.lie) / 2) * 100 if cap_analyzer.lse != cap_analyzer.lie else 0.0,
                is_centered=abs(cap_analyzer.process_mean - (cap_analyzer.lse + cap_analyzer.lie) / 2) <= 0.1 * (cap_analyzer.lse - cap_analyzer.lie) if cap_analyzer.lse != cap_analyzer.lie else True,
                success_probability=success_prob if success_prob is not None else 0.0
            )
        elif hasattr(instance, 'lse') and hasattr(instance, 'lie') and instance.lse is not None and instance.lie is not None:
            cap_analyzer = ProcessCapability(
                sigma=instance.sigma,
                lse=instance.lse,
                lie=instance.lie
            )
            if chart_type == "XR" and hasattr(instance, 'x_double_mean'):
                cap_analyzer.set_process_mean(instance.x_double_mean)
                process_mean_value = instance.x_double_mean
            else:
                cap_analyzer.set_process_mean(instance.x_mean)
                process_mean_value = instance.x_mean
            cap_results = cap_analyzer.calculate_all()
            success_prob = cap_analyzer.calculate_success_probability()
            capability_result = CapabilityResult(
                lse=instance.lse,
                lie=instance.lie,
                process_mean=process_mean_value,
                sigma=instance.sigma,
                rcp=cap_results['rcp'] if cap_results['rcp'] is not None else 0.0,
                rcpk=cap_results['rcpk'] if cap_results['rcpk'] is not None else 0.0,
                rcps=cap_results['rcps'] if cap_results['rcps'] is not None else 0.0,
                rcpi=cap_results['rcpi'] if cap_results['rcpi'] is not None else 0.0,
                rcp_interpretation=cap_analyzer.interpret_rcp(),
                rcpk_interpretation=cap_analyzer.interpret_rcpk(),
                centralization_pct=abs(process_mean_value - (instance.lse + instance.lie) / 2) / ((instance.lse - instance.lie) / 2) * 100 if instance.lse != instance.lie else 0.0,
                is_centered=abs(process_mean_value - (instance.lse + instance.lie) / 2) <= 0.1 * (instance.lse - instance.lie) if instance.lse != instance.lie else True,
                success_probability=success_prob if success_prob is not None else 0.0
            )

        
        if chart_type == "XR":
            report_data = XRReportData(
                df=instance.df,
                x_mean=instance.x_double_mean,
                r_mean=instance.r_mean,
                sigma=instance.sigma,
                x_control_limits=x_control_limits,
                r_control_limits=r_control_limits,
                out_of_control_x=out_of_control_x,
                out_of_control_r=out_of_control_r,
                western_electric_x=western_electric_x,
                western_electric_r=western_electric_r,
                process_info=process_info,
                image_base64=image_base64,
                capability=capability_result
            )
            output_file = generator.generate_xr_report(report_data)
            print(f"[INFO] Relatório HTML gerado: {output_file}")
        else:
            from html_report_generator import XReportData
            report_data = XReportData(
                df=instance.df,
                x_mean=instance.x_mean,
                sigma=instance.sigma,
                x_control_limits=x_control_limits,
                out_of_control_x=out_of_control_x,
                western_electric_x=western_electric_x,
                process_info=process_info,
                image_base64=image_base64,
                capability=capability_result
            )
            output_file = generator.generate_x_report(report_data)
            print(f"[INFO] Relatório HTML gerado: {output_file}")
    except Exception as e:
        print(f"[ERROR] Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()


