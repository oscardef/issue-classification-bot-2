import os
import requests
import json
import base64
import hmac

from flask import Flask, request, abort
from github import Github, GithubIntegration
from apscheduler.schedulers.background import BackgroundScheduler
from emailSender import send_email
from lingeringIssuesProcessor import process_lingering_issues

app = Flask(__name__)

app_id = 821348

# Read the bot certificate
with open("bot_key.pem", "r") as cert_file:
    app_key = cert_file.read()

# Create a GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)

# Read the local bot configuration file
with open("config.json", "r") as f:
    configuration_initial = json.load(f)

"""
* Get the values of the "repository-owner" and "repository-name" fields from the local Bot/config.json file opened at 
  the startup of the bot application. 
* Make sure to have these fields set correctly to the GitHub username of the owner and the repository where the bot is 
  installed and used, BEFORE the bot is started.
* After this point, the bot will only use the most recent config.json file from the repository (or from the local 
  directory, if it does not exist in the repository) for every action that it performs. 
* Please note that the "repository-owner" and "repository-name" fields must not be modified while the bot is running (as 
  it will not have any effect, anyway).  
* The values of all the other fields of the Bot/config.json (in the repository and/or in the local directory) can be 
  safely modified while the bot is running, and these changes will be reflected in the bot next time it performs an 
  action (label an issue/check for lingering issues/etc.).
"""
repository_owner = configuration_initial["repository-owner"]
repository_name = configuration_initial["repository-name"]

# Scheduling the processing of lingering issues
scheduler = BackgroundScheduler()
# Schedule the function process_lingering_issues to run every 1 day from the moment the bot is started
lingering_check_frequency = 1
scheduler.add_job(func=process_lingering_issues, trigger='interval', days=lingering_check_frequency,
                  args=(git_integration, repository_owner, repository_name, lingering_check_frequency))
scheduler.start()


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
        # Send email if emails for labels/all types of emails are enabled in config.json
        if config["send-emails"] == True and config["when-to-send"] in ["label", "all"]:
            send_email([issue], config, 0, label)
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
    # Send email if emails for labels/all types of emails are enabled in config.json
    if config["send-emails"] == True and config["when-to-send"] in ["label", "all"]:
        if title_label == description_label:
            # Single email if the labels generated for both the title and the description of the issue are identical
            send_email([issue], config, 0, title_label)
        else:
            # Separate emails if the labels generated for the title and the description of the issue are different
            send_email([issue], config, 0, "Title: " + title_label)
            send_email([issue], config, 0, "Description: " + description_label)


def handle_issue_comment_event(repo, payload, config):
    commenter = payload["comment"]["user"]["login"]
    if commenter == "technical-debt-mitigation-bot[bot]":
        return "ok"

    comment = repo.get_issue(number=payload["issue"]["number"]).get_comment(
        payload["comment"]["id"]
    )
    issue = repo.get_issue(number=payload["issue"]["number"])

    # Comment body will be a command like "/tdbot label", "/tdbot help", etc. So we need to parse it
    command = comment.body.split(" ")
    if command[0] == "/tdbot":
        if command[1] == "label":
            if len(command) == 2:
                label_issue(issue, config)
            else:
                # Add everything after the command to the label
                label = " ".join(command[2:])
                label_issue(issue, config, label)
        elif command[1] == "help":
            with open("help_message.txt", "r") as f:
                help_message = f.read()
            issue.create_comment(help_message)
        else:
            issue.create_comment("I don't understand your command. Please try again.")
    return "ok"


def handle_issue_creation_event(repo, payload, config):
    # Check if the issue is newly created
    if payload["action"] != "opened":
        return "ok"

    issue = repo.get_issue(number=payload["issue"]["number"])
    # Check if the repo is enabled for auto labeling
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
    # Validate that the request is from GitHub
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

    # Check if the event is a GitHub issue comment creation event
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
    # If repo has config.json file in the Bot directory, use it. Otherwise, use the config.json file locally in the bot
    try:
        config_file = repo.get_contents("Bot/config.json")
        print("Using config file from the repo", flush=True)
        # Decode the file
        config = json.loads(base64.b64decode(config_file.content).decode("utf-8"))
    except:
        with open("config.json", "r") as f:
            config = json.load(f)
            print("Using config file from local Bot directory", flush=True)

    if payload_type == "issue_comment":
        return handle_issue_comment_event(repo, payload, config)
    elif payload_type == "issues":
        return handle_issue_creation_event(repo, payload, config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
