import unittest
import json
from time import sleep
from app import create_app, db
from app.models import Users, Bucketlists, Items


class UserBucketlistTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        user1 = Users(username="johndoe", email="johnguy@example.com",
                      password="foobar")
        user2 = Users(username="john", email="man@example.com",
                      password="foobar")
        db.session.add_all([user1, user2])
        db.session.commit()
        test_usr = Users.query.filter_by(username="johndoe").first()
        bucket1 = Bucketlists(name="testlist", user_id=test_usr.id)
        db.session.add(bucket1)
        db.session.commit()
        bucket2 = Bucketlists(name="somelist", user_id=test_usr.id)
        db.session.add(bucket2)
        db.session.commit()
        test_lst = Bucketlists.query.filter_by(name="testlist").first()
        item = Items(name="testitem", bucket_id=test_lst.id)
        db.session.add(item)
        db.session.commit()
        self.mime_type = "application/json"
        self.test_token = "JWT " + str(test_usr.generate_confirmation_token())
        self.data_bckt = json.dumps({"name": "testlist 2"})
        self.data_item = json.dumps({"name": "test item here"})
        self.data_item_updt = json.dumps({"status": "done"})
        self.url_bckt = "api/v1/bucketlists"
        self.url_lst = "api/v1/bucketlists/2"
        self.url_item = "api/v1/bucketlists/1/items"
        self.url_item_updt = "api/v1/bucketlists/1/items/1"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_access_bucketlist_no_authorisation(self):
        """
        test that access is denied to view, delete, update bucketlists
        if authentication token isn't provided
        """
        get_response = self.client.get(self.url_bckt, content_type=self.mime_type)
        server_resp = json.loads(get_response.data)
        self.assertEqual(get_response.status_code, 401)
        self.assertEqual("authorisation required", server_resp["message"])

        post_resp = self.client.post(self.url_bckt, data=self.data_bckt,
                                     content_type=self.mime_type)
        srvr_pst_resp = json.loads(post_resp.data)
        self.assertEqual(post_resp.status_code, 401)
        self.assertEqual("authorisation required", srvr_pst_resp["message"])

        get_lst_resp = self.client.get(self.url_lst, content_type=self.mime_type)
        srvr_lst_resp = json.loads(get_lst_resp.data)
        self.assertEqual(get_lst_resp.status_code, 401)
        self.assertEqual("authorisation required", srvr_lst_resp["message"])

        del_lst_resp = self.client.delete(self.url_lst, content_type=self.mime_type)
        srvr_del_resp = json.loads(del_lst_resp.data)
        self.assertEqual(del_lst_resp.status_code, 401)
        self.assertEqual("authorisation required", srvr_del_resp["message"])

        post_lst_resp = self.client.post(self.url_item, data=self.data_item,
                                         content_type=self.mime_type)
        srvr_pstitm_resp = json.loads(post_lst_resp.data)
        self.assertEqual(post_lst_resp.status_code, 401)
        self.assertEqual("authorisation required", srvr_pstitm_resp["message"])

        post_itmupdt_resp = self.client.post(self.url_item_updt,
                                             data=self.data_item_updt,
                                             content_type=self.mime_type)
        srvr_itmupdt_resp = json.loads(post_itmupdt_resp.data)
        self.assertEqual(post_itmupdt_resp.status_code, 401)
        self.assertEqual("authorisation required",
                         srvr_itmupdt_resp["message"])

    def test_token_expires(self):
        """
        test that the token generated expires
        """
        test_usr = Users.query.filter_by(username="johndoe").first()
        # token expires in 1sec
        token = "JWT " + str(test_usr.generate_confirmation_token(1))
        header = {"Authorization": token}
        sleep(1.1)
        get_resp = self.client.get(self.url_bckt, content_type=self.mime_type,
                                   headers=header)
        srvr_get_resp = json.loads(get_resp.data)
        self.assertEqual(get_resp.status_code, 401)
        self.assertEqual("token expired", srvr_get_resp["message"])

    def test_view_or_filter_bucketlists(self):
        """
        test to get all bucketlists and filter to get specific bucketlist
        """
        header = {"Authorization": self.test_token}
        get_bcktlist = self.client.get(self.url_bckt, content_type=self.mime_type,
                                       headers=header)
        server_resp = json.loads(get_bcktlist.data)
        self.assertEqual(get_bcktlist.status_code, 200)
        self.assertEqual("testlist", server_resp[0]["name"])
        self.assertEqual("somelist", server_resp[1]["name"])
    #
    # def test_edit_delete_bucketlists(self):
    #     """ test that bucketlists can be edited and deleted"""
    #     header = {"Authorization": self.test_token}
    #     data = json.dumps({"name": "altered list"})
    #     edit_bcklst = self.client.put(self.url_lst, data=data,
    #                                   content_type=self.mime_type, header=header)
    #     server_resp = json.loads(edit_bcktlst.data)
    #     self.assertEqual(edit_bcktlst.status_code, 200)
    #     changedbckt = Bucketlists.query.filter_by(id=2).first()
    #     self.assertEqual("altered list", changedbckt.name)
    #
    #     del_bcklst = self.client.delete(self.url_lst, content_type=self.mime_type,
    #                                     header=header)
    #     server_resp = json.loads(del_bcklst.data)
    #     self.assertEqual(del_bcklst.status_code, 200)
    #     self.assertEqual("bucketlist: altered list deleted",
    #                      server_resp["message"])
    #
    # def test_edit_bucketlist_missing_arguments(self):
    #     """ test that editing a bucketlist requires a name argument"""
    #     header = {"Authorization": self.test_token}
    #     edit_bcklst = self.client.put(self.url_lst, content_type=self.mime_type,
    #                                   header=header)
    #     server_resp = json.loads(edit_bcktlst.data)
    #     self.assertEqual(edit_bcktlst.status_code, 400)
    #     self.assertEqual("missing argument", server_resp["message"])
    #
    # def test_view_bucketlists_not_existing(self):
    #     """ view bucketlists for User that hasn't created any bucketlists yet
    #     or when a user tries to edit nonexistant bucketlist
    #     """
    #     usr = Users.query.filter_by(username='john').first()
    #     testtkn = "JWT " + usr.generate_confirmation_token()
    #     header = {"Authorization": testtkn}
    #     get_bcktlist = self.client.get(self.url_bckt, content_type=self.mime_type,
    #                                    header=header)
    #     server_resp = json.loads(get_bcktlist.data)
    #     self.assertEqual(get_bcktlist.status_code, 200)
    #     self.assertEqual("bucketlist doesn't exist", server_resp["message"])
    #
    #     header = {"Authorization": self.test_token}
    #     url_mia = "api/v1/bucketlists/20"
    #     data = json.dumps({"name": "altered list"})
    #     edit_bcklst = self.client.put(url_mia, data=data,
    #                                   content_type=self.mime_type, header=header)
    #     server_resp = json.loads(edit_bcklst.data)
    #     self.assertEqual(edit_bcklst.status_code, 404)
    #     self.assertEqual("bucketlist doesn't exist", server_resp["message"])
