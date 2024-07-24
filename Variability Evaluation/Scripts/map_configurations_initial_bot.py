import json

def generate_configurations():
    # Defining the possible values for each field
    payload_types = ["description", "title", "merged", "both"]
    endpoint = "http://model:8000/models/Model1_IssueTracker_Li2022_ESEM"
    label_location = "label"
    boolean_options = [True, False]
    configurations = []

    for payload_type in payload_types:
        for auto_label in boolean_options:
            for initial_message in boolean_options:
                config = {
                    "payload-type": payload_type,
                    "endpoint": endpoint,
                    "label-location": label_location,
                    "auto-label": auto_label,
                    "initial-message": initial_message     
                }
                configurations.append(config)
                                   
    return configurations

# Generating the configurations and printing them
configurations = generate_configurations()
for i, config in enumerate(configurations):
    print(f"Configuration {i + 1}:")
    print(json.dumps(config, indent=2))
    print()