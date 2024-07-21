from locust import HttpUser, TaskSet, task, constant
import hmac
import hashlib
import json

github_secret = "secret"

# Function to create HMAC SHA1 signature
def create_signature(secret, payload):
    signature = 'sha1=' + hmac.new(secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha1).hexdigest()
    return signature

# Sample payload for GitHub issue comment event for "/tdbot label"
issue_comment_payload = {
  "action": "created",
  "issue": {
    "repository_url": "https://api.github.com/repos/tudoroscoiu/test-repo",
    "html_url": "https://github.com/tudoroscoiu/test-repo/issues/40",
    "id": 2382296379,
    "number": 40,
    "title": "Test issue",
    "user": {
      "login": "tudoroscoiu",
      "id": 99651294,
    },
    "state": "open",
    "created_at": "2024-06-30T15:06:27Z",
    "updated_at": "2024-06-30T15:08:44Z",
    "body": "Addressing the issue raised in the review, Jackson TypeReferences should be declared constant.",
  },
  "comment": {
    "id": 2198592833,
    "user": {
      "login": "tudoroscoiu",
      "id": 99651294,
    },
    "created_at": "2024-06-30T15:08:44Z",
    "updated_at": "2024-06-30T15:08:44Z",
    "body": "/tdbot label",
  },
  "repository": {
    "id": 808839806,
    "name": "test-repo",
    "owner": {
      "login": "tudoroscoiu",
      "id": 99651294
    }
  },
  "sender": {
    "login": "tudoroscoiu",
    "id": 99651294
  }
}

class UserBehavior(TaskSet):
    @task
    def index(self):
        headers = {"Content-Type": "application/json", "X-GitHub-Event": "issue_comment", "X-Hub-Signature": create_signature(github_secret, json.dumps(issue_comment_payload))}
        self.client.post("/webhook", data = json.dumps(issue_comment_payload), headers = headers)  

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = constant(0)