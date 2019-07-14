===================================================
Aim and basic specifications of the Autofit system
===================================================

By Autofit we mean an IT system, built around Python and a relation database aimed at the full automation 
of calibration tasks for IPV purposes. Though at least initially focused on Equity, efforts will be spent to 
maintain the implementation as general as possible.

The basic issues in implementing such system are:

1. IPV methodologies are interdependent and related through a hierachical dependency tree - for example, volatility calibration is performed only after the forward and implied volatility calculation
#. Different methodologies can be applied to the calibration of the same parameters depending on the available market data
#. New methodoogies can be inserted in the hierarchy tree with minimal changes to the code
#. The calibration tasks must be run in parallel and ideally on different machine
#. The system must cope with exeptions and failures of particular market data with no disruption on unrelated tasks
#. In case of catastrophic collapse, the system can be restarted from the last valid state