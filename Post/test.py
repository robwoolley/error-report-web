import unittest
import urllib
import json
from django.test import Client
from Post.models import BuildFailure, Build


def delete_data_after (func):
    def wrap(*args, **kwargs):
        func(*args, **kwargs)

        self = args[0]

        bfo = BuildFailure.objects.all()
        bo = Build.objects.all()

        self.assertEqual(bfo.count(), 1)
        self.assertEqual(bo.count(), 1)

        bfo.delete()
        bo.delete()

    return wrap


class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="testhost")
        self.client_0_3 = Client(HTTP_HOST="testhost", HTTP_USER_AGENT="send-error-report/0.3")

    def test_links(self):
        response = self.client.get('/Errors/Latest/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/Statistics/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/Errors/Build/1/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/Errors/Details/1/')
        self.assertEqual(response.status_code, 200)

    # Opening test-payload.json and submitting it to server
    # expecting json response 1st item inserted to db
    @delete_data_after
    def test_submission(self):

        with open("test-data/test-payload.json") as f:
            data = f.read()


        data = urllib.urlencode({'data': data})

        response = self.client.post("/ClientPost/",
                                    data,
                                    "application/json")

        self.assertEqual(response.status_code, 200)
        # Now let's see if the data entered the db
        data_ob = BuildFailure.objects.get()

        self.assertEqual("/Build/"+str(data_ob.BUILD.id) in response.content, True)

        self.assertEqual("tester" in data_ob.BUILD.NAME, True)


    @delete_data_after
    def test_submission_0_3(self):
        with open("test-data/test-payload.json") as f:
            data = f.read()

        response = self.client_0_3.post("/ClientPost/",
                                        data,
                                        "application/json")

        self.assertEqual(response.status_code, 200)

        # Now let's see if the data entered the db
        data_ob = BuildFailure.objects.get()

        self.assertEqual("/Build/"+str(data_ob.BUILD.id) in response.content, True)

        self.assertEqual("tester" in data_ob.BUILD.NAME, True)

    @delete_data_after
    def test_submission_ret_json(self):

        with open("test-data/test-payload.json") as f:
            data = f.read()

        data = urllib.urlencode({'data': data})

        response = self.client.post("/ClientPost/JSON/",
                                    data,
                                    "application/json")

        self.assertEqual(response.status_code, 200)

        ret = json.loads(response.content)

        # Now let's see if the data entered the db
        data_ob = BuildFailure.objects.get()

        self.assertEqual(ret['build_id'], data_ob.BUILD.id)
        fails = ret['failures']

        self.assertEqual(fails[0]['id'], data_ob.id)
        self.assertEqual("tester" in data_ob.BUILD.NAME, True)


    @delete_data_after
    def test_submission_ret_json_0_3(self):

        with open("test-data/test-payload.json") as f:
            data = f.read()

        response = self.client_0_3.post("/ClientPost/JSON/",
                                        data,
                                        "application/json")

        self.assertEqual(response.status_code, 200)

        ret = json.loads(response.content)

        data_ob = BuildFailure.objects.get()
        self.assertEqual(ret['build_id'], data_ob.BUILD.id)
        fails = ret['failures']

        self.assertEqual(fails[0]['id'], data_ob.id)

        # Now let's see if the data entered the db
        self.assertEqual("tester" in data_ob.BUILD.NAME, True)



    # Submitting invalid json to server expecting Invalid json in response
    def test_invalid_json(self):
        response = self.client.post("/ClientPost/",
                                    "data=woeifjopeijefowiejfoweijfo",
                                    "application/json")


        self.assertEqual("Invalid json" in response.content, True)


    # Submitting invalid json to server expecting Invalid json in
    # a json response
    def test_invalid_json_ret_json(self):
        response = self.client.post("/ClientPost/JSON/",
                                    "data=woeifjopeijefowiejfoweijfo",
                                    "application/json")


        ret = json.loads(response.content)

        self.assertEqual(response.status_code, 500)
        self.assertEqual("Invalid json" in ret['error'], True)


     # Submitting valid json to server with fields missing
    def test_missing_fields_ret_json(self):

        response = self.client.post("/ClientPost/JSON/",
                                    "data={}",
                                    "application/json")


        ret = json.loads(response.content)

        self.assertEqual(response.status_code, 500)
        self.assertEqual("Payload missing required fields" in ret['error'],
                         True)

    # Test invalid parameters
    def test_invalid_parms(self):

        response = self.client.get("/Errors/Latest/?order_by=wfwjeofiwejo")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/Errors/Latest/?filter=wefwfe")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/Errors/Latest/?filter=wefwfe&type=wefijwoe")
        response = self.client.get("/Errors/Latest/?page=-1")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/Errors/Latest/?page=wefwef")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/Errors/Latest/?limit=-1")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/Errors/Latest/?limit=wefwef")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/Errors/Latest/?order_by=-iojqwef&filter=wefwef&type=dewwef&limit=wefe&page=wefwef")
        self.assertEqual(response.status_code, 200)
