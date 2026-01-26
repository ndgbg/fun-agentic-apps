"""
Lambda function to handle Bedrock Agent action group requests
Deploy this as an AWS Lambda function to handle agent actions
"""

import json

def lambda_handler(event, context):
    """
    Handle Bedrock Agent action group invocations
    
    Event structure from Bedrock:
    {
        "messageVersion": "1.0",
        "agent": {...},
        "inputText": "user input",
        "sessionId": "session-id",
        "actionGroup": "action-group-name",
        "apiPath": "/api/path",
        "httpMethod": "GET",
        "parameters": [...]
    }
    """
    
    # Extract action details
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = event.get('parameters', [])
    
    # Convert parameters to dict
    params_dict = {param['name']: param['value'] for param in parameters}
    
    # Route to appropriate handler
    if api_path == '/get_weather':
        result = get_weather(params_dict.get('location', 'Unknown'))
    else:
        result = {"error": f"Unknown API path: {api_path}"}
    
    # Return response in Bedrock format
    response = {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": event.get('httpMethod', 'GET'),
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(result)
                }
            }
        }
    }
    
    return response


def get_weather(location: str) -> dict:
    """Mock weather function - replace with actual API call"""
    
    # This is a mock response - in production, call a real weather API
    mock_weather = {
        "location": location,
        "temperature": 72,
        "condition": "Sunny",
        "humidity": 45,
        "wind_speed": 10
    }
    
    return mock_weather
