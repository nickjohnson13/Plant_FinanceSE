"""
fin_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, Enum, VarTree

from fusedwind.plant_cost.fused_finance import BaseFinancialModel, BaseFinancialAggregator, configure_base_finance
from fusedwind.interface import implement_base

# -------------------------------------------------------------------
@implement_base(BaseFinancialModel)
class fin_cst_assembly(Assembly):

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    # parameters
    fixed_charge_rate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    tax_rate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    offshore = Bool(True, iotype = 'in', desc = 'boolean for offshore')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

    def configure(self):

        configure_base_finance(self)

        self.replace('fin', fin_cst_component())

        self.connect('fixed_charge_rate','fin.fixed_charge_rate')
        self.connect('tax_rate','fin.tax_rate')
        self.connect('offshore','fin.offshore')

@implement_base(BaseFinancialAggregator)
class fin_cst_component(Component):

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    # parameters
    fixed_charge_rate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    tax_rate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    offshore = Bool(True, iotype = 'in', desc = 'boolean for offshore')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

    def __init__(self):
        """
        OpenMDAO component to wrap finance model of the NREL Cost and Scaling Model (csmFinance.py)
        """

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes finance model of the NREL Cost and Scaling model to determine overall plant COE and LCOE.
        """

        # print "In {0}.execute()...".format(self.__class__)

        if self.offshore:
           warrantyPremium = (self.turbine_cost * self.turbine_number / 1.10) * 0.15
           icc = self.turbine_cost * self.turbine_number + warrantyPremium + self.bos_costs
        else:
           icc = self.turbine_cost * self.turbine_number + self.bos_costs

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

        inputs = ['turbine_cost', 'bos_costs', 'avg_annual_opex', 'net_aep']
        outputs = ['coe']

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

    fin.fixed_charge_rate = 0.12
    fin.tax_rate = 0.4
    fin.offshore = True

    fin.run()
    print "Cost of energy for offshore wind plant with 50 NREL 5 MW Reference Turbines"
    print "COE: ${0:.4f} USD/kWh".format(fin.coe)

if __name__ == "__main__":

    example()