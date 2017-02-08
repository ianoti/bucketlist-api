from tests.setup_test import BaseTestClass
from app.models import User, Bucketlist, Item

import json


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
        self.assertEqual("johndoe", bckt_data["created_by"])

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

        nobckt_del = self.app.delete("/api/v1/bucketlists/1",
                                     headers=self.header)
        nobckt_del_data = json.loads(nobckt_del.data)
        self.assertEqual(404, nobckt_del.status_code)
        self.assertIn("bucketlist not found", nobckt_del_data["message"])

        bad_del = self.app.delete("/api/v1/bucketlists", headers=self.header)
        bad_del_data = json.loads(bad_del.data)
        self.assertEqual(400, bad_del.status_code)
        self.assertEqual("bad request", bad_del_data["message"])

    def test_update_bucketlist(self):
        """ check that bucketlist updates"""
        data = json.dumps({"name": "updated testlist"})
        data_empty = json.dumps({})
        data_noname = json.dumps({"name": ""})
        data_space = json.dumps({"name": " "})

        valid = self.app.put("/api/v1/bucketlists/1", data=data,
                             headers=self.header, content_type=self.mime_type)
        valid_data = json.loads(valid.data)

        no_bucket = self.app.put("/api/v1/bucketlists/13", data=data,
                                 headers=self.header,
                                 content_type=self.mime_type)
        no_bucket_data = json.loads(no_bucket.data)

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

        self.assertListEqual([200, 400, 400, 400, 404],
                             [valid.status_code, blank.status_code,
                              noname.status_code, name_space.status_code,
                              no_bucket.status_code])
        self.assertIn("bucketlist not found", no_bucket_data["message"])
        self.assertIn("has been updated", valid_data["message"])
        self.assertIn("name required", blank_data["message"]["name"])
        self.assertIn("no blank fields", noname_data["message"])
        self.assertIn("name is invalid", name_space_data["message"])
        # assert that modified date is more current
        bckt = Bucketlist.query.filter_by(id=1).first()
        self.assertTrue(bckt.date_modified > bckt.date_created)

    def test_user_can_not_access_other_users_buckets(self):
        """ the logged in user can't access anothers users bucketlists"""
        # log in new user and use token
        data = json.dumps({"username": "janedoe", "password": "foobar"})
        resp = self.app.post("/api/v1/auth/login", data=data,
                             content_type=self.mime_type)
        respdata = json.loads(resp.data)
        token = "Bearer " + respdata["token"]
        headerjane = {"Authorization": token}
        # create jane's bucketlist
        new_bckt = json.dumps({"name": "jane's list"})
        bckt = self.app.post("api/v1/bucketlists", data=new_bckt,
                             headers=headerjane, content_type=self.mime_type)
        self.assertEqual(201, bckt.status_code)
        self.assertEqual(2, Bucketlist.query.count())
        # john's attempted access
        jhn_bckt = self.app.get("api/v1/bucketlists/2", headers=self.header)
        jhn_bcktdata = json.loads(jhn_bckt.data)
        self.assertEqual(404, jhn_bckt.status_code)
        self.assertIn("bucketlist not found", jhn_bcktdata["message"])

    def test_bad_post_route(self):
        """test won't post if id is provided"""
        name = json.dumps({"name": "something to do"})
        resp = self.app.post("/api/v1/bucketlists/1", data=name,
                             headers=self.header, content_type=self.mime_type)
        resp_data = json.loads(resp.data)
        self.assertEqual(400, resp.status_code)
        self.assertEqual("bad request", resp_data["message"])

    def test_search_bucketlist(self):
        """ test that the search functionality works for bucketlists"""
        # any buckets with list in their name
        search = self.app.get("/api/v1/bucketlists?q=list",
                              headers=self.header)
        search_data = json.loads(search.data)
        self.assertEqual(200, search.status_code)
        self.assertEqual("testlist", search_data[0]["name"])
        self.assertEqual("johndoe", search_data[0]["created_by"])

        missing = self.app.get("/api/v1/bucketlists?q=missing",
                               headers=self.header)
        missing_data = json.loads(missing.data)
        self.assertEqual(404, missing.status_code)
        self.assertIn("that name not found", missing_data["message"])

    def test_pagination_limit_for_bucketlist(self):
        """ test that pagination and limit arguments work for get bucketlists
        url"""
        # add bucketlists for testing in addition to one from setup
        name_1 = json.dumps({"name": "lister"})
        self.app.post("/api/v1/bucketlists", data=name_1, headers=self.header,
                      content_type=self.mime_type)
        name_2 = json.dumps({"name": "bloom"})
        self.app.post("/api/v1/bucketlists", data=name_2, headers=self.header,
                      content_type=self.mime_type)

        page_1 = self.app.get("/api/v1/bucketlists?page=1&limit=1",
                              headers=self.header)
        page_1_data = json.loads(page_1.data)
        page_2 = self.app.get("/api/v1/bucketlists?page=2&limit=1",
                              headers=self.header)
        page_2_data = json.loads(page_2.data)
        page_3 = self.app.get("/api/v1/bucketlists?page=3&limit=1",
                              headers=self.header)
        page_3_data = json.loads(page_3.data)
        page_all = self.app.get("/api/v1/bucketlists?page=1&limit=3",
                                headers=self.header)
        page_all_data = json.loads(page_all.data)

        self.assertListEqual([200, 200, 200],
                             [page_1.status_code, page_2.status_code,
                              page_3.status_code])
        self.assertListEqual(["testlist", "lister", "bloom"],
                             [page_1_data[0]["name"], page_2_data[0]["name"],
                              page_3_data[0]["name"]])
        self.assertEqual(3, len(page_all_data))
