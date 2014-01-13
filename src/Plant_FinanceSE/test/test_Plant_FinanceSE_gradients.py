
#!/usr/bin/env python
# encoding: utf-8
"""
test_Turbine_CostsSE.py

Created by Katherine Dykes on 2014-01-07.
Copyright (c) NREL. All rights reserved.
"""

import unittest
import numpy as np
from commonse.utilities import check_gradient_unit_test
from Plant_FinanceSE.NREL_CSM_FIN.coe_fin import fin_cst_component
from Plant_FinanceSE.NREL_CSM_FIN.nrel_csm_fin import fin_csm_component


class Test_fin_cst_component(unittest.TestCase):

    def test1(self):

        fin = fin_cst_component()
    
        fin.turbine_cost = 6087803.555 / 50
        fin.turbine_number = 50
        preventative_maintenance_cost = 401819.023
        land_lease_cost = 22225.395
        corrective_maintenance_cost = 91048.387
        fin.avg_annual_opex = preventative_maintenance_cost + corrective_maintenance_cost + land_lease_cost
        fin.bos_cost = 7668775.3
        fin.net_aep = 15756299.843

        check_gradient_unit_test(self, fin)
 
class Test_fin_csm_component(unittest.TestCase):

    def test1(self):

        fin = fin_csm_component()
    
        fin.turbine_cost = 6087803.555 / 50
        fin.turbine_number = 50
        fin.preventative_opex = 401819.023
        fin.lease_opex = 22225.395
        fin.corrective_opex = 91048.387
        #fin.avg_annual_opex = fin.preventative_opex + fin.corrective_opex + fin.lease_opex
        fin.bos_costs = 7668775.3
        fin.net_aep = 15756299.843

        check_gradient_unit_test(self, fin)
        
if __name__ == "__main__":
    unittest.main()
    