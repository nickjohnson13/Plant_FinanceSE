"""
fin_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, Enum, VarTree

from fusedwind.plant_cost.fused_fin_asym import BaseFinancialModel, BaseFinancialAggregator

# -------------------------------------------------------------------

class fin_cst_assembly(BaseFinancialModel):
    
    def configure(self):
    
        super(fin_cst_assembly, self).configure()
        
        self.replace('fin', fin_cst_component())

        self.create_passthrough('fin.fixed_charge_rate')
        self.create_passthrough('fin.tax_rate')
        self.create_passthrough('fin.offshore')

class fin_cst_component(BaseFinancialAggregator):

    # parameters
    fixed_charge_rate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    tax_rate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    offshore = Bool(True, iotype = 'in', desc = 'boolean for offshore')
    
    def __init__(self):
        """
        OpenMDAO component to wrap finance model of the NREL Cost and Scaling Model (csmFinance.py)

        Parameters
        ----------
        fixedChargeRate : float
          fixed charge rate for coe calculation
        taxRate : float
          tax rate applied to operations
        turbineNumber : int
          number of turbines at plant
        aep : float
          Annual energy production [kWh]
        turbineCost : float
          Turbine capital costs [USD per turbine]
        BOScost : float
          Balance of station costs total [USD]
        preventativeMaintenanceCost : float
          O&M costs annual total [USD]
        correctiveMaintenanceCost : float
          levelized replacement costs annual total [USD]
        landLeaseCost : float
          land lease costs annual total [USD] 
            
        Returns
        -------
        lcoe : float
          Cost of energy - levelized [USD/kWh]
        """
        
        super(fin_cst_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes finance model of the NREL Cost and Scaling model to determine overall plant COE and LCOE.
        """
        
        print "In {0}.execute()...".format(self.__class__)

        if self.offshore:
           warrantyPremium = (self.turbine_cost * self.turbine_number / 1.10) * 0.15
           icc = self.turbine_cost * self.turbine_number + warrantyPremium + self.bos_costs
        else:
           icc = self.turbine_cost * self.turbine_number + self.bos_cost

        # compute COE and LCOE values
        self.coe = (icc * self.fixed_charge_rate + self.avg_annual_opex * (1-self.tax_rate)) / self.net_aep
        
        # derivatives
        if self.offshore:
            self.d_coe_d_turbine_cost = (self.turbine_number * (1 + 0.15/1.10) * self.fixed_charge_rate + 0.15/1.10) / self.net_aep
        else:
            self.d_coe_d_turbine_cost = self.turbine_number * self.fixed_charge_rate / self.net_aep
        self.d_coe_d_bos_cost = self.fixed_charge_rate / self.net_aep
        self.d_coe_d_avg_annual_opex = (1-self.tax_rate) / self.net_aep
        self.d_coe_d_net_aep = -(((self.turbine_cost * self.turbine_number + self.bos_costs) * self.fixed_charge_rate) + self.avg_annual_opex * (1-self.tax_rate)) / (self.net_aep**2)

    def list_deriv_vars(self):

        inputs = ('turbine_cost', 'bos_cost', 'avg_annual_opex', 'net_aep')
        outputs = ('coe')

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_coe_d_turbine_cost, self.d_coe_d_bos_cost, self.d_coe_d_avg_annual_opex, self.d_coe_d_net_aep]])

        return self.J

def example():
  
    # simple test of module
    fin = fin_cst_assembly()

    fin.turbine_cost = 6087803.555 / 50
    fin.turbine_number = 50
    preventative_maintenance_cost = 401819.023
    land_lease_cost = 22225.395
    corrective_maintenance_cost = 91048.387
    fin.avg_annual_opex = preventative_maintenance_cost + corrective_maintenance_cost + land_lease_cost
    fin.bos_costs = 7668775.3
    fin.net_aep = 15756299.843
    
    fin.execute()
    print "Offshore"
    print "coe: {0}".format(fin.coe)

if __name__ == "__main__":

    example()