=======================
Buxfer export converter
=======================

This script can be used to convert your `buxfer <http://buxfer.com>`_ transaction exports into compatible clear checkbook ones.

*****
Usage
*****
::

    ./bconv.py buxfer_export.csv clearcheckbooks_import.csv

*******
Remarks
*******
* Converts 'Income', 'Expense' and 'Transfers'
* Skips 'Settlement', 'Paid for friend', 'Split bill', 'Loan'
* Converts tags to categories; on multiply tags the last one is choosen
