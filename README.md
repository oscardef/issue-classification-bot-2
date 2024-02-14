# Issue Classification Bot

## Introduction
The Issue Classification Bot is a tool designed to automate the labeling of GitHub issues using machine learning. It analyzes the content of issues (titles, descriptions) and assigns relevant labels, facilitating easier issue tracking and management. This bot is particularly useful for large projects where manual issue categorization can be time-consuming.

## Requirements
- Python 3.6 or higher
- Dependencies listed in `requirements.txt`

To install dependencies, run:
```bash
pip install -r requirements.txt
```

## Installation and Running Instructions
1. Clone the repository to your local machine.
2. Navigate to the root directory containing the `app.py` file.
3. Run the bot using the command:
   ```bash
   python3 app.py
   ```
4. Open a new terminal window and start the Smee client with:
   ```bash
   smee -u https://smee.io/Wpx6fSOaWjEaOK --port 5000
   ```

## Usage
Interact with the Issue Classification Bot by using the following commands in the comments of a GitHub issue:
- `/tdbot label`: Automatically labels an issue using the ML model.
- `/tdbot label <label>`: Manually labels an issue with the specified label.
- `/tdbot help`: Displays this help message with command details.

## Configuring the Bot
Edit the `config.json` file to configure the bot's behavior:
- `payload-type`: Choose between "title", "description", "merged", or "both" to set which parts of the issue the model evaluates.
- `endpoint`: URL of the machine learning model's endpoint.
- `label-location`: JSON path in the model's response for the label.
- `auto-label`: Boolean to set if the bot should automatically label new issues.
- `initial-message`: Boolean to set if the bot should send a message when an issue is created.

## Troubleshooting
If you encounter issues with the bot:
- Ensure all dependencies are correctly installed.
- Verify the `config.json` file is correctly set up and the endpoint is reachable.
- Check if the Smee client is running and properly connected.

## Contributing
Contributions to the Issue Classification Bot are welcome! Please read our contributing guidelines for details on submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For questions or feedback regarding the Issue Classification Bot, please open an issue in the GitHub repository.

## Acknowledgments
Special thanks to all contributors and maintainers of this project. Your efforts greatly enhance its quality and usability.
