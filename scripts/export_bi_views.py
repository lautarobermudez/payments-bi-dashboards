#!/usr/bin/env python3
"""Export bi.v_ops from the payments database to CSV (and, optionally, to a Tableau .hyper extract).

    python scripts/export_bi_views.py                 # data/v_ops.csv (decimal point) and data/v_ops_es_AR.csv (decimal comma)
    python scripts/export_bi_views.py --hyper out.hyper   # also build a Tableau extract (needs tableauhyperapi)

The CSV with decimal comma is the one the Tableau workbook reads (it is authored in the es_AR locale).
Connection: --dsn or DATABASE_URL (default: dbname=payments).
"""
import argparse
import csv
import datetime as dt
import os
import pathlib

import psycopg

COLUMNS = ['op_id', 'empresa', 'nro_op', 'fecha_op', 'mes', 'anio', 'proveedor', 'estado', 'forma_pago',
           'condicion_pago', 'importe_total', 'fecha_pago', 'dias_pendiente', 'fecha_vencimiento', 'renglones']
DATA = pathlib.Path(__file__).resolve().parents[1] / 'data'


def fetch(dsn):
    with psycopg.connect(dsn) as con:
        return con.execute(f'SELECT {", ".join(COLUMNS)} FROM bi.v_ops ORDER BY op_id').fetchall()


def write_csv(path, rows, decimal_comma):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for row in rows:
            out = []
            for name, v in zip(COLUMNS, row):
                if v is None:
                    out.append('')
                elif name == 'importe_total' and decimal_comma:
                    out.append(f'{v:.2f}'.replace('.', ','))
                else:
                    out.append(str(v))
            w.writerow(out)


def write_hyper(path, rows):
    from tableauhyperapi import (Connection, CreateMode, HyperProcess, Inserter, SqlType, TableDefinition,
                                 TableName, Telemetry, Date)
    types = dict(op_id=SqlType.big_int(), empresa=SqlType.text(), nro_op=SqlType.big_int(), fecha_op=SqlType.date(),
                 mes=SqlType.date(), anio=SqlType.big_int(), proveedor=SqlType.text(), estado=SqlType.text(),
                 forma_pago=SqlType.text(), condicion_pago=SqlType.text(), importe_total=SqlType.double(),
                 fecha_pago=SqlType.date(), dias_pendiente=SqlType.big_int(), fecha_vencimiento=SqlType.date(),
                 renglones=SqlType.big_int())

    def conv(name, v):
        if v is None:
            return None
        if isinstance(v, dt.date):
            return Date(v.year, v.month, v.day)
        return float(v) if name == 'importe_total' else v

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(hp.endpoint, str(path), CreateMode.CREATE_AND_REPLACE) as c:
            c.catalog.create_schema('Extract')
            table = TableDefinition(TableName('Extract', 'Extract'), [TableDefinition.Column(n, types[n]) for n in COLUMNS])
            c.catalog.create_table(table)
            with Inserter(c, table) as ins:
                ins.add_rows([[conv(n, v) for n, v in zip(COLUMNS, row)] for row in rows])
                ins.execute()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dsn', default=os.environ.get('DATABASE_URL', 'dbname=payments'))
    ap.add_argument('--hyper', help='also write a Tableau extract to this path')
    args = ap.parse_args()
    rows = fetch(args.dsn)
    DATA.mkdir(exist_ok=True)
    write_csv(DATA / 'v_ops.csv', rows, decimal_comma=False)
    write_csv(DATA / 'v_ops_es_AR.csv', rows, decimal_comma=True)
    print(f'{len(rows)} rows -> data/v_ops.csv, data/v_ops_es_AR.csv')
    if args.hyper:
        write_hyper(pathlib.Path(args.hyper), rows)
        print(f'extract -> {args.hyper}')


if __name__ == '__main__':
    main()
