#!/usr/bin/python3
"""
Ubuntu charm functional test using Zaza. Take note that the Ubuntu
charm does not have any relations or config options to exercise.
"""

import unittest
import logging
import socket
import sctp
import zaza.model as model
import pymongo


class BasicDeployment(unittest.TestCase):
    """ class defines functional testing of all charms """

    def create_connection(self):
        """ create mongo mongodb connection """
        try:
            for unit in model.get_units("mongodb"):
                logging.info(
                    "Checking if the unit mongodb is active: %s", unit.entity_id
                )
                logging.info("checking for mongodb connection....")
                mongodb_ip = model.get_status().applications["mongodb"]["units"][
                    unit.entity_id
                ]["address"]
                myclient = pymongo.MongoClient(f"mongodb://{mongodb_ip}:27017/")
                logging.info("Mongodb connected successfully !!!")
        except pymongo.errors.ConnectionFailure:
            logging.info("Could not connect to Mongomongodb")
        return myclient

    def mongo_read_data(
        self, mongodb_name, coll_name, myclient
    ):  # pylint disable=no-self-use
        """ Reading data from mongodb """
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        cursor = collection.find()
        return cursor

    def test1_mongo_listcollections(self):
        """ ***** list collections in mongodb *****"""
        collection = []
        mongodb_name = "free5gc"
        myclient = BasicDeployment.create_connection(self)
        mongodblist = myclient.list_database_names()
        if mongodb_name in mongodblist:
            logging.info("free5gc Database Exists")
            core_mongodb = myclient[mongodb_name]
            for coll in core_mongodb.list_collection_names():
                collection.append(coll)
            logging.info("collection list %s", collection)
        else:
            logging.info("Database doesnot exists")
        myclient.close()

    def test2_mongo_insert(self):
        """ ****** Insert record in mongomongodb ***** """
        mongodb_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007487"
        record = None
        myclient = BasicDeployment.create_connection(self)
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        ins_rec = {"subscCats": [mongodb_name], "ueId": ue_id}
        collection.insert_one(ins_rec)
        cursor = BasicDeployment.mongo_read_data(
            self, mongodb_name, coll_name, myclient
        )
        for record in cursor:
            logging.info("Reading the inserted document from mongodb %s", record)
        self.assertEqual(ins_rec, record)
        myclient.close()

    def test4_mongo_delete(self):
        """ ***** Delete record in mongomongodb ***** """
        mongodb_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007488"
        myclient = BasicDeployment.create_connection(self)
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        del_rec = {"ueId": ue_id}
        result = collection.delete_one(del_rec)
        BasicDeployment.mongo_read_data(self, mongodb_name, coll_name, myclient)
        if core_mongodb.collection.count_documents({"ueId": ue_id}, limit=1) == 0:
            logging.info("Reading the deleted document ue_id: %s", ue_id)
            self.assertEqual(1, result.deleted_count)
        else:
            logging.info("Document present")
        myclient.close()

    def test3_mongo_update(self):
        """ ***** Update record in mongomongodb ***** """
        mongodb_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007487"
        myclient = BasicDeployment.create_connection(self)
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        myquery = {"ueId": ue_id}
        update_rec = {"$set": {"ueId": "imsi-2089300007488"}}
        result = collection.update_one(myquery, update_rec)
        cursor = BasicDeployment.mongo_read_data(
            self, mongodb_name, coll_name, myclient
        )
        for record in cursor:
            logging.info("updated document %s", record)
            self.assertEqual(1, result.modified_count)
        myclient.close()

    def test5_sctp_connection_amf(self):
        """ ***** checking sctp transport connection in amf ***** """
        amf_sctp_port = 38412
        sock = sctp.sctpsocket_tcp(socket.AF_INET)
        for unit in model.get_units("amf"):
            amf_ip = model.get_status().applications["amf"]["units"][unit.entity_id][
                "address"
            ]
            result = sock.connect_ex((amf_ip, amf_sctp_port))
            if result == 0:
                logging.info("SCTP Transport is Listening ...")
            else:
                logging.info("SCTP Transport is not available")
            self.assertEqual(result, 0)

    def test6_upfgtp_connection(self):
        """ ***** checking gtp connection in upf ***** """
        upf_gtp_port = 2152
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for unit in model.get_units("upf1"):
            upf1_ip = model.get_status().applications["upf1"]["units"][unit.entity_id][
                "address"
            ]
            result = sock.connect_ex((upf1_ip, upf_gtp_port))
            if result == 0:
                logging.info("GTP Transport is Listening ...")
            else:
                logging.info("GTP Transport is not available")
            self.assertEqual(result, 0)
