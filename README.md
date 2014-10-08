Plant_FinanceSE is a set of models for assessing overall wind plant cost of energy (coe).  The models use wind turbine and plant cost and energy production information as well as several financial parameters in simple equations to estimate coe.

Author: [K. Dykes](mailto:nrel.wisdem+plantfinancese@gmail.com)

## Version

This software is a beta version 0.1.0.

## Detailed Documentation

For detailed documentation see <http://wisdem.github.io/Plant_FinanceSE/>

## Prerequisites

General: NumPy, SciPy, Swig, pyWin32, MatlPlotLib, Lxml, OpenMDAO

## Dependencies:

Wind Plant Framework: [FUSED-Wind](http://fusedwind.org) (Framework for Unified Systems Engineering and Design of Wind Plants)

Sub-Models: CommonSE, AeroelasticSE, RotorSE, DriveSE, DriveWPACT, TowerSE, JacketSE, Turbine_CostsSE, Plant_CostsSE, Plant_EnergySE, Plant_FinanceSE, pBEAM, CCBlade, Akima

Supporting python packages: Pandas, Algopy, Zope.interface, Sphinx, Xlrd, PyOpt, py2exe, Pyzmq, Sphinxcontrib-bibtex, Sphinxcontrib-zopeext, Numpydoc, Ipython


## Installation

First, clone the [repository](https://github.com/WISDEM/Plant_FinanceSE)
or download the releases and uncompress/unpack (Plant_FinanceSE.py-|release|.tar.gz or Plant_FinanceSE.py-|release|.zip) from the website link at the bottom the [Plant_FinanceSE site](http://nwtc.nrel.gov/Plant_FinanceSE).

Install Turbine_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module

	$ python
	> import plant_financese.basic_finance.coe_fin
	> import plant_financese.nrel_csm_fin.nrel_csm_fin

You may also run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

	$ python src/test/test_Plant_FinanceSE.py

For software issues please use <https://github.com/WISDEM/Plant_FinanceSE/issues>.  For functionality and theory related questions and comments please use the NWTC forum for [Systems Engineering Software Questions](https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002).