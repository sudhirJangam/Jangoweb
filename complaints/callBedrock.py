import boto3
import langchain
import json

def callBedrock(model_id, text):
    """
    Generate a vector of embeddings for a text input using Amazon Titan Text Embeddings G1 on demand.
    Args:
        model_id (str): The model ID to use.
        body (str) : The request body to use.
    Returns:
        response (JSON): The text that the model generated, token information, and the
        reason the model stopped generating text.
    """

    bedrock = boto3.client(service_name='bedrock-runtime',
                           region_name=AWS_REGION,
                           aws_access_key_id=ACCESS_KEY,
                           aws_secret_access_key=SECRET_ACCESS_KEY )

    promptHead = ("\\n\\nHuman: You are a customer service agent tasked with classifying emails by type. "
              "Please output your answer and then justify your classification. How would you categorize "
              "this email?\\n<email>\\n")

    categories= ("\\n<email>\\nThe categories are: \\n(A) Credit card \\n(B) Mortgage "
                 "\\n(C) vehical loan\\n(D) Other (please explain)\\n\\nAssistant:\\n")

    prompt=promptHead+text+categories

    accept = "application/json"
    content_type = "application/json"
    body= {"messages": [{ "role": "user",
                         "content": [ { "type" : "text",
                                        "text" :prompt
                                       }]
                         }],
           "anthropic_version": "bedrock-2023-05-31", "temperature": 0.5,
           "top_k":250,"top_p":1, "max_tokens":2048,"stop_sequences":["\\n\\nHuman:"] }

    body_bytes = json.dumps(body).encode('utf-8')

    response = bedrock.invoke_model(
        body=body_bytes, modelId=model_id, accept=accept, contentType=content_type)

    response_body = json.loads(response.get('body').read())
    print(response_body)
    return response_body
