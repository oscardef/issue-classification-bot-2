# 🤖 Issue Classification Bot

## Introduction
The *Issue Classification Bot* is a tool designed to automate the labeling of GitHub issues using machine learning (ML). It analyzes the content of issues (titles, descriptions), assigns relevant labels, and sends email notifications, facilitating easier issue tracking and management. This bot is particularly useful for large projects where manual issue tracking and categorization can be time-consuming.

## Requirements
- **Docker Compose installed** (check [installation guide](https://docs.docker.com/compose/install))
- **Smee CLI installed** (check [installation guide](https://github.com/probot/smee-client))
- **Storage:**
  + At least 14GB of storage available on your local machine:
      * 3GB for the bot files (including the weight files required by the ML model, see [Installation and Running Instructions](#installation-and-running-instructions))
      * at least 11GB for Docker Compose to create the Docker Images necessary to run the bot
 - **Ports Availability:**
     + Port 5001 on your local machine must be available
     + Port 8000 on your local machine must be available

## Installation and Running Instructions
1. Clone the repository to your local machine.
2. Add the following files to the local `/issue-classification-bot-2/Bot` directory:
  - `bot_key.pem`: containing the private key of the bot's GitHub App (find more information about private keys [here](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps))
  - `bot_email.secret`: containing the email address and the email password used by the bot to send notifications, structured as follows:
    * 1st line for the bot email address
    * 2nd line for the bot email password (app password, not the usual email password. For Google Accounts, find more information [here](https://support.google.com/mail/answer/185833?hl=en))
3. Download the [weight files](https://zenodo.org/records/7821209) required by the bot's ML model and add them to the local<br> `/issue-classification-bot-2/ModelsBackend/plugins/satd/SATD_Detector/data` directory as follows:
    * Rename `fasttext_issue_300.bin` to `embeddings.bin`
    * Rename `satd_detector_for_issues.hdf5` to `weights.hdf5`
4. Navigate to the root directory `/issue-classification-bot-2` containing the `docker-compose.yml` file.
5. Run the bot using the command:
   ```bash
   docker compose up
   ```
6. Open a new terminal window and run the following command, to automatically synchronize any future non-functional modifications to the bot's local files into its Docker container, while the bot is running:
   ```bash
   docker compose watch
   ```
7. Open a new terminal window and start the Smee CLI with:
   ```bash
   smee --url https://smee.io/Wpx6fSOaWjEaOK --path /webhook --port 5001
   ```

## Usage
Interact with the *Issue Classification Bot* by using the following commands in the comments of a GitHub issue:
- `/tdbot label`: Automatically labels an issue using the ML model.
- `/tdbot label <label>`: Manually labels an issue with the specified label.
- `/tdbot help`: Displays this help message with command details.

## Configuring the Bot
Edit the `config.json` file to configure the bot's behavior:
- `repository-owner`: the GitHub username of the owner of the repository where the bot is installed (*string*)
- `repository-name`: the name of the repository where the bot is installed (*string*)
- `payload-type`: Choose between:
  * "title":       to set whether the bot's ML model should generate a label based on the title of the issue
  * "description": to set whether the bot's ML model should generate a label based on the description of the issue
  * "merged":      to set whether the bot's ML model should generate a single label based on the title and the description of the issue
  * "both":        to set whether the bot's ML model should generate two separate labels based on the title and the description of the issue
- `endpoint`: URL of the ML model's endpoint (*string*)
- `label-location`: JSON path in the ML model's response for the generated label (*string*)
- `auto-label`: *Boolean* to set if the bot should automatically label new issues
- `initial-message`: *Boolean* to set if the bot should create a comment message when an issue is created
- `send-emails`: *Boolean* to set if the bot should send email notifications
- `when-to-send`: Choose between:
  * "label":     to set whether the bot should send email notifications when an issue is labeled
  * "lingering": to set whether the bot should send email notifications when lingering issues have been identified in the repository
  * "all":       to set whether the bot should send email notifications for all the above scenarios
- `email-info`: Configuration options for the email sender
  - `which-labels`: if the bot should send email notifications when it adds a label to the issue (by setting `when-to-send` to "label" or "all"), choose between:
    * "all":      if the bot should send email notifications for all kinds of labels
    * "except":   if the bot should send email notifications for all kinds of labels except the ones specified in `except-labels`
    * "specific": if the bot should send email notifications only for the labels specified in `specific-labels`
  - `except-labels`: the labels for which the bot does not send email notifications, specified as a *list of strings*: \["label1", "label2", ...]
  - `specific-labels`: the labels for which the bot sends email notifications, specified as a *list of strings*: \["label1", "label2", ...]
  - `lingering-check-frequency`: the frequency, in number of days (*integer*) > 0, with which the bot checks for lingering issues in the repository and sends email notifications based on them<br>
  **IMPORTANT❗** <br> › *Make sure to have* `lingering-check-frequency` *set to the desired frequency with which you want (or will want) to receive email notifications about lingering issues **BEFORE** the bot is started, even if at the time of startup of the bot, you do not want to receive this kind of email notifications (by specifying* `when-to-send` *to "label" or anything other than "lingering" or "all").* <br>
    › *In the future, if you modify* `when-to-send` *to "lingering" or "all" while the bot is running, the bot will be able to send email notifications about lingering issues with the frequency that was specified in* `lingering-check-frequency` *before the bot was started.* <br>
    › *Once the bot is started, the frequency with which the bot checks for lingering issues and sends email notifications based on them:* `lingering-check-frequency` ***CANNOT** be modified (without stopping the bot and restarting it).*
  - `lingering-issue-threshold`: if the bot should send email notifications when lingering issues have been identified in the repository (by setting `when-to-send` to "lingering" or "all"), choose the threshold, in number of days (*integer*), after an issue would be considered lingering
  - `lingering-mode`: if the bot should send email notifications when lingering issues have been identified in the repository (by setting `when-to-send` to "lingering" or "all"), choose between:
    * "creation-date": if the bot should determine whether an issue is lingering or not based on the creation date of the issue
    * "last-modified": if the bot should determine whether an issue is lingering or not based on the last date when the issue has been modified (either by posting a comment, assigning a label, or any other kind of modification)
  - `recipients`: the list of email addresses of contributors that should receive email notifications, specified as a *list of strings*: \["emailAddress1", "emailAddress2", ...]
  - `email-description-template`: The template strings used for the description of the bot-generated emails
    * `label`: email description template (*string*) for email notifications about labels<br>
    **Any string that you use for this email description template should contain three '{}' inside the string, the first one for the label that was associated with the issue, the second one for the issue number, and the third one for the issue title, in this order.**
    * `lingering`: email description template (*string*) for email notifications about lingering issues<br>
    **Any string that you use for this email description template should contain one '{}' inside the string, for the lingering issues found in the repository.**
  - `email-subject-template`: the template strings used for the subject of the bot-generated emails
    * `label`:     email subject template (*string*) for email notifications about labels
    * `lingering`: email subject template (*string*) for email notifications about lingering issues
## Troubleshooting
If you encounter issues with the bot:
- If labels are not being assigned to issues when a `/tdbot label` comment is posted:
  * Verify that the `config.json` file is located in the `/issue-classification-bot-2/Bot` directory, both locally and on the repository, and that it is [set up correctly](#configuring-the-bot).
  * Verify that the Smee CLI is running and properly connected.
  * Verify that the generated label is not already assigned to the issue.
- If bot email notifications are not being sent/received:
  * Verify that the `config.json` file is located in the `/issue-classification-bot-2/Bot` directory, both locally and on the repository, and that it is [set up correctly](#configuring-the-bot).
  * Verify that the Smee CLI is running and properly connected.
  * Verify that the `bot_email.secret` file is stored in the local `/issue-classification-bot-2/Bot` directory, and that it is [set up correctly](#installation-and-running-instructions).

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For questions or feedback regarding the Issue Classification Bot, please open an issue in the GitHub repository.

## Acknowledgments
Special thanks to all contributors and maintainers of this project. Your efforts greatly enhance its quality and usability.
