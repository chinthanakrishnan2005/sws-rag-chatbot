import requests
import json

def test_chat():
    url = "http://127.0.0.1:8000/api/chat"
    payload = {
        "question": "What is the company policy on remote work?"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"Sending question: {payload['question']}")
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("\n--- Response ---")
            print(f"Answer: {result['answer']}")
            print(f"Sources: {', '.join(result['sources']) if result['sources'] else 'None'}")
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure 'uvicorn app:app --reload' is running!")

if __name__ == "__main__":
    test_chat()
