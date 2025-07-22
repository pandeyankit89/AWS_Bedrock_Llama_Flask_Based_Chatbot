from flask import Flask, render_template, request, jsonify
import os
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# AWS credentials and Bedrock client setup
client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Set the model ID, e.g., Llama 3 8b Instruct.
model_id = "meta.llama3-8b-instruct-v1:0"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    system_prompt = "While Answering, answer in limited words, to the point if possible"
    user_input = request.json['message']
    # Construct LLaMA-style prompt
    llama_prompt = f"""[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_input} [/INST]"""
    conversation = [
        {
            "role": "user",
            "content": [{"text": llama_prompt}],
        }
    ]
    
    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]
        return jsonify({'reply': response_text})
    
    except Exception as e:
        return jsonify({'reply': f"ERROR: Can't invoke '{model_id}'. Reason: {e}"}), 500

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True)

