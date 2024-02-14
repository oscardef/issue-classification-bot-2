import os
import requests
import json
import base64

from flask import Flask, request, abort
import hmac
from github import Github, GithubIntegration

app = Flask(__name__)

app_id = 821348

# Read the bot certificate
with open(os.path.normpath(os.path.expanduser("bot_key.pem")), "r") as cert_file:
    app_key = cert_file.read()

# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)


def label_issue(issue, config, label=None):
    if label is None:
        # Call the model API to get the label
        url = config["endpoint"]
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {}
        if config["payload-type"] == "title":
            data["text"] = issue.title
        elif config["payload-type"] == "description":
            data["text"] = issue.body
        elif config["payload-type"] == "merged":
            data["text"] = issue.title + " " + issue.body
        elif config["payload-type"] == "both":
            label_title_and_desc(config, data, headers, issue, url)
            return
        result = requests.post(url, headers=headers, data=json.dumps(data)).json()
        label_location = config["label-location"]
        label = result[label_location]
        # Add the label to the issue
        issue.add_to_labels(label)
    else:
        # Simply add the label to the issue (for custom labels)
        issue.add_to_labels(label)


def label_title_and_desc(config, data, headers, issue, url):
    data["text"] = issue.title
    result = requests.post(url, headers=headers, data=json.dumps(data)).json()
    label_location = config["label-location"]
    title_label = result[label_location]
    data["text"] = issue.body
    result = requests.post(url, headers=headers, data=json.dumps(data)).json()
    label_location = config["label-location"]
    description_label = result[label_location]
    # Add the labels to the issue
    issue.add_to_labels("title: " + title_label)
    issue.add_to_labels("description: " + description_label)


def handle_issue_comment_event(repo, payload, config):
    commenter = payload["comment"]["user"]["login"]
    if commenter == "technical-debt-mitigation-bot[bot]":
        return "ok"

    comment = repo.get_issue(number=payload["issue"]["number"]).get_comment(
        payload["comment"]["id"]
    )
    issue = repo.get_issue(number=payload["issue"]["number"])

    # comment body will be a command like "/tdbot label", "/tdbot help", etc. So we need to parse it
    command = comment.body.split(" ")
    if command[0] == "/tdbot":
        if command[1] == "label":
            if len(command) == 2:
                label_issue(issue, config)
            else:
                # add everything after the command to the label
                label = " ".join(command[2:])
                label_issue(issue, config, label)
        elif command[1] == "help":
            help_message = ""
            with open("help_message.txt", "r") as f:
                help_message = f.read()
            issue.create_comment(help_message)
        else:
            issue.create_comment("I don't understand your command. Please try again.")
    return "ok"


def handle_issue_creation_event(repo, payload, config):
    # check if the issue is newly created
    if payload["action"] != "opened":
        return "ok"

    issue = repo.get_issue(number=payload["issue"]["number"])
    # check if the repo is enabled for auto labeling
    if config["auto-label"] == True:
        label_issue(issue, config)
        return "ok"
    if config["initial-message"] == True:
        issue.create_comment(
            "This issue seems to document technical debt.\n\n"
            'You can label it with "/tdbot label"'
        )
    return "ok"


@app.route("/webhook", methods=["POST"])
def bot():
    # Validate the request is from GitHub
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    signature = request.headers.get("X-Hub-Signature")
    if signature is None:
        abort(403)

    sha_name, signature = signature.split("=")
    if sha_name != "sha1":
        abort(501)

    mac = hmac.new(secret.encode("utf-8"), msg=request.data, digestmod="sha1")

    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        abort(403)

    # Get the event payload
    payload = request.json

    # Check if the event is a GitHub Issue Comment creation event
    payload_type = request.headers.get("X-GitHub-Event")
    owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]

    # Get a git connection as our bot
    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )

    repo = git_connection.get_repo(f"{owner}/{repo_name}")
    # if repo has config.json file use it, otherwise use the config.json file locally in the bot
    config_file = {}
    try:
        config_file = repo.get_contents("configs.json")
        print("Using config file from the repo")
        # decode the file
        config = json.loads(base64.b64decode(config_file.content).decode("utf-8"))
    except:
        with open("config.json", "r") as f:
            config = json.load(f)

    if payload_type == "issue_comment":
        return handle_issue_comment_event(repo, payload, config)
    elif payload_type == "issues":
        return handle_issue_creation_event(repo, payload, config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
