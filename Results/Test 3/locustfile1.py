from locust import HttpUser, TaskSet, task, constant
import hmac
import hashlib
import json

github_secret = "secret"

# Function to create HMAC SHA1 signature
def create_signature(secret, payload):
    signature = 'sha1=' + hmac.new(secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha1).hexdigest()
    return signature

# Sample payload for GitHub issue creation that contains the feature under development inside its description
issue_creation_payload = {
  "action": "opened",
  "issue": {
    "repository_url": "https://api.github.com/repos/tudoroscoiu/test-repo",
    "html_url": "https://github.com/tudoroscoiu/test-repo/issues/41",
    "id": 2382318468,
    "number": 41,
    "title": "Test issue 1",
    "user": {
      "login": "tudoroscoiu",
      "id": 99651294
    },
    "state": "open",
    "created_at": "2024-06-30T16:01:45Z",
    "updated_at": "2024-06-30T16:01:45Z",
    "body": "Implemented automation for C code formatting using clang-format and integrated static analysis with cppcheck to streamline the review process",
  },
  "repository": {
    "id": 808839806,
    "name": "test-repo",
    "owner": {
      "login": "tudoroscoiu",
      "id": 99651294,
    },
  },
  "sender": {
    "login": "tudoroscoiu",
    "id": 99651294
  }
}

class UserBehavior(TaskSet):
    @task
    def index(self):
        headers = {"Content-Type": "application/json", "X-GitHub-Event": "issues", "X-Hub-Signature": create_signature(github_secret, json.dumps(issue_creation_payload))}
        self.client.post("/webhook", data = json.dumps(issue_creation_payload), headers = headers)  

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = constant(0)