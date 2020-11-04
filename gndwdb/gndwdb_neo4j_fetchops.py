####################################################################
# GnanaDWDB Fetch Ops Module on Neo4j
#    - Fetch nodes and its properties from neo4j
#    - Fetch edges(relationships) from Neo4j
###################################################################
import os
import csv
import json
import psycopg2
import sys
import numpy as np
import neo4j
import warnings
import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


from  .gndwdb_neo4j_conn import gndwdb_neo4j_conn_metarepo, gndwdb_neo4j_conn_datarepo;


#curentDir=os.getcwd()
#listDir=curentDir.rsplit('/',1)[0]
#gndwdbDir=listDir+'/gndwdb'
#if listDir not in sys.path:
#    sys.path.append(listDir)
#if gndwdbDir not in sys.path:
#    sys.path.append(gndwdbDir)
#print(sys.path)



class    gndwdbFetchApp:

    def __init__(self, driverconnp):
        ###self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver = driverconnp;

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()



    def find_node_byname(self, node_name, verbose):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_node, node_name);

            njson = '{';
            
            for record in result:
                if (verbose > 3):
                    print("gndwdbFetchApp: Found node: {record}".format(record=record));
                if (verbose > 4):     
                    print(record);
                njson += ' "node": { '+ "\n";

                
                 
    @staticmethod
    def   _find_and_return_node_byname(tx, node_name, verbose):
        query = (
            "MATCH (p) "
            "WHERE p.name = $name "
            "RETURN p"
        )
        result = tx.run(query, name=node_name);
        njson = '';
        
        for record in result:
            node = record['p'];
            njson += convert_node_rec_json(node, verbose);
            
        return njson;


    def     find_node_by_id(self, node_id, verbose):
        
        with self.driver.session() as session:

              query = (
                 "MATCH (p) "
                 "WHERE ID(p) = $id "
                 "RETURN p"
                 );


            
              ###result = session.read_transaction(self._find_and_return_node_byid, node_id);
              result = session.run(query, id=node_id);

              for record in result:
                 node = record['p'];
                 if (verbose > 3):
                    print("gndwdbFetchApp: Found node: {record}".format(record=record));
                    
                 if (verbose > 4):
                    print(record);
                 #njson += ' "node": { '+ "\n";
                 ndict = self.convert_node_rec_dict(node, verbose);

                 if (verbose > 5):
                    print('gndwdbFetchApp: node id:'+str(node_id));
                    print(ndict);

              return(ndict);     

             
    
    def      _find_and_return_node_byid(tx, id, verbose):
        query = (
            "MATCH (p) "
            "WHERE ID(p) = $id "
            "RETURN p"
        );
        
        result = tx.run(query, id=id);
        #njson = '';
        
        #for record in result:
        #    node = record['p'];
        #    nodedict = convert_node_rec_dict(node, verbose);
            
        return result;


    
        
    def     convert_node_rec_dict(self, node, verbose):

                ndict = {};
                njson = '{'+"\n";
                nodeid = node.id;
                
                if (verbose > 3):
                    print('GNdwFetchApp:  convert node rec dict '+str(nodeid));
                    
                 ###nl_iter = iter(node.labels);
                nodelabel = ''; 
                for l in iter(node.labels):
                  nodelabel = l;

                if (verbose > 3):  
                   print('GNdwFetchApp: convert node label '+str(nodelabel));

                   
                njson += '  "id": "'+str(nodeid)+'" ,'+"\n";
                njson += '  "nodetype": "'+str(nodelabel)+'" ';

                ndict['id'] = nodeid;
                ndict['nodename'] = nodelabel;

                i = 0;
                for nkey in node.keys():
                    if (verbose > 5):
                       print("GNdwFetchApp: getting node keys Record  Key k:"+str(nkey));
                                        
                    nkval = node.get(nkey);
                    if (verbose > 5):
                       print("GNDwFetchApp: getting node keys Record Key val "+str(nkval));
                       
                    if (i >= 0):
                        njson += ','+"\n";
                        
                    if (nkey == "id"):
                        nkey = "node_id";
                        
                    njson += '   "'+str(nkey)+'":  "'+str(nkval)+'" ';
                    ndict[nkey] = nkval;
                    i += 1;

                njson += "\n";    
                njson += "} ";
                #### These attributes set at client
                #njson += '  "group": "nodes" ,'+"\n";
                #njson += '   "selectable": true,'+"\n";
                #njson += '  "grabbable":  true '+"\n";
                #njson += '  },'+"\n";
                #if (verbose > 4):
                #   print(njson);
                ndict['jsonstr'] = njson;
                return(ndict);

                 

    def      find_nodes_return_rec(self, verbose):
        
        with self.driver.session() as session:
            njson = "{ "+"\n";
            query = (
                 "MATCH (n) "
                " RETURN n LIMIT 5"
            )
            
            result = session.run(query);
            nnum = 0;
            njson += ' "nodes": [ '+"\n";
            for record in result:

                if (verbose > 5):
                    
                     print(record);
                node = record["n"];
                
                if (nnum > 0):
                   njson += ", "+"\n";
                
                ndict = self.convert_node_rec_json(node, verbose);
                nj = ndict['jsonstr'];
                njson += nj;
                if (verbose > 4):
                    print('gndwdbFetchOps: convet node to json ele '+str(nnum));
                    print(nj);
                
                nnum += 1; 

            njson += "\n";
            njson += "]" +"\n";
            
            njson += "}"+"\n";
            
            
            if (verbose > 3):
                print('gndbdwFetchOps: Find Nodes res ');
                print(njson);
            return(njson);

        
    def      convert_rel_rec_dict(self, relnode, verbose):
        
         if (verbose > 4):
             print(relnode);
             
         rdict = {};    
         ###relnode = record["r"];
         reltype = relnode.type;
         relid = relnode.id;

         if (verbose > 3):
             print("GNDwFetchApp: converting relation  id:"+str(relid)+"  type: "+str(reltype));
           
         rjson = '  {'+"\n";
         rjson += '  "type": "'+str(reltype)+'" ,'+"\n";
         rjson += '   "id": "'+str(relid)+'"  ,'+"\n";

         rdict['id'] = relid;
         rdict['type'] = reltype;
         
         nodes = relnode.nodes;

         if (verbose > 6):
            print("GNDwFetchApp: converting relation  relationship Nodes: ");
            print(nodes);
            
         snode = nodes[0];
         tnode = nodes[1];
         ###print("Source Node id:"+str(snode.id));
         ##print("Target Node id:"+str(tnode.id));
         rjson += '   "source": "'+str(snode.id)+'"  ,'+"\n";
         rjson += '   "target": "'+str(tnode.id)+'"  ,'+"\n";
         rjson += '   "directed": true, '+"\n";
             
         if (verbose > 3):
             print('GndwDBFetchApp:   source node '+str(snode.id));
             
         sdict = self.convert_node_rec_dict(snode, verbose);
         tdict = self.convert_node_rec_dict(tnode, verbose);
         ###sdict = self.find_node_by_id(snode.id, verbose);
         ###tdict = self.find_node_by_id(tnode.id, verbose);
         
         rdict['source'] = sdict;
         rdict['target'] = tdict;
        
         rk = 0;
         
         for rkey in relnode.keys():
              rkeyval = relnode.get(rkey);
              if (rk > 0):
                  rjson += ','+"\n";
              
              if (verbose > 4):
                 print("GNDwFetchApp: relation key:"+str(rkey)+" val:"+str(rkeyval));
                 
              rdict[rkey] = rkeyval;   
              rjson += '   "'+str(rkey)+'": "'+str(rkeyval)+'"';
              rk += 1; 

         rjson += "\n";      
         rjson += '}';
         rdict['jsonstr'] = rjson;
         
         return (rdict);

     
    def     convert_rel_rec_dict_old(self, relnode, verbose):

         if (verbose > 4):
             print(relnode);
             
         rdict = {}; 
             
         ###relnode = record["r"];
         rdict['type'] = relnode.type;
         rdict['id']  = relnode.id;

         if (verbose > 3):
           print("Relationship type: "+str(rdict['type']));
           
         nodes = relnode.nodes;

         if (verbose > 3):
            print(" Relationship Nodes \n");
            print(nodes);

         rdict['snodeid'] = nodes[0];
         rdict['tnodeid'] = nodes[1];
         
         ###print("Source Node id:"+str(snode.id));
         ##print("Target Node id:"+str(tnode.id));
         rjson += '   "directed": true, '+"\n";
         rdict['directed'] = true;
         
         rk = 0;

         for rkey in relnode.keys():
              rkeyval = relnode.get(rkey);

              #if (verbose > 4):
              #   print(" Relationship key key: "+str(rkey));
              #   print(" Relationship val: "+str(rkeyval));

              rdict[rkey] = rkeyval;
              
              #rjson += '   "'+str(rkey)+'": "'+str(rkeyval)+'"';
              rk += 1;

         #rjson += "\n";
         #rjson += '}';
         return (rdict);

     

            
    def            find_edges_return_rec(self, verbose):
            
        with self.driver.session() as session:
            #rjson = " { "+"\n";
            rel_list= {};
            nodelist = {};
            nnum = 0;
            
            query = (
                 "MATCH ()-[r]->() "
                ###"WHERE p.name = $person_name "
                " RETURN r LIMIT 10"
            )
            
            result = session.run(query);
            rnum = 0;
            rjson = '';
            rjson += '   "edges": [ '+"\n";
            
            for record in result:
                if (verbose > 5): 
                   print(record);
                   
                relnode = record["r"];
               
                if (rnum > 0):
                    rjson += ", "+"\n";
                    
                rdict = self.convert_rel_rec_dict(relnode, verbose);
                relid = rdict['id'];
                rel_list[relid] = rdict;
                
                snode = rdict['source'];
                tnode = rdict['target'];
                sid = snode["id"];
                tid = tnode["id"];

                
                if sid in nodelist.keys():
                    if (verbose > 4):
                        print(" GndwDBFetchOp: source node is present "+str(sid));
                        sdict = nodelist[sid];
                        print(sdict);
                    
                else:
                    sdict = self.find_node_by_id(sid, verbose);
                    nodelist[sid] = sdict;
                    if (verbose > 4):
                        print('GndwDBFetchApp: new snode id:'+str(sid));
                        print(sdict);
                    nnum += 1;

                if tid in nodelist.keys():
                    if (verbose > 4):
                        print(" GndwDBFetchOp: target node is present "+str(tid));
                        tdict = nodelist[tid];
                        print(tdict);
                else:
                    tdict = self.find_node_by_id(tid, verbose);
                    nodelist[tid] = tdict;
                    if (verbose > 4):
                        print('GndwDBFetchApp: new tnode id '+str(tid));
                        print(tdict);
                    nnum += 1;

                rj = rdict['jsonstr'];  
                rjson += rj;
                rnum += 1;

            rjson += "\n";
            rjson += "]" ;
           # rjson += '}'+"\n";
           
            if (verbose > 3):
                print('gndwdbFetchOps: Fetch edges #edges: '+str(rnum));
                print(rel_list);
                print('gndwDBFetchOps: Fetch nodes #node: '+str(nnum));
                print(nodelist);
            nj = '   "nodes": [ '+ "\n";
            nnum = 0;
            for nk in nodelist.keys():
                n = nodelist[nk];
                if (nnum > 0):
                    nj += ', '+"\n";
                nj += n['jsonstr'];
                nnum += 1;

            nj += "\n";
            nj += "]" + "\n";
            
            retjson = '{ '+"\n";
            retjson += rjson;
            retjson += ", "+"\n";
            retjson += nj;
            retjson += '}' +"\n";
            
            return(retjson);
    
    
def       gndwdb_metarepo_nodes_fetch_api(verbose):

     graph_connp = gndwdb_neo4j_conn_metarepo(verbose);
     
     fetchApp = gndwdbFetchApp(graph_connp);
     njson = fetchApp.find_nodes_return_rec(verbose);
     #reljson = fetchApp.find_rels_return_rec(verbose);
     #rjson = '{ '."\n";
     #rjson += njson;
     #rjson += ','."\n";
     
     fetchApp.close();
     return njson;

 
def       gndwdb_metarepo_edges_fetch_api(verbose):

     graph_connp = gndwdb_neo4j_conn_metarepo(verbose);

     fetchApp = gndwdbFetchApp(graph_connp);
     rjson = fetchApp.find_edges_return_rec(verbose);
     #reljson = fetchApp.find_rels_return_rec(verbose);
     #rjson = '{ '."\n";
     #rjson += njson;
     #rjson += ','."\n";

     fetchApp.close();
     return rjson;



 
 
if __name__ == "__main__":
    # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.
   # scheme = "bolt"  # Connecting to Aura, use the "neo4j+s" URI scheme
   # host_name = "172.17.0.10"
   # port = 7687
    #url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    #user = "neo4j"
    #password = 'ca$hc0w';
    #app = gndwdbFetchApp(url, user, password)
    #app.create_friendship("Alice", "David")
    ##app.find_person_return_rec("Alice");
    verbose = 5;
    #app.find_nodes_return_rec(verbose);
##    app.find_rels_return_rec(verbose);
    #app.close();
    #njson = gndwdb_metarepo_nodes_fetch_api(verbose);
    #print(njson);
    rjson = gndwdb_metarepo_edges_fetch_api(verbose);
    print(rjson);
    