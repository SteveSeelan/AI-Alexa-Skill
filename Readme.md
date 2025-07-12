# Description

Amazon Alexa skill kit (ASK) AI integration. The code here is used by a lambda function which is called by the amazon Alexa skill when the "invocation name" defined in the Alexa Skill.

## Basic needs

- Make sure to create an Amazon Alexa Developer account with the email that your Alexa device is register to on the Amazon Alexa App
- Make sure to have an AWS developer account for the Lambda function
- Get an API key from an LLM provider like OpenAI, for our purposes, Google AI platform for Gemini

### Amazon Alexa Skill setup

Go to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask) and click "Create Skill".

1. Skill name: My AI Helper (or anything you like)

2. Primary locale: Choose your language, same as your Alexa device

3. Choose a model: Custom

4. Choose a method to host: Provision your own (basically the Lambda Function set up later)

5. At the top right, click "Create skill".

6. Choose a Template: Select the Hello World Skill. This gives you a basic starting point.

Set the Invocation Name:

1. On the left-hand menu, click on Invocations -> Skill Invocation Name.

2. This is the phrase you'll use to start your skill. Set it to something unique like "my a. i."

3. Click Save Model at the top.

Create an Intent to Capture User Queries:

1. On the left, under Interaction Model, click on Intents.

2. Click "Add Intent". Name it AskLlmIntent. **Note this*** if not using my .zip, your custom code would need this to be handled.

3. You can delete the HelloWorldHandler
Now, we need to capture the user's question. Under Intent Slots, create a slot with:

`Name: query`

`Type: AMAZON.SearchQuery`

This is a special slot type designed to capture free-form speech, perfect for an LLM prompt.

Next, link what the user says to this intent and slot. Under Sample Utterances, add the following lines, then press enter after each one:

`ask {query}`

`who is {query}`

`what is {query}`

`ask {query} who`

Click Save Model, then click Build Model. This will take a minute or two.

### AWS Lambda Function setup

Create a new lambda function with:

- name: anyNameWorks
- runtime: Python 3.12
- architecture: arm64

Click into your lambda function

- Add trigger: Alexa
- Configuration
  - general configuration
    - timeout to 15s (LLM slow)
    - increase memory to 512MB maybe?
  - environment variables
    - key: "GEMINI_API_KEY", value: 8not1real9hrkaff783by198the91way
- Code
  - upload from .zip file (the .zip file in this repo or your own zip)
  - If you want your own zipped code (summary)
    - I created a docker container with the `amazonlinux:latest` image. **MAKE SURE this is the same architecture(arm64), OS(amazonlinux), and Runtime(Python3.12) as the Lambda Function**
    - ran it in interactive mode mounting my working directory to /var/task/
    - inside the container I installed the python3.12 with `yum install python3.12`
    - use python3.12 to create your venv and activate it
    - `pip install --target ./package google-generativeai ask-sdk-core`
      - this will create the necessary packages needed to import libraries
    - `touch lambda_function.py` and create your code, needs to be this name
    - cd into package and run `zip -r ../my-deployment-package.zip .`
    - cd .. and run `zip -g my-deployment-package.zip lambda_function.py`
  - Upload the .zip to the lambda function
- deploy the code and then copy the ARN of the lambda function

### Final steps

Go back to the Amazon Developer Console and paste the copied ARN in the Endpoint under the Default Region

Go to the test tab and try an invocation like "ask my a. i." and continue with more prompts like "ask my a. i. who are you? or "what is the meaning of life" - should be fun lol. Debug using the CloudWatch logs in AWS.

Since your email for the developer account is the same as the email the Alexa device is registered to, you will be good to go in asking the device itself. Enjoy!
