import unittest, requests, json, os
from kubernetes import client, config

MAIN_APP = '{}/api_app'.format(os.environ.get('DEV_API_ENDPOINT', 'http://localhost:8001'))
JWT = None
JOB_ID = None
NUM_CRAWLERS = 0 #should be greater than 0 once the crawling flow is fixed

def do_request(uri, data={}, headers={}):
  try:
    response = requests.post(os.path.join(MAIN_APP, uri), json=data, headers=headers)

    return json.loads(response.text)
  except Exception as e:
    raise e

class TestCreateJob(unittest.TestCase):
  def test_1_auth(self):
    global JWT

    try:
      data = do_request('authenticate_user', {
        "username": "admin",
        "password": "s3cr3tp4ss"
      })
      JWT = data['token']
    except Exception as e:
      print('Exception -- ', e)

    self.assertIsNot(JWT, None)

  def test_2_create_job(self):
    global JOB_ID, JWT

    token = 'Bearer {}'.format(JWT)

    try:
      data = do_request('api/create_crawl', {
        "username": "admin",
        "name": "test job",
        "domain": "https://colombianspanish.co",
        "urls": "https://colombianspanish.co/what-to-study"
      }, {'Authorization': token})
      JOB_ID = data['jobId']
    except Exception as e:
      print('Exception -- ', e)

    self.assertIsNot(JOB_ID, None)

  def test_3_get_job_status(self):
    global JOB_ID, JWT

    token = 'Bearer {}'.format(JWT)

    try:
      data = do_request('api/get_job_status', {
        "job_id": JOB_ID
      }, {'Authorization': token})
    except Exception as e:
      print('Exception -- ', e)
    print('jo id', JOB_ID)
    self.assertIsNot(data['status'], None)
    self.assertIs(data['status'], 1)


  def test_4_count_job_crawlers(self):
    global JOB_ID, NUM_CRAWLERS

    config.load_kube_config()

    v1 = client.BatchV1Api()
    label='jobId={}'.format(JOB_ID)

    ret = v1.list_job_for_all_namespaces(label_selector=label, watch=False)

    self.assertIsNot(ret.items, None)
    self.assertIs(len(ret.items), NUM_CRAWLERS)

if __name__ == '__main__':
  unittest.main()