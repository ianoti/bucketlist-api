from tests.setup_test import BaseTestClass
from app.models import User, Bucketlist, Item

import json


class ItemTest(BaseTestClass):
    """ the tests concerning items C.R.U.D operations """

    def test_add_item(self):
        """ test for successful addition of an item """
        old_count = Item.query.count()
        item_name = json.dumps({"name": "something to do"})
        resp = self.app.post("/api/v1/bucketlists/1/items", data=item_name,
                             headers=self.header, content_type=self.mime_type)
        resp_data = json.loads(resp.data)

        resp_nobckt = self.app.post("/api/v1/bucketlists/23/items",
                                    data=item_name, headers=self.header,
                                    content_type=self.mime_type)
        resp_nobckt_data = json.loads(resp_nobckt.data)

        new_count = Item.query.count()
        self.assertEqual(1, new_count-old_count)
        self.assertListEqual([201, 404],
                             [resp.status_code, resp_nobckt.status_code])
        self.assertIn("bucketlist not found", resp_nobckt_data["message"])
        self.assertEqual("item has been added to the bucketlist",
                         resp_data["message"])

    def test_add_item_wrong_inputs(self):
        """ test that blank spaces, empty arguments not accepted when adding
        item"""
        blank = json.dumps({})
        empty = json.dumps({"name": ""})
        space = json.dumps({"name": " "})

        resp_blank = self.app.post("/api/v1/bucketlists/1/items",
                                   data=blank, headers=self.header,
                                   content_type=self.mime_type)
        resp_empty = self.app.post("/api/v1/bucketlists/1/items",
                                   data=empty, headers=self.header,
                                   content_type=self.mime_type)
        resp_space = self.app.post("/api/v1/bucketlists/1/items",
                                   data=space, headers=self.header,
                                   content_type=self.mime_type)
        resp_blank_data = json.loads(resp_blank.data)
        resp_empty_data = json.loads(resp_empty.data)
        resp_space_data = json.loads(resp_space.data)

        self.assertEqual(1, Item.query.count())
        self.assertListEqual([400, 400, 400],
                             [resp_blank.status_code, resp_empty.status_code,
                              resp_space.status_code])
        self.assertIn("name required", resp_blank_data["message"]["name"])
        self.assertEqual("no blank fields allowed", resp_empty_data["message"])
        self.assertEqual("name is invalid", resp_space_data["message"])

    def test_delete_item(self):
        """ test that item is deleted """
        old = Item.query.count()
        resp = self.app.delete("/api/v1/bucketlists/1/items/1",
                               headers=self.header)
        resp_data = json.loads(resp.data)
        new = Item.query.count()
        self.assertEqual(1, old-new)
        self.assertEqual(200, resp.status_code)
        self.assertIn("deleted successfully", resp_data["message"])

        noitem_resp = self.app.delete("/api/v1/bucketlists/1/items/1",
                                      headers=self.header)
        noitem_resp_data = json.loads(noitem_resp.data)
        self.assertEqual(404, noitem_resp.status_code)
        self.assertIn("item not found", noitem_resp_data["message"])

    def test_update_item(self):
        """ test that item can be updated and that at least
        one argument must be provided"""
        valid_data = json.dumps({"name": "updated list", "status": "true"})
        inv_status = json.dumps({"status": "boom"})
        empty_name = json.dumps({"name": "", "status": "true"})
        space_name = json.dumps({"name": " ", "status": "true"})
        blank_data = json.dumps({})

        resp_valid = self.app.put("/api/v1/bucketlists/1/items/1",
                                  data=valid_data, headers=self.header,
                                  content_type=self.mime_type)
        resp_blank = self.app.put("/api/v1/bucketlists/1/items/1",
                                  data=blank_data, headers=self.header,
                                  content_type=self.mime_type)
        resp_invstatus = self.app.put("/api/v1/bucketlists/1/items/1",
                                      data=inv_status, headers=self.header,
                                      content_type=self.mime_type)
        resp_invurl = self.app.put("/api/v1/bucketlists/1/items",
                                   data=valid_data, headers=self.header,
                                   content_type=self.mime_type)
        resp_empty_name = self.app.put("/api/v1/bucketlists/1/items/1",
                                       data=empty_name, headers=self.header,
                                       content_type=self.mime_type)
        resp_space_name = self.app.put("/api/v1/bucketlists/1/items/1",
                                       data=space_name, headers=self.header,
                                       content_type=self.mime_type)

        resp_valid_data = json.loads(resp_valid.data)
        resp_blank_data = json.loads(resp_blank.data)
        resp_invstatus_data = json.loads(resp_invstatus.data)
        resp_invurl_data = json.loads(resp_invurl.data)
        resp_empty_name_data = json.loads(resp_empty_name.data)
        resp_space_name_data = json.loads(resp_space_name.data)

        item_check = Item.query.filter_by(id=1).first()
        self.assertEqual("updated list", item_check.name)
        self.assertTrue(item_check.status)
        self.assertTrue(item_check.date_modified > item_check.date_created)
        self.assertListEqual([200, 400, 400, 400, 400, 400],
                             [resp_valid.status_code, resp_blank.status_code,
                              resp_invstatus.status_code,
                              resp_invurl.status_code,
                              resp_empty_name.status_code,
                              resp_space_name.status_code])
        self.assertEqual("item has been updated", resp_valid_data["message"])
        self.assertEqual("status required as true or false",
                         resp_invstatus_data["message"]["status"])
        self.assertEqual("provide at least one parameter to change",
                         resp_blank_data["message"])
        self.assertEqual("bad request", resp_invurl_data["message"])
        self.assertEqual("name is invalid",
                         resp_space_name_data["message"])
        self.assertEqual("name can't be blank",
                         resp_empty_name_data["message"])
        resp_nobckt = self.app.put("/api/v1/bucketlists/34/items/1",
                                   data=valid_data, headers=self.header,
                                   content_type=self.mime_type)
        self.assertEqual(404, resp_nobckt.status_code)

    def test_bad_request(self):
        """ test that put command exceptions are handled"""
        valid_data = json.dumps({"name": "updated list", "status": "true"})
        resp_invalid = self.app.put("/api/v1/bucketlists/1/items",
                                    data=valid_data, headers=self.header,
                                    content_type=self.mime_type)
        resp_invalid_data = json.loads(resp_invalid.data)
        self.assertEqual(resp_invalid.status_code, 400)
        self.assertEqual("bad request", resp_invalid_data["message"])
