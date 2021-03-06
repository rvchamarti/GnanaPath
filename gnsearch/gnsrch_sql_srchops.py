######################################################################
#  GnanaSearch main module
#
#   through gnsrch module,
#   - SQL SELECT is supported.
#   - INSERT and UPDATE  are not supported
#   - Other SQL commands syntax are not *yet* supported
#
######################################################################
import os,sys
curentDir = os.getcwd()
listDir = curentDir.rsplit('/', 1)[0]
#print(' Test listdir: '+listDir)
sys.path.append(listDir)

from gndwdb.gndwdb_neo4j_fetchops import gndwdb_datarepo_edges_fetch_api, gndwdb_datarepo_edges_fetch_bynodelist_api
from gnutils.replace_spl_chars import gnutils_filter_json_escval
from gndwdb.gndwdb_neo4j_conn import gndwdb_neo4j_conn_metarepo, gndwdb_neo4j_conn_datarepo
from neo4j import GraphDatabase, basic_auth
from moz_sql_parser import parse
import json
import numpy as np
import neo4j
import warnings

import re
warnings.simplefilter('ignore')


def gnsrch_process_select_convert_cypher(sqlst, verbose):

    if (verbose > 3):
        print('gnsrch_process_select_conevert: processing sqlstring ' + sqlst)

    jsql = parse(sqlst)
    selstr = "select"
    retval = 0
    cql = ''
    if (selstr in jsql):
        # Select statement
        if (verbose > 3):
            print('gnsrch_process_select_convert_cypher: Processing select:')
        attrlist = jsql[selstr]
        entlist = jsql["from"]

        if (verbose > 3):
            print('gnsrch_process_select_convert_cypher: attrlist:' + attrlist)
            print('gnsrch_process_select_convert_cypher: entitylist:' + entlist)

        if (attrlist == "*"):
            # Ex: Select * from Customer
            cql += "MATCH (" + str(entlist) + " "
            cql += "{metanode:'" + str(entlist) + "'}) "
            cql += " return " + str(entlist) + " LIMIT 10 ;"

            if (verbose > 4):
                print('gnsrch_process_select_convert_cypher: cqlqry :' + cql)

            return cql

    else:
        retval = -1
        if (verbose > 3):
            print('gnsrch_process_select_conver_cypher: ERROR not a SELECT statement ')

    print('gnsrch_process_select_covert_cypher: ret val ' + str(retval))
    return cql


def gnsrch_process_sqlstr(sqlstr, meta_graph_conn,
                          data_graph_conn, verbose):

    # Convert sql query to CYPHER
    rjson = ''
    csqlstr = gnsrch_process_select_convert_cypher(sqlstr, verbose)

    if (verbose > 3):
        print('gnsrch_process_sqlstr: Converted sql to csql:' + csqlstr)

    # Execute it on Data Repo
    with data_graph_conn.session() as dataGrpDbSes:
        # Execute csql
        nodes = dataGrpDbSes.run(csqlstr)
        nlen = 0
        rjson = '{' + "\n"
        rjson += ' nodes: [' + "\n"

        for n in nodes:
            if (nlen > 0):
                rjson += ',' + "\n"
            for k in n.keys():
                rjson += '{ ' + "\n"
                a = 0
                nprops = n.get(k)
                for p in nprops.keys():
                    pv = nprops.get(p)
                    if (a > 0):
                        rjson += ', ' + "\n"
                    if (p == "name"):
                        rjson += '"id": "' + \
                            gnutils_filter_json_escval(pv) + '"'
                    else:
                        rjson += '"' + str(p) + '": "' + \
                            gnutils_filter_json_escval(pv) + '"'

                    a = a + 1
                if (a > 0):
                    rjson += "\n"
                rjson += '} '
            nlen += 1
        if (nlen > 0):
            rjson += "\n"

        rjson += ']' + "\n"
        rjson += '}' + "\n"
        return rjson

# API to send srch string  and return json output


def gnsrch_sqlqry_api(sqlstr, verbose):

    slen = len(sqlstr)

    if (slen == 0):
        # Empty search string get all data nodes
        rjson = gnsrch_datarepo_fetch_nodes_api(verbose)
        return (rjson)

    if (verbose > 3):
        print('gnrch_sqlqry_api: Starting search api ' + sqlstr)

    ##meta_graph_conn = gndwdb_neo4j_conn_metarepo(verbose)
    ##data_graph_conn = gndwdb_neo4j_conn_datarepo(verbose)

    ###ret = gnsrch_process_sqlstr(sqlstr, meta_graph_conn,
    ##                            data_graph_conn, verbose)

    jsql = parse(sqlstr);
    selstr = "select"

    if (selstr in jsql):
        if (verbose > 3):
            print('gnsrch_sql_srch_api: Processing select ')

        attrtlist = jsql[selstr]
        entlist = jsql["from"]

        if (verbose > 3):
            print('gnsrch_sql_srch_api: entity list is ')
            print(entlist);
            
        rjson = gndwdb_datarepo_edges_fetch_bynodelist_api(entlist, verbose)
            
        if (verbose > 4):
            print('gnsrch_sql_srch_api: process nodelist '+rjson)
            
    return rjson


def gnsrch_datarepo_fetch_nodes_api(verbose):

    if (verbose > 3):
        print('gnsrch_datarepo_fetch_nodes: fetching data repo nodes ')
    rjson = gndwdb_datarepo_edges_fetch_api(verbose)

    return(rjson)


if __name__ == '__main__':

    sqlst = "SELECT * from product;"
    # Setting up metarepo and db repo conns
    verbose = 6

    rjson = gnsrch_sqlqry_api(sqlst, verbose)

    if (verbose > 3):
        print('gnsrch_sql_srchops: rjson:')
        print(rjson)

    djson = gnsrch_datarepo_fetch_nodes_api(verbose)

    print(djson)
