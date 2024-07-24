import json

def generate_configurations():
    # Defining the possible values for each field
    payload_types = ["description", "title", "merged", "both"]
    endpoint = "http://model:8000/models/Model1_IssueTracker_Li2022_ESEM"
    label_location = "label"
    lingering_issue_threshold = 1

    boolean_options = [True, False]
    when_to_send_options = ["all", "label", "lingering", "feature"]
    which_labels_options = ["all", "specific", "except"]
    lingering_mode_options = ["last-modified", "creation-date"]

    configurations = []

    for payload_type in payload_types:
        for auto_label in boolean_options:
            for initial_message in boolean_options:
                for send_emails in boolean_options:
                    if send_emails:
                        for when_to_send in when_to_send_options:
                            if when_to_send == "label":
                                for which_labels in which_labels_options:
                                    config = {
                                        "payload-type": payload_type,
                                        "endpoint": endpoint,
                                        "label-location": label_location,
                                        "auto-label": auto_label,
                                        "initial-message": initial_message,
                                        "send-emails": send_emails,
                                        "when-to-send": when_to_send,
                                        "email-info": {}
                                    }
                                    email_info_with_labels = {}
                                    email_info_with_labels["which-labels"] = which_labels
                                    if which_labels == "except":
                                        email_info_with_labels["except-labels"] = [""]
                                    elif which_labels == "specific":
                                        email_info_with_labels["specific-labels"] = [""]
                                    email_info_with_labels["recipients"] = [""]

                                    email_info_with_labels["email-body-template"] = {}
                                    email_info_with_labels["email-body-template"]["label"] = ""
                                    email_info_with_labels["email-subject-template"] = {}
                                    email_info_with_labels["email-subject-template"]["label"] = ""

                                    config["email-info"] = email_info_with_labels
                                    configurations.append(config)

                            if when_to_send == "lingering":
                                for lingering_mode in lingering_mode_options:
                                    config = {
                                        "payload-type": payload_type,
                                        "endpoint": endpoint,
                                        "label-location": label_location,
                                        "auto-label": auto_label,
                                        "initial-message": initial_message,
                                        "send-emails": send_emails,
                                        "when-to-send": when_to_send,
                                        "email-info": {}
                                    }
                                    email_info_with_lingering = {}
                                    email_info_with_lingering["lingering-mode"] = lingering_mode
                                    email_info_with_lingering["lingering-issue-threshold"] = lingering_issue_threshold
                                    email_info_with_lingering["recipients"] = [""]

                                    email_info_with_lingering["email-body-template"] = {}
                                    email_info_with_lingering["email-body-template"]["lingering"] = ["", ""]
                                    email_info_with_lingering["email-subject-template"] = {}
                                    email_info_with_lingering["email-subject-template"]["lingering"] = ""

                                    config["email-info"] = email_info_with_lingering
                                    configurations.append(config)

                            if when_to_send == "feature":
                                config = {
                                    "payload-type": payload_type,
                                    "endpoint": endpoint,
                                    "label-location": label_location,
                                    "auto-label": auto_label,
                                    "initial-message": initial_message,
                                    "send-emails": send_emails,
                                    "when-to-send": when_to_send,
                                    "email-info": {}
                                }
                                email_info_with_feature = {}
                                email_info_with_feature["feature-under-development"] = ""
                                email_info_with_feature["recipients"] = [""]

                                email_info_with_feature["email-body-template"] = {}
                                email_info_with_feature["email-body-template"]["feature"] = ""
                                email_info_with_feature["email-subject-template"] = {}
                                email_info_with_feature["email-subject-template"]["feature"] = ""

                                config["email-info"] = email_info_with_feature
                                configurations.append(config)

                            if when_to_send == "all":
                                for which_labels in which_labels_options:
                                    for lingering_mode in lingering_mode_options:
                                        config = {
                                            "payload-type": payload_type,
                                            "endpoint": endpoint,
                                            "label-location": label_location,
                                            "auto-label": auto_label,
                                            "initial-message": initial_message,
                                            "send-emails": send_emails,
                                            "when-to-send": when_to_send,
                                            "email-info": {}
                                        }
                                        email_info_with_all = {}
                                        email_info_with_all["which-labels"] = which_labels
                                        if which_labels == "except":
                                            email_info_with_all["except-labels"] = [""]
                                        elif which_labels == "specific":
                                            email_info_with_all["specific-labels"] = [""]
                                        email_info_with_all["lingering-mode"] = lingering_mode
                                        email_info_with_all["lingering-issue-threshold"] = lingering_issue_threshold
                                        email_info_with_all["feature-under-development"] = ""
                                        email_info_with_all["recipients"] = [""]

                                        email_info_with_all["email-body-template"] = {}
                                        email_info_with_all["email-body-template"]["label"] = ""
                                        email_info_with_all["email-body-template"]["lingering"] = ["", ""]
                                        email_info_with_all["email-body-template"]["feature"] = ""
                                        email_info_with_all["email-subject-template"] = {}
                                        email_info_with_all["email-subject-template"]["label"] = ""
                                        email_info_with_all["email-subject-template"]["lingering"] = ""
                                        email_info_with_all["email-subject-template"]["feature"] = ""

                                        config["email-info"] = email_info_with_all
                                        configurations.append(config)
                                        
                    else:
                        config = {
                            "payload-type": payload_type,
                            "endpoint": endpoint,
                            "label-location": label_location,
                            "auto-label": auto_label,
                            "initial-message": initial_message,
                            "send-emails": send_emails
                        }
                        configurations.append(config)

    return configurations

# Generating the configurations and printing them
configurations = generate_configurations()
for i, config in enumerate(configurations):
    print(f"Configuration {i + 1}:")
    print(json.dumps(config, indent=2))
    print()
