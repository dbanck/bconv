#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Buxfer export converter
    ~~~~~~~~~~~~~~~~~~~~~~~

    Convert buxfer csv export files into clearcheckbook compatible ones.
    Make sure your account names (e.g. 'Savings', 'Cash') are the same on
    both services.

    Remarks:
        * Converts 'Income', 'Expense' and 'Transfers'
        * Skips 'Settlement', 'Paid for friend', 'Split bill', 'Loan'
        * Converts tags to categories
        * On multiply tags the last one is selected

    :copyright: (c) 2012 by Daniel Banck <daniel@dbanck.de>
    :license: see LICENSE
"""

import csv
import os
import sys


OLD_FIELDS = {
    'ACCOUNT': 6,
    'AMOUNT': 3,
    'CURRENCY': 2,
    'DATE': 0,
    'DESCRIPTION': 1,
    'STATUS': 7,
    'TAGS': 5,
    'TYPE': 4,
}

NEW_FIELDS = {
    'ACCOUNT': 7,
    'AMOUNT': 1,
    'CATEGORY': 6,
    'CHECK_NUMBER': 5,
    'DATE': 0,
    'DESCRIPTION': 2,
    'MEMO': 3,
    'PAYEE': 4,
}

ROW_TYPES = {
    'DEPOSIT': 'Income',
    'TRANSFER': 'Transfer',
    'WITHDRAWAL': 'Expense',
}


class Converter(object):

    def __init__(self, input_path, output_path):
        """Constructor."""

        self.input_file = open(input_path, 'rb')
        self.output_file = open(output_path, 'wb')
        self.new_rows = []

    def _convert_row(self, row):
        """Convert an old row into a new one."""

        new_row = ['' for i in NEW_FIELDS]
        new_row[NEW_FIELDS['DATE']] = row[OLD_FIELDS['DATE']]
        new_row[NEW_FIELDS['DESCRIPTION']] = row[OLD_FIELDS['DESCRIPTION']]

        self._set_category(new_row, row)

        if row[OLD_FIELDS['TYPE']] == ROW_TYPES['TRANSFER']:
            self._handle_transfer(new_row, row)
        else:
            if not self._format_amount(new_row, row):
                return # Skip this row on unknown type
            new_row[NEW_FIELDS['ACCOUNT']] = row[OLD_FIELDS['ACCOUNT']]

        self.new_rows.append(new_row)

    def _format_amount(self, new_row, row):
        """Format the new amount. Return if conversion was successful."""

        if row[OLD_FIELDS['TYPE']] == ROW_TYPES['WITHDRAWAL']:
            prefix = '-'
        elif row[OLD_FIELDS['TYPE']] == ROW_TYPES['DEPOSIT']:
            prefix = ''
        else:
            return False

        new_row[NEW_FIELDS['AMOUNT']] = '{0}{1}'.format(prefix,
                row[OLD_FIELDS['AMOUNT']][2:].replace('.','').replace(',','.'))

        return True

    def _handle_transfer(self, new_row, row):
        """Add another row for transfers."""

        accounts = row[OLD_FIELDS['ACCOUNT']].split(' -> ')

        new_row2 = new_row[:] # copy
        new_row[NEW_FIELDS['AMOUNT']] = \
                row[OLD_FIELDS['AMOUNT']][2:].replace('.','').replace(',','.')
        new_row[NEW_FIELDS['ACCOUNT']] = accounts[1]

        new_row2[NEW_FIELDS['AMOUNT']] = '-{0}'.format(
                row[OLD_FIELDS['AMOUNT']][2:].replace('.','').replace(',','.'))
        new_row2[NEW_FIELDS['ACCOUNT']] = accounts[0]

        self.new_rows.append(new_row2)

    def _set_category(self, new_row, row):
        """
        Set the category from the old tags.
        If there is more than one tag, pick the last one.
        """

        if ',' in row[OLD_FIELDS['TAGS']]:
            new_row[NEW_FIELDS['CATEGORY']] = \
                    row[OLD_FIELDS['TAGS']].split(',')[-1]
        else:
            new_row[NEW_FIELDS['CATEGORY']] = row[OLD_FIELDS['TAGS']]

    def parse_file(self):
        """Parse the input file and convert each row."""

        reader = csv.reader(self.input_file)

        for row in reader:
            self._convert_row(row)

    def write_file(self):
        """Write converted rows into new file."""

        writer = csv.writer(self.output_file)

        for row in self.new_rows:
            writer.writerow(row)

        print "Conversion complete. Check your output file."

if __name__ == '__main__':
    arglen = len(sys.argv)

    if arglen != 3:
        print "Usage: ./bconv.py input.csv output.csv"
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print "Input file does not exists."
        sys.exit(1)

    if not os.access(input_file, os.R_OK):
        print "Input file is not readable."
        sys.exit(1)

    if not os.access(output_file, os.W_OK):
        print "Output file is not writable."
        sys.exit(1)

    c = Converter(input_file, output_file)
    c.parse_file()
    c.write_file()
