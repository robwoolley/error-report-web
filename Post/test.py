import unittest
import urllib
import json
from django.test import Client
from Post.models import BuildFailure

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="testhost")

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
    def test_submission(self):

        with open("test-data/test-payload.json") as f:
            data = f.read()


        data = urllib.urlencode({'data': data})

        response = self.client.post("/ClientPost/",
                                    data,
                                    "application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual("/Build/1" in response.content, True)

        # Now let's see if the data entered the db
        data_ob = BuildFailure.objects.get(id=1)
        self.assertEqual("tester" in data_ob.BUILD.NAME, True)


    # Opening test-payload.json and submitting it to server
    # expecting json response 2nd item inserted to db
    def test_submission_ret_json(self):

        with open("test-data/test-payload.json") as f:
            data = f.read()


        data = urllib.urlencode({'data': data})

        response = self.client.post("/ClientPost/JSON/",
                                    data,
                                    "application/json")

        self.assertEqual(response.status_code, 200)

        ret = json.loads(response.content)

        self.assertEqual(ret['build_id'], 2)
        fails = ret['failures']

        self.assertEqual(fails[0]['id'], 2)

        # Now let's see if the data entered the db
        data_ob = BuildFailure.objects.get(id=2)
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
