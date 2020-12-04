#!/usr/bin/python3
"""
Ubuntu charm functional test using Zaza. Take note that the Ubuntu
charm does not have any relations or config options to exercise.
"""

import unittest
import zaza
import logging
import socket
import sctp
import netifaces
import zaza.model as model
import pymongo
from juju.model import Model
import zaza.charm_lifecycle.utils as lifecycle_utils

class BasicDeployment(unittest.TestCase):

    def create_connection(self):
        try:
            for unit in zaza.model.get_units('db'):
                logging.info("Checking if the unit db is active: {}".format(unit.entity_id))
                logging.info("checking for mongo db connection....")
                db_ip = model.get_status().applications["db"]["units"][unit.entity_id]["address"]
                myclient = pymongo.MongoClient("mongodb://"+db_ip+":27017/")
                logging.info("Mongodb connected successfully !!!")
        except:
            logging.info("Could not connect to Mongodb")
        return myclient
    
    def mongo_read_data(self, db_name, coll_name, myclient):
        core_db = myclient[db_name]
        collection = core_db[coll_name]
        cursor = collection.find()
        return cursor

    def test1_mongo_listcollections(self):
        """ ***** list collections in mongodb *****"""
        collection = []
        db_name = "free5gc"
        myclient = BasicDeployment.create_connection(self)
        dblist = myclient.list_database_names()
        if db_name in dblist:
            logging.info("free5gc Database Exists")
            core_db = myclient[db_name]
            for coll in core_db.list_collection_names():
                collection.append(coll)
            logging.info("collection list {}".format(collection))
        else:
            logging.info("Database doesnot exists")
        myclient.close()

    def test2_mongo_insert(self):
        """ ****** Insert record in mongodb ***** """ 
        db_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007487"
        myclient = BasicDeployment.create_connection(self)
        core_db = myclient[db_name]
        collection = core_db[coll_name]
        ins_rec = { "subscCats" : [ db_name ], "ueId" : ue_id }
        logging.info("Record to be inserted {}".format(ins_rec))
        collection.insert_one(ins_rec)
        logging.info("Data inserted successfully !!")
        cursor = BasicDeployment.mongo_read_data(self, db_name, coll_name, myclient)
        for record in cursor:
            logging.info("Reading the inserted document from mongodb {}".format(record))
        logging.info("To check inserted record and retrieved document are same ...")
        self.assertEqual(ins_rec, record) 
        myclient.close()
    
    def test4_mongo_delete(self):
        """ ***** Delete record in mongodb ***** """
        db_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007488"
        myclient = BasicDeployment.create_connection(self)
        core_db = myclient[db_name]
        collection = core_db[coll_name]
        logging.info("Deleting record based on UE-Id")
        del_rec = { "ueId" : ue_id }
        logging.info("Record to be deleted {}".format(del_rec))
        result = collection.delete_one(del_rec)
        logging.info("Data deleted {}".format(result.deleted_count))
        logging.info("Data deleted successfully !!")
        cursor = BasicDeployment.mongo_read_data(self, db_name, coll_name, myclient)
        if core_db.collection.count_documents({ 'ueId': ue_id }, limit = 1) == 0:
            logging.info("Reading the deleted document ue_id: {}".format(ue_id))
            self.assertEqual(1,result.deleted_count)
        else:
            logging.info("Document present")
        myclient.close()

    def test3_mongo_update(self):
        """ ***** Update record in mongodb ***** """
        db_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007487"
        myclient = BasicDeployment.create_connection(self)
        core_db = myclient[db_name]
        collection = core_db[coll_name]
        myquery = { "ueId" : ue_id }
        update_rec = { "$set": { "ueId": "imsi-2089300007488" } }
        result = collection.update_one(myquery, update_rec)
        logging.info("Data updated successfully !!")
        cursor = BasicDeployment.mongo_read_data(self, db_name, coll_name, myclient)
        for record in cursor:
            logging.info("updated document {}".format(record))
            self.assertEqual(1, result.modified_count)
            
        myclient.close()

    def test5_sctp_connection_amf(self):
        """ ***** checking sctp transport connection in amf ***** """
        amf_sctp_port = 38412
        sock = sctp.sctpsocket_tcp(socket.AF_INET)
        for unit in zaza.model.get_units('amf'):
            amf_ip = model.get_status().applications["amf"]["units"][unit.entity_id]["address"]
            result = sock.connect_ex((amf_ip, amf_sctp_port))
            if result == 0:
                logging.info("SCTP Transport is Listening ...")
            else:
                logging.info("SCTP Transport is not available")
            self.assertEqual(result,0)
    
    def test6_upfgtp_connection(self):
        """ ***** checking gtp connection in upf ***** """
        upf_gtp_port = 2152
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for unit in zaza.model.get_units('upf1'):
            upf1_ip = model.get_status().applications["upf1"]["units"][unit.entity_id]["address"]
            result = sock.connect_ex((upf1_ip, upf_gtp_port))
            if result == 0:
                logging.info("GTP Transport is Listening ...")
            else:
                logging.info("GTP Transport is not available")
            self.assertEqual(result,0)

