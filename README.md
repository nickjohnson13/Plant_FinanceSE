Plant_FinanceSE is a set of models for assessing overall wind plant cost of energy (coe).  The models use wind turbine and plant cost and energy production information as well as several financial parameters in simple equations to estimate coe.

Author: [K. Dykes](mailto:katherine.dykes@nrel.gov)

## Detailed Documentation

For detailed documentation see <http://wisdem.github.io/Plant_FinanceSE/>

## Prerequisites

NumPy, SciPy, FUSED-Wind, OpenMDAO

## Installation

Install Turbine_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module

	$ python
	> import basic_finance.coe_fin
	> import nrel_csm_fin.nrel_csm_fin

You may also run the unit tests.

	$ python src/test/test_Plant_FinanceSE_gradients.py

