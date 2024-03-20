import uvicorn
import os
import logging
import boto3
from flask_cors import CORS
from fastapi import FastAPI
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import ORJSONResponse
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from openai import OpenAI
from os import environ


# Load variables from the .env file
load_dotenv()

# Load environment variables
OPENAI_KEY = os.getenv("OPENAI_KEY")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
REGION_NAME = os.getenv("REGION_NAME")


# Access the variables

client = OpenAI(api_key=OPENAI_KEY)
# Specify the name of the log group and log stream
log_group_name = 'voiceflow'
log_stream_name = 'default'
app = FastAPI()


# Get session
def get_session():
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION_NAME
    )
    return session

session = get_session()
ssm = session.client('ssm')


# Initialize a boto3 client for CloudWatch Logs using the session
cloudwatch_logs = session.client('logs', region_name='us-east-1')

# Specify the name of the log group and log stream
log_group_name = 'graincheck'
log_stream_name = 'userid-123456'

# Check if the log group already exists
try:
    cloudwatch_logs.describe_log_groups(logGroupNamePrefix=log_group_name)
    print(f"Log group '{log_group_name}' already exists.")
except cloudwatch_logs.exceptions.ResourceNotFoundException:
    # Log group does not exist, create it
    cloudwatch_logs.create_log_group(logGroupName=log_group_name)
    print(f"Log group '{log_group_name}' created.")

# Check if the log stream already exists
try:
    response = cloudwatch_logs.describe_log_streams(logGroupName=log_group_name, logStreamNamePrefix=log_stream_name)
    if not response['logStreams']:
        # Log stream does not exist, create it
        cloudwatch_logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        print(f"Log stream '{log_stream_name}' created within log group '{log_group_name}'.")
    else:
        print(f"Log stream '{log_stream_name}' already exists within log group '{log_group_name}'.")
except cloudwatch_logs.exceptions.ResourceNotFoundException:
    # Log group does not exist
    print(f"Log group '{log_group_name}' does not exist.")


# Configure the Python logging module to send logs to CloudWatch Logs
logging.basicConfig(level=logging.INFO)

# Create a custom logger
logger = logging.getLogger('fastapi_template')

# Define a custom handler for CloudWatch Logs
class CloudWatchLogsHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            # Send the log record to CloudWatch Logs
            cloudwatch_logs.put_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(record.created * 1000),
                        'message': self.format(record)
                    }
                ]
            )
        except Exception as e:
            print(f"Failed to send log record to CloudWatch Logs: {e}")

# Add the CloudWatchLogsHandler to the logger
logger.addHandler(CloudWatchLogsHandler())

@app.post('/openAIchat', response_class=ORJSONResponse)
async def openAIchat(sentence : str ,parameter_name :str):   
        
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are expert tax assistant of Canada, skilled in explaining complex tax queries with clarity and appropriate answer.Don't mock up answers, if you don't know say I don't know"},
        {"role": "user", "content": sentence}
    ]
    )
    response = completion.choices[0].message

    logger.info(f"Parameter name : {parameter_name}. {response.content}")

    return response

if __name__ == '__main__':
   
    uvicorn.run(app, host="0.0.0.0", port=5001)
