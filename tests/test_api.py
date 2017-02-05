from setup_test import BaseTestClass
from app.models import User, Bucketlist, Item

import json
from time import sleep


class BucketlistsTest(BaseTestClass):
    """ the tests concerning the bucketlist endpoint C.R.U.D operations"""

    def test_authorisation_required(self):
        """ test that access is denied if no token is given """
        get_bckt = self.app.get("/api/v1/bucketlists")
        get_bcktdata = json.loads(get_bckt.data)
        pst_item = self.app.post("/api/v1/bucketlists/1/items")
        pst_itemdata = json.loads(pst_item.data)
        self.assertListEqual([401, 401], [get_bckt.status_code,
                                          pst_item.status_code])
        self.assertListEqual([Bucketlist.query.count(), Item.query.count()],
                             [1, 1])
        self.assertEqual("Access denied", get_bcktdata["message"])
        self.assertEqual("Access denied", pst_itemdata["message"])

    def test_token_grants_access(self):
        """ test that the authentication token grants access"""
        resp = self.app.get("/api/v1/bucketlists", headers=self.header)
        self.assertEqual(200, resp.status_code)

    def test_successfully_add_view_bucketlist(self):
        """ test that bucketlits can be added and viewed"""
        old = Bucketlist.query.count()

        data = json.dumps({"name": "testbucket"})
        resp = self.app.post("/api/v1/bucketlists", data=data,
                             headers=self.header, content_type=self.mime_type)
        resp_data = json.loads(resp.data)
        new = Bucketlist.query.count()
        self.assertEqual(1, new-old)
        self.assertEqual(201, resp.status_code)
        self.assertIn("testbucket", resp_data["message"])

        respnew = self.app.get("api/v1/bucketlists", headers=self.header)
        resp_datnew = json.loads(respnew.data)
        self.assertEqual(200, respnew.status_code)
        self.assertListEqual(["testlist", "testbucket"],
                             [resp_datnew[0]["name"], resp_datnew[1]["name"]])

        bckt = self.app.get("api/v1/bucketlists/2", headers=self.header)
        bckt_data = json.loads(bckt.data)
        self.assertEqual(200, respnew.status_code)
        self.assertEqual("testbucket", bckt_data["name"])

        bckt_absent = self.app.get("api/v1/bucketlists/12",
                                   headers=self.header)

        bckt_absent_data = json.loads(bckt_absent.data)
        self.assertEqual(404, bckt_absent.status_code)
        self.assertIn("not found", bckt_absent_data["message"])

    def test_inputs_required_to_post(self):
        """test that user inputs to make the bucketlist are validated"""
        old = Bucketlist.query.count()
        no_det = json.dumps({})
        response = self.app.post("api/v1/bucketlists", data=no_det,
                                 headers=self.header,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        new = Bucketlist.query.count()
        self.assertEqual("bucketlist name required",
                         resp_data["message"]["name"])

        bl_name = json.dumps({"name": ""})
        resp_bl_name = self.app.post("api/v1/bucketlists", data=bl_name,
                                     headers=self.header,
                                     content_type=self.mime_type)
        new_bl = Bucketlist.query.count()
        resp_bl_name_data = json.loads(resp_bl_name.data)
        self.assertEqual("no blank fields allowed",
                         resp_bl_name_data["message"])

        sp_name = json.dumps({"name": " "})
        resp_sp_name = self.app.post("api/v1/bucketlists", data=sp_name,
                                     headers=self.header,
                                     content_type=self.mime_type)
        sp_namedata = json.loads(resp_sp_name.data)
        new_sp = Bucketlist.query.count()
        self.assertEqual("name is invalid", sp_namedata["message"])

        self.assertListEqual([400, 400, 400],
                             [response.status_code, resp_bl_name.status_code,
                              resp_sp_name.status_code])
        self.assertListEqual([0, 0, 0], [new-old, new_bl-old, new_sp-old])

    def test_deleting_bucketlist(self):
        """ test that bucketlist can be viewed
        deleted and this cascades to the items on delete"""
        oldbcnt = Bucketlist.query.count()
        olditcnt = Item.query.count()
        bckt_del = self.app.delete("/api/v1/bucketlists/1",
                                   headers=self.header)
        bckt_deldata = json.loads(bckt_del.data)
        newbcnt = Bucketlist.query.count()
        newitcnt = Item.query.count()
        self.assertEqual(bckt_del.status_code, 200)
        self.assertListEqual([1, 1], [oldbcnt-newbcnt, olditcnt-newitcnt])
        self.assertIn("testlist has been deleted", bckt_deldata["message"])

    def test_update_bucketlist(self):
        """ check that bucketlist updates"""
        data = json.dumps({"name": "updated testlist"})
        data_empty = json.dumps({})
        data_noname = json.dumps({"name": ""})
        data_space = json.dumps({"name": " "})

        valid = self.app.put("/api/v1/bucketlists/1", data=data,
                             headers=self.header, content_type=self.mime_type)
        valid_data = json.loads(valid.data)

        blank = self.app.put("/api/v1/bucketlists/1", data=data_empty,
                             headers=self.header, content_type=self.mime_type)
        blank_data = json.loads(blank.data)

        noname = self.app.put("/api/v1/bucketlists/1", data=data_noname,
                              headers=self.header, content_type=self.mime_type)
        noname_data = json.loads(noname.data)

        name_space = self.app.put("/api/v1/bucketlists/1", data=data_space,
                                  headers=self.header,
                                  content_type=self.mime_type)
        name_space_data = json.loads(name_space.data)

        self.assertListEqual([200, 400, 400, 400],
                             [valid.status_code, blank.status_code,
                              noname.status_code, name_space.status_code])
        self.assertIn("has been updated", valid_data["message"])
        self.assertIn("name required", blank_data["message"]["name"])
        self.assertIn("no blank fields", noname_data["message"])
        self.assertIn("name is invalid", name_space_data["message"])
