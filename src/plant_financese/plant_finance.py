from openmdao.api import Component

import numpy as np

class PlantFinance(Component):
    def __init__(self):
        super(PlantFinance, self).__init__()

        self.amortFactor = None
        
        # Inputs
        self.add_param('turbine_cost' , val=0.0, units='USD', desc = 'A Wind Turbine Capital _cost')
        self.add_param('turbine_number', val=0, desc = 'number of turbines at plant', pass_by_obj=True)
        self.add_param('bos_costs', val=0.0, units='USD', desc='A Wind Plant Balance of Station _cost Model')
        self.add_param('avg_annual_opex', val=0.0, units='USD', desc='A Wind Plant Operations Expenditures Model')
        self.add_param('net_aep', val=0.0, desc='A Wind Plant Annual Energy Production Model', units='kW*h')

        # parameters
        self.add_param('fixed_charge_rate', val=0.12, desc = 'fixed charge rate for coe calculation')
        self.add_param('tax_rate', val=0.4, desc = 'tax rate applied to operations')
        self.add_param('discount_rate', val=0.07, desc = 'applicable project discount rate')
        self.add_param('construction_time', val=1.0, units='years', desc = 'number of years to complete project construction')
        self.add_param('project_lifetime', val=20.0, units='years', desc = 'project lifetime for LCOE calculation')
        self.add_param('sea_depth', val=20.0, units='m', desc = 'depth of project for offshore, (0 for onshore)')

        #Outputs
        self.add_output('coe', val=0.0, desc='Levelized cost of energy for the wind plant', units='USD/kW')
        self.add_output('lcoe', val=0.0, desc='_cost of energy - unlevelized', units='USD/kW')
    
    def solve_nonlinear(self, params, unknowns, resids):
        # Unpack parameters
        depth       = params['sea_depth']
        n_turbine   = params['turbine_number']
        c_turbine   = params['turbine_cost']
        c_bos       = params['bos_costs']
        c_opex      = params['avg_annual_opex']
        fcr         = params['fixed_charge_rate']
        tax         = params['tax_rate']
        r           = params['discount_rate']
        aep         = params['net_aep']
        t_construct = params['construction_time']
        t_project   = params['project_lifetime']
        
        # Handy offshore boolean flag
        offshore = (depth > 0.0)

        icc = c_turbine*n_turbine + c_bos
        if offshore:
           # warranty Premium 
           icc += (c_turbine * n_turbine / 1.10) * 0.15

        #compute COE and LCOE values
        unknowns['coe'] = (icc*fcr + c_opex*(1-tax)) / aep

        self.amortFactor = (1 + 0.5*((1+r)**t_construct - 1)) * (r/(1-(1+r)**(-t_project)))
        unknowns['lcoe'] = (icc * self.amortFactor + c_opex)/aep

    def linearize(self, params, unknowns, resids):
        # Unpack parameters
        depth       = params['sea_depth']
        n_turbine   = params['turbine_number']
        c_turbine   = params['turbine_cost']
        c_bos       = params['bos_costs']
        c_opex      = params['avg_annual_opex']
        fcr         = params['fixed_charge_rate']
        tax         = params['tax_rate']
        r           = params['discount_rate']
        aep         = params['net_aep']
        t_construct = params['construction_time']
        t_project   = params['project_lifetime']

        # Handy offshore boolean flag
        offshore = (depth > 0.0)

        dicc_dcturb = n_turbine
        dicc_dcbos  = 1.0
        if offshore:
            dicc_dcturb = n_turbine * (1.0 + 0.15 / 1.10)
            
        dcoe_dcturb = dicc_dcturb * fcr/aep
        dcoe_dcbos  = dicc_dcbos  * fcr/aep
        dcoe_dopex  = (1-tax)          /aep
        dcoe_daep   = -unknowns['coe'] /aep

        dlcoe_dcturb = dicc_dcturb * self.amortFactor/aep
        dlcoe_dcbos  = dicc_dcbos  * self.amortFactor/aep
        dlcoe_dopex  = 1.0                           /aep
        dlcoe_daep   = -unknowns['lcoe']             /aep

        J = {}
        J['coe' , 'turbine_cost'   ] = dcoe_dcturb
        J['coe' , 'bos_cost'       ] = dcoe_dcbos
        J['coe' , 'avg_annual_opex'] = dcoe_dopex
        J['coe' , 'net_aep'        ] = dcoe_daep
        J['lcoe', 'turbine_cost'   ] = dlcoe_dcturb
        J['lcoe', 'bos_cost'       ] = dlcoe_dcbos
        J['lcoe', 'avg_annual_opex'] = dlcoe_dopex
        J['lcoe', 'net_aep'        ] = dlcoe_daep
        return J
        

        
