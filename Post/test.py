import unittest
import urllib
import json
import re
from django.test import Client
from Post.models import BuildFailure, Build

#Delete the data between tests
def data_runner (func):
    def wrap(*args, **kwargs):

        self = args[0]

        bo = Build.objects.all()
        bfo = BuildFailure.objects.all()

        bo.delete()
        bfo.delete()

        # run the test
        func(*args, **kwargs)

        # The submission should have added one row in each table
        self.assertEqual(bfo.count(), 1)
        self.assertEqual(bo.count(), 1)

        compare_db_obj_with_payload(self, bfo[0])

    return wrap

def compare_db_obj_with_payload(self, bf_object):
    f = open("test-data/test-payload.json")
    data = f.read()
    payload = json.loads(data)

    self.assertEqual(bf_object.BUILD.MACHINE == str(payload['machine']), True)
    self.assertEqual(bf_object.BUILD.NATIVELSBSTRING == str(payload['nativelsb']), True)
    self.assertEqual(bf_object.BUILD.TARGET_SYS == str(payload['target_sys']), True)

    self.assertEqual(bf_object.BUILD.BUILD_SYS == str(payload['build_sys']), True)
    self.assertEqual(bf_object.BUILD.DISTRO == str(payload['distro']), True)
    self.assertEqual(bf_object.BUILD.NAME == str(payload['username']), True)
    self.assertEqual(bf_object.BUILD.EMAIL == str(payload['email']), True)
    self.assertEqual(bf_object.BUILD.LINK_BACK == payload.get("link_back", None), True)

    g = re.match(r'(.*): (.*)', payload['branch_commit'])

    self.assertEqual(bf_object.BUILD.BRANCH == str(g.group(1)), True)
    self.assertEqual(bf_object.BUILD.COMMIT == str(g.group(2)), True)

    fail = payload['failures'][0]
    package = str(fail['package'])
    g = re.match(r'(.*)\-(\d.*)', package)

    self.assertEqual(bf_object.ERROR_DETAILS == str(fail['log']), True)
    self.assertEqual(bf_object.TASK == str(fail['task']), True)
    self.assertEqual(bf_object.RECIPE == str(g.group(1)), True)
    self.assertEqual(bf_object.RECIPE_VERSION == str(g.group(2)), True)

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
    @data_runner
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


    @data_runner
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

    @data_runner
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


    @data_runner
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
        self.assertEqual("Problem reading json payload" in ret['error'],
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
