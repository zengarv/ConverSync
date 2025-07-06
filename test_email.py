import requests
import json

# Test the email functionality
def test_email_functionality():
    base_url = "http://localhost:5000"
    
    # Step 1: Start a chat session with a test transcript
    test_transcript = """
    Speaker 1: Welcome everyone to today's team meeting. We have several important items to discuss today.
    Speaker 2: Thank you for organizing this meeting. I'd like to start by presenting the quarterly sales results.
    Speaker 1: Excellent. The numbers look promising this quarter.
    Speaker 2: Yes, we've exceeded our targets by 15%. The new marketing campaign has been very effective.
    Speaker 3: That's great news! I think we should also discuss the upcoming product launch.
    Speaker 1: Absolutely. Sarah, can you give us an update on the development timeline?
    Speaker 3: The development is on track. We're planning to launch in two weeks.
    Speaker 2: Perfect. We'll need to coordinate the marketing materials with the launch date.
    Speaker 1: Action items: Sarah will provide final timeline by Friday, Marketing team will prepare launch materials.
    Speaker 3: Agreed. Meeting adjourned.
    """
    
    # Start session
    print("🔄 Starting chat session...")
    session_response = requests.post(f"{base_url}/chat/start", 
                                   json={"transcript": test_transcript})
    
    if session_response.status_code != 200:
        print(f"❌ Failed to start session: {session_response.text}")
        return False
    
    session_data = session_response.json()
    session_id = session_data["session_id"]
    print(f"✅ Session started: {session_id}")
    
    # Step 2: Test email sending
    email_data = {
        "recipients": ["test@example.com"],
        "meeting_title": "Test Meeting",
        "meeting_date": "2025-01-07",
        "company_name": "Test Company",
        "custom_message": "This is a test email from the ConverSync API."
    }
    
    print("🔄 Sending test email...")
    email_response = requests.post(f"{base_url}/chat/{session_id}/send-email",
                                 json=email_data)
    
    print(f"📧 Email response status: {email_response.status_code}")
    print(f"📧 Email response: {email_response.text}")
    
    if email_response.status_code == 200:
        print("✅ Email endpoint responded successfully!")
        result = email_response.json()
        print(f"📧 Result: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Email failed: {email_response.text}")
    
    return email_response.status_code == 200

if __name__ == "__main__":
    test_email_functionality()
