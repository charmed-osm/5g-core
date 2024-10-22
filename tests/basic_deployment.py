#!/usr/bin/python3
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##

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


def create_connection():
    """ create mongo mongodb connection """
    try:
        for unit in model.get_units("mongodb"):
            logging.info("Checking if the unit mongodb is active: %s", unit.entity_id)
            logging.info("checking for mongodb connection....")
            mongodb_ip = model.get_status().applications["mongodb"]["units"][
                unit.entity_id
            ]["address"]
            myclient = pymongo.MongoClient("mongodb://" + mongodb_ip + ":27017/")
            logging.info("Mongodb connected successfully !!!")
    except pymongo.errors.ConnectionFailure:
        logging.info("Could not connect to Mongomongodb")
    return myclient


def mongo_read_data(mongodb_name, coll_name, myclient):
    """ Reading data from mongodb """
    core_mongodb = myclient[mongodb_name]
    collection = core_mongodb[coll_name]
    cursor = collection.find()
    return cursor


class BasicDeployment(unittest.TestCase):
    """ class defines functional testing of all charms """

    def test1_mongo_insert(self):
        """ ****** Insert record in mongomongodb ***** """
        mongodb_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007487"
        record = None
        myclient = create_connection()
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        ins_rec = {"subscCats": [mongodb_name], "ueId": ue_id}
        logging.info("Record to be inserted %s", ins_rec)
        collection.insert_one(ins_rec)
        logging.info("Data inserted successfully !!")
        cursor = mongo_read_data(mongodb_name, coll_name, myclient)
        for record in cursor:
            logging.info("Reading the inserted document from mongodb %s", record)
        logging.info("To check inserted record and retrieved document are same ...")
        self.assertEqual(ins_rec, record)
        myclient.close()

    def test3_mongo_delete(self):
        """ ***** Delete record in mongomongodb ***** """
        mongodb_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007488"
        myclient = create_connection()
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        logging.info("Deleting record based on UE-Id")
        del_rec = {"ueId": ue_id}
        logging.info("Record to be deleted %s", del_rec)
        result = collection.delete_one(del_rec)
        logging.info("Data deleted %d ", result.deleted_count)
        logging.info("Data deleted successfully !!")
        mongo_read_data(mongodb_name, coll_name, myclient)
        if core_mongodb.collection.count_documents({"ueId": ue_id}, limit=1) == 0:
            logging.info("Reading the deleted document ue_id: %s", ue_id)
            self.assertEqual(1, result.deleted_count)
        else:
            logging.info("Document present")
        myclient.close()

    def test2_mongo_update(self):
        """ ***** Update record in mongomongodb ***** """
        mongodb_name = "free5gc"
        coll_name = "policyData.ues.amData"
        ue_id = "imsi-2089300007487"
        myclient = create_connection()
        core_mongodb = myclient[mongodb_name]
        collection = core_mongodb[coll_name]
        myquery = {"ueId": ue_id}
        update_rec = {"$set": {"ueId": "imsi-2089300007488"}}
        result = collection.update_one(myquery, update_rec)
        logging.info("Data updated successfully !!")
        cursor = mongo_read_data(mongodb_name, coll_name, myclient)
        for record in cursor:
            logging.info("updated document %s", record)
            self.assertEqual(1, result.modified_count)
        myclient.close()

    def test4_sctp_connection_amf(self):
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

    def test5_upfgtp_connection(self):
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
