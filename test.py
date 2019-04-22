import unittest, requests, json, os

MAIN_APP = 'http://localhost:8001/main_app'
JWT = None
JOB_ID = None

def do_request(uri, data={}, headers={}):
  try:
    response = requests.post(os.path.join(MAIN_APP, uri), json=data, headers=headers)

    return json.loads(response.text)
  except Exception as e:
    raise e

class TestCreateJob(unittest.TestCase):
  def test_auth(self):
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

  def test_create_job(self):
    global JOB_ID
    global JWT
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

  def test_get_job_status(self):
    global JOB_ID
    global JWT
    token = 'Bearer {}'.format(JWT)

    try:
      data = do_request('api/get_job_status', {
        "job_id": JOB_ID
      }, {'Authorization': token})
    except Exception as e:
      print('Exception -- ', e)

    print(data)
    self.assertIsNot(data['status'], None)
    self.assertIs(data['status'], 1)

if __name__ == '__main__':
  unittest.main()