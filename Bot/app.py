import os
import requests
import json
import base64
import hmac

from flask import Flask, request, abort
from emailSender import send_email
from lingeringIssuesProcessor import process_lingering_issues

app = Flask(__name__)

# Read the bot certificate
with open("bot_key.pem", "r") as cert_file:
    github_app_key = cert_file.read()

def label_issue(issue, config, label=None):
    if label is None:
        # Call the ML model API to get the label
        url = config["endpoint"]
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {}
        if config["payload-type"] == "title":
            data["text"] = issue["title"]
        elif config["payload-type"] == "description":
            if issue["body"] is not None:
                data["text"] = issue["body"]
            else:
                print("Issue does not have a description, no label generated", flush=True)
                return
        elif config["payload-type"] == "merged":
            data["text"] = issue["title"] + (" " + issue["body"] if issue["body"] is not None else "")
        elif config["payload-type"] == "both":
            label_title_and_desc(config, data, headers, issue, url)
            return
        result = requests.post(url, headers=headers, data=json.dumps(data)).json()
        label_location = config["label-location"]
        label = result[label_location]
        # Send email if emails for labels/all types of emails are enabled in config.json
        if config["send-emails"] is True and config["when-to-send"] in ["label", "all"]:
            send_email([issue], config, 0, label)
    else:
        # Send email if emails for feature under development/all types of emails are enabled in config.json
        if config["send-emails"] is True and config["when-to-send"] in ["feature", "all"]:
            send_email([issue], config, 2, label)


def label_title_and_desc(config, data, headers, issue, url):
    data["text"] = issue["title"]
    result = requests.post(url, headers=headers, data=json.dumps(data)).json()
    label_location = config["label-location"]
    title_label = result[label_location]

    description_label = None
    if issue["body"] is not None:
        data["text"] = issue["body"]
        result = requests.post(url, headers=headers, data=json.dumps(data)).json()
        label_location = config["label-location"]
        description_label = result[label_location]
    else:
        print("Issue does not have a description, no description label generated", flush=True)

    # Send email if emails for labels/all types of emails are enabled in config.json
    if config["send-emails"] is True and config["when-to-send"] in ["label", "all"]:
        if description_label is None or title_label == description_label:
            """
            Single email (for the title label) if the issue does not contain a description (and consequently, no 
            description label is generated) or if the labels generated for both the title and the description of the 
            issue are identical
            """
            send_email([issue], config, 0, title_label)
        else:
            # Separate emails if the labels generated for the title and the description of the issue are different
            send_email([issue], config, 0, "Title: " + title_label)
            send_email([issue], config, 0, "Description: " + description_label)


def handle_issue_comment_event(repo, payload, config):
    commenter = payload["comment"]["user"]["login"]
    if commenter == "issue-classification-bot[bot]":
        return "ok"

    issue = payload["issue"]
    comment = payload["comment"]["body"]

    # Comment body will be a command like "/tdbot label", "/tdbot help", etc. So we need to parse it
    command = comment.split(" ")
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

    return "ok"


def handle_issue_creation_event(repo, payload, config):
    # Check if the issue is newly created
    if payload["action"] != "opened":
        return "ok"

    issue = payload["issue"]
    # Check if auto-labeling of issues is enabled in config.json
    if config["auto-label"] is True:
        label_issue(issue, config)
    # Send email if emails for feature under development/all types of emails are enabled in config.json
    if config["send-emails"] is True and config["when-to-send"] in ["feature", "all"]:
        send_email([issue], config, 2)

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

    # Obtain the type of GitHub event
    payload_type = request.headers.get("X-GitHub-Event")

    # Check if the event is a GitHub App install/uninstall event
    if payload_type in ["installation", "installation_repositories"]:
        return "ok"

    repo = None

    # If repo has config.json file in the Bot directory, use it. Otherwise, use the config.json file locally in the bot
    with open("config.json", "r") as f:
        config = json.load(f)
        print("Using config file from the local Bot directory", flush=True)

    # Check if the event is a GitHub issue comment creation or issue creation event
    if payload_type == "issue_comment":
        return handle_issue_comment_event(repo, payload, config)
    elif payload_type == "issues":
        return handle_issue_creation_event(repo, payload, config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
