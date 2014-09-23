# 1 ---------

# A simple test of nrel_csm_fin model
from plant_financese.nrel_csm_fin.nrel_csm_fin import fin_csm_assembly

fin = fin_csm_assembly()

# 1 ---------
# 2 ---------

# Plant cost and energy production inputs
fin.turbine_cost = 6087803.555 / 50
fin.turbine_number = 50
preventative_opex = 401819.023
lease_opex = 22225.395
corrective_opex = 91048.387
fin.avg_annual_opex = preventative_opex + corrective_opex + lease_opex
fin.bos_costs = 7668775.3
fin.net_aep = 15756299.843

# 2 ---------
# 3 ---------

fin.run()

# 3 ---------
# 4 --------- 

print "Cost of energy for offshore wind plant with 50 NREL 5 MW Reference Turbines"
print "Levelized COE: {0}".format(fin.lcoe)
print "COE: {0}".format(fin.coe)
print

# 4 ----------
# 5 ----------

# A simple test of basic_finance model
from plant_financese.basic_finance.basic_finance import fin_cst_assembly

fin2 = fin_cst_assembly()

# 5 ---------- 
# 6 ----------

fin2.turbine_cost = 6087803.555 / 50
fin2.turbine_number = 50
preventative_maintenance_cost = 401819.023
land_lease_cost = 22225.395
corrective_maintenance_cost = 91048.387
fin2.avg_annual_opex = preventative_maintenance_cost + corrective_maintenance_cost + land_lease_cost
fin2.bos_costs = 7668775.3
fin2.net_aep = 15756299.843

# 6 ----------
# 7 ----------

fin2.run()

# 7 ----------
# 8 ----------

print "Cost of energy for offshore wind plant with 50 NREL 5 MW Reference Turbines"
print "COE: ${0:.2f} USD".format(fin.coe)

# 8 -----------