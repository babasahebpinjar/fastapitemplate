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


app = FastAPI()
# Access the variables

client = OpenAI(api_key=OPENAI_KEY)

@app.post('/openAIchat', response_class=ORJSONResponse)
async def openAIchat(sentence : str ):   
        
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are grain expert of Canada, skilled in explaining complex grain queries with clarity and appropriate answer.Don't mock up answers, if you don't know say I don't know"},
        {"role": "user", "content": sentence}
    ]
    )
    response = completion.choices[0].message

    print(f"PInput : {sentence}. {response.content}")

    return response


@app.post('/helloWorld', response_class=ORJSONResponse)
async def helloWorld(sentence : str ): 
    return sentence

if __name__ == '__main__':
   
    uvicorn.run(app, host="0.0.0.0", port=5001)
