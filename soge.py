import csv
import sys
import math
import re

if len(sys.argv) < 2:
    print "usage : python soge.py filename.tsv"
    sys.exit()

SOGE_SYNTAX = \
[{'filter' : 'FRAIS PAIEMENT',    'fields' : [],                       'start' : 48, 'format' : 'FRAIS BANCAIRES - {SUB}'},       \
 {'filter' : 'RETRAIT DAB',       'fields' : [],                       'start' : 0,  'format' : 'RETRAIT DAB'},                   \
 {'filter' : 'CARTE',             'fields' : [],                       'start' : 18, 'format' : '{SUB}'},                         \
 {'filter' : 'PRELEVEMENT PEL',   'fields' : [],                       'start' : 0,  'format' : 'PRELEVEMENT PEL'},               \
 {'filter' : 'PRELEVEMENT',       'fields' : ['DE', 'ID', 'MOTIF'],    'start' : 0,  'format' : 'PRELEVEMENT - {DE} - {MOTIF}'},  \
 {'filter' : 'VIR EUROPEEN EMIS', 'fields' : ['POUR', 'REF'],          'start' : 0,  'format' : 'VIREMENT - {POUR}'},             \
 {'filter' : 'VIR PERM',          'fields' : ['POUR', 'REF', 'MOTIF'], 'start' : 0,  'format' : 'VIREMENT - {POUR} - {MOTIF}'},   \
 {'filter' : 'VIR RECU',          'fields' : ['DE', 'REF', 'MOTIF'],   'start' : 0,  'format' : 'VIREMENT - {DE} - {MOTIF}'},     \
 {'filter' : 'REMISE CHEQUE',     'fields' : [],                       'start' : 0,  'format' : 'REMISE CHEQUE'}]

def list_extend(input_list, extend_items):
    copy = input_list
    copy.extend(extend_items)
    return copy

def advanced_split(motif, fields, start):
    motif_split = dict.fromkeys(list_extend(fields, ['SUB', 'ALL']), '')
    motif_split['ALL'] = motif
    motif_split['SUB'] = motif[start:]
    tokens = re.split('({})'.format('|'.join([field + ':' for field in fields])), motif)
    current_field = ''
    for token in tokens:
        if token.rstrip(':') in fields:
            current_field = token.rstrip(':')
        elif current_field != '':
            motif_split[current_field] = token.strip()
            current_field = ''
    return motif_split

def advanced_format(format_str, motif_split):
    return format_str.format(**motif_split)

def format_motif(motif):
    for syntax in SOGE_SYNTAX:
        if syntax['filter'] in motif:
            motif_split = advanced_split(motif, syntax['fields'], syntax['start'])
            return advanced_format(syntax['format'], motif_split)
    # no filter found
    return motif

debits  = []
credits = []

with open(sys.argv[1]) as tsv:

    # discard the 2 first lines
    next(tsv)
    next(tsv)
    next(tsv)

    for line in csv.reader(tsv, dialect="excel-tab"): #You can also use delimiter="\t" rather than giving a dialect.
        if (len(line) == 5):
            date        = line[0].strip()
            motif       = format_motif(line[2].strip().upper())
            montant     = float(line[3].replace(",", "."))
            montant_str = (str(math.fabs(montant))).replace(".", ",")

            # outputs in a string
            output_str  = "{}\t{}\t{}".format(date, motif, montant_str)

            if (montant < 0.0):
                   debits.append(output_str)
            else:
                credits.append(output_str)

    print "\n".join(debits)
    print ' '
    print "\n".join(credits)