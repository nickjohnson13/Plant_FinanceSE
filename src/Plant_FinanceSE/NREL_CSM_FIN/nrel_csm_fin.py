"""
fin_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, Enum, VarTree

from fusedwind.plant_cost.fused_fin_asym import BaseFinancialModel, BaseFinancialAggregator

import numpy as np

# -------------------------------------------------------------------

class fin_csm_assembly(BaseFinancialModel):

    # parameters
    fixed_charge_rate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    construction_finance_rate = Float(0.00, iotype='in', desc = 'construction financing rate applied to overnight capital costs')
    tax_rate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    discount_rate = Float(0.07, iotype = 'in', desc = 'applicable project discount rate')
    construction_time = Float(1.0, iotype = 'in', desc = 'number of years to complete project construction')
    project_lifetime = Float(20.0, iotype = 'in', desc = 'project lifetime for LCOE calculation')
    sea_depth = Float(20.0, iotype='in', units='m', desc = 'depth of project for offshore, (0 for onshore)')

    # output
    lcoe = Float(iotype='out', desc='_cost of energy - unlevelized')

    def configure(self):

        super(fin_csm_assembly, self).configure()

        self.replace('fin', fin_csm_component())

        self.connect('fixed_charge_rate','fin.fixed_charge_rate')
        self.connect('construction_finance_rate','fin.construction_finance_rate')
        self.connect('tax_rate','fin.tax_rate')
        self.connect('discount_rate','fin.discount_rate')
        self.connect('construction_time','fin.construction_time')
        self.connect('project_lifetime','fin.project_lifetime')

        self.connect('sea_depth','fin.sea_depth')

        self.connect('fin.lcoe','lcoe')

class fin_csm_component(BaseFinancialAggregator):

    # parameters
    fixed_charge_rate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    construction_finance_rate = Float(0.00, iotype='in', desc = 'construction financing rate applied to overnight capital costs')
    tax_rate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    discount_rate = Float(0.07, iotype = 'in', desc = 'applicable project discount rate')
    construction_time = Float(1.0, iotype = 'in', desc = 'number of years to complete project construction')
    project_lifetime = Float(20.0, iotype = 'in', desc = 'project lifetime for LCOE calculation')
    sea_depth = Float(20.0, iotype='in', units='m', desc = 'depth of project for offshore, (0 for onshore)')

    # output
    lcoe = Float(iotype='out', desc='_cost of energy - unlevelized')

    def __init__(self):
        """
        OpenMDAO component to wrap finance model of the NREL _cost and Scaling Model (csmFinance.py)

        Parameters
        ----------
        machine_rating : float
          rated power for a wind turbine [kW]
        fixedChargeRate : float
          fixed charge rate for coe calculation
        constructionFinancingRate : float
          construction financing rate applied to overnight capital costs
        taxRate : float
          tax rate applied to operations
        discountRate : float
          applicable project discount rate
        constructionTime : float
          number of years to complete project construction
        project_lifetime : float
          project lifetime for LCOE calculation
        turbine_number : int
          number of turbines at plant
        aep : float
          Annual energy production [kWh]
        turbine_cost : float
          Turbine capital costs [USD per turbine]
        BOScost : float
          Balance of station costs total [USD]
        preventativeMaintenance_cost : float
          O&M costs annual total [USD]
        correctiveMaintenance_cost : float
          levelized replacement costs annual total [USD]
        landLease_cost : float
          land lease costs annual total [USD]
        sea_depth : float
          depth of project [m]

        Returns
        -------
        coe : float
          _cost of energy - unlevelized [USD/kWh]
        lcoe : float
          _cost of energy - levelized [USD/kWh]
        """

        super(fin_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes finance model of the NREL _cost and Scaling model to determine overall plant COE and LCOE.
        """

        # print "In {0}.execute()...".format(self.__class__)

        if self.sea_depth > 0.0:
           offshore = True
        else:
           offshore = False

        if offshore:
           warrantyPremium = (self.turbine_cost * self.turbine_number / 1.10) * 0.15
           icc = self.turbine_cost * self.turbine_number + warrantyPremium + self.bos_costs
        else:
           icc = self.turbine_cost * self.turbine_number + self.bos_costs

        #compute COE and LCOE values
        self.coe = (icc* self.fixed_charge_rate / self.net_aep) + \
                   (self.avg_annual_opex) * (1-self.tax_rate) / self.net_aep

        amortFactor = (1 + 0.5*((1+self.discount_rate)**self.construction_time-1)) * \
                      (self.discount_rate/(1-(1+self.discount_rate)**(-1.0*self.project_lifetime)))
        self.lcoe = (icc * amortFactor + self.avg_annual_opex)/self.net_aep


        # derivatives
        if offshore:
            self.d_coe_d_turbine_cost = (self.turbine_number * (1 + 0.15/1.10) * self.fixed_charge_rate + 0.15/1.10) / self.net_aep
        else:
            self.d_coe_d_turbine_cost = self.turbine_number * self.fixed_charge_rate / self.net_aep
        self.d_coe_d_bos_cost = self.fixed_charge_rate / self.net_aep
        self.d_coe_d_avg_opex = (1-self.tax_rate) / self.net_aep
        self.d_coe_d_net_aep = -(icc * self.fixed_charge_rate + self.avg_annual_opex * (1-self.tax_rate)) / (self.net_aep**2)

        if offshore:
            self.d_lcoe_d_turbine_cost = (1 + 0.15/1.10) * amortFactor / self.net_aep
        else:
            self.d_lcoe_d_turbine_cost = amortFactor / self.net_aep
        self.d_lcoe_d_bos_cost = amortFactor / self.net_aep
        self.d_lcoe_d_avg_opex = 1. / self.net_aep
        self.d_lcoe_d_net_aep = -(icc * amortFactor + self.avg_annual_opex) / (self.net_aep**2)

    def list_deriv_vars(self):

        inputs = ['turbine_cost', 'bos_costs', 'avg_annual_opex', 'net_aep']
        outputs = ['coe', 'lcoe']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_coe_d_turbine_cost, self.d_coe_d_bos_cost, self.d_coe_d_avg_opex, self.d_coe_d_net_aep],\
                           [self.d_lcoe_d_turbine_cost, self.d_lcoe_d_bos_cost, self.d_lcoe_d_avg_opex, self.d_lcoe_d_net_aep]])

        return self.J


def example():

    # simple test of module

    fin = fin_csm_component()

    fin.turbine_cost = 6087803.555 / 50
    fin.turbine_number = 50
    preventative_opex = 401819.023
    lease_opex = 22225.395
    corrective_opex = 91048.387
    fin.avg_annual_opex = preventative_opex + corrective_opex + lease_opex
    fin.bos_costs = 7668775.3
    fin.net_aep = 15756299.843

    fin.execute()
    print "Offshore"
    print "lcoe: {0}".format(fin.lcoe)
    print "coe: {0}".format(fin.coe)

if __name__ == "__main__":

    example()