"""
fin_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, Enum, VarTree

from fusedwind.plant_cost.fused_fin_asym import BaseFinancialModel, BaseFinancialAggregator

from NREL_CSM.csmFinance import csmFinance 

# -------------------------------------------------------------------

class fin_csm_assembly(BaseFinancialModel):
    
    def configure(self):
    
        super(fin_csm_assembly, self).configure()
        
        self.replace('fin', fin_csm_component())
        
        self.create_passthrough('fin.rated_power')
        self.create_passthrough('fin.fixed_charge_rate')
        self.create_passthrough('fin.construction_finance_rate')
        self.create_passthrough('fin.tax_rate')
        self.create_passthrough('fin.discount_rate')
        self.create_passthrough('fin.construction_time')
        self.create_passthrough('fin.project_lifetime')
        
        self.create_passthrough('fin.preventative_maintenance_cost')
        self.create_passthrough('fin.corrective_maintenance_cost')
        self.create_passthrough('fin.land_lease_cost')
        self.create_passthrough('fin.sea_depth')
        
        self.create_passthrough('fin.lcoe')

class fin_csm_component(BaseFinancialAggregator):    

    # variables
    rated_power = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    
    # parameters
    fixed_charge_rate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    construction_finance_rate = Float(0.00, iotype='in', desc = 'construction financing rate applied to overnight capital costs')
    tax_rate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    discount_rate = Float(0.07, iotype = 'in', desc = 'applicable project discount rate')
    construction_time = Float(1.0, iotype = 'in', desc = 'number of years to complete project construction')
    project_lifetime = Float(20.0, iotype = 'in', desc = 'project lifetime for LCOE calculation')

    preventative_maintenance_cost = Float(401819.023, iotype='in', units='USD', desc='O&M costs')
    corrective_maintenance_cost   = Float(91048.387, iotype='in', units='USD', desc='levelized replacement costs')
    land_lease_cost     = Float(22225.395, iotype='in', units='USD', desc='land lease costs')  
    sea_depth = Float(20.0, iotype='in', units='m', desc = 'depth of project for offshore, (0 for onshore)')
        
    # output
    lcoe = Float(0.0, iotype='out', desc='Cost of energy - unlevelized')
    
    def __init__(self):
        """
        OpenMDAO component to wrap finance model of the NREL Cost and Scaling Model (csmFinance.py)

        Parameters
        ----------  
		    ratedPower : float
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
		    projectLifetime : float
		      project lifetime for LCOE calculation
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
		    seaDepth : float
		      depth of project [m]
		        
        Returns
        -------
		    coe : float
		      Cost of energy - unlevelized [USD/kWh]
		    lcoe : float
		      Cost of energy - levelized [USD/kWh]

        """

        super(fin_csm_component, self).__init__()

        #initialize csmFIN model
        self.fin = csmFinance()


    def execute(self):
        """
        Executes finance model of the NREL Cost and Scaling model to determine overall plant COE and LCOE.
        """
        
        print "In {0}.execute()...".format(self.__class__)

        self.fin.compute(self.rated_power, self.turbine_cost * self.turbine_number, self.preventative_maintenance_cost, \
                         self.land_lease_cost, self.corrective_maintenance_cost, self.bos_cost, self.net_aep, \
                         self.fixed_charge_rate, self.construction_finance_rate, self.tax_rate, self.discount_rate, self.construction_time, \
                         self.project_lifetime, self.turbine_number, self.sea_depth)

        self.coe = self.fin.getCOE()
        self.lcoe = self.fin.getLCOE()

def example():
	
    # simple test of module

    fin = fin_csm_component()

    fin.turbine_cost = 6087803.555 / 50
    fin.turbine_number = 50
    fin.preventative_maintenance_cost = 401819.023
    fin.land_lease_cost = 22225.395
    fin.corrective_maintenance_cost = 91048.387
    fin.avg_annual_opex = fin.preventative_maintenance_cost + fin.corrective_maintenance_cost + fin.land_lease_cost
    fin.bos_cost = 7668775.3
    fin.net_aep = 15756299.843
    
    fin.execute()
    print "Offshore"
    print "lcoe: {0}".format(fin.lcoe)
    print "coe: {0}".format(fin.coe)	

if __name__ == "__main__":

    example()