"""
Main entry point for the ConverSync Meeting Assistant
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.meeting_assistant import MeetingAssistant
from config import Config

def main():
    """Main function to run the meeting assistant."""
    print("🤖 ConverSync Meeting Assistant")
    print("=" * 40)
    
    try:
        # Initialize the assistant
        assistant = MeetingAssistant()
        
        # Test services
        print("Testing services...")
        service_status = assistant.test_services()
        
        print("\nService Status:")
        for service, status in service_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {service.title()}: {'OK' if status else 'Failed'}")
        
        if not all(service_status.values()):
            print("\n⚠️  Some services failed. Please check your configuration.")
            return False
        
        print("\n🎉 All services are working correctly!")
        print("\nYou can now:")
        print("1. Use the Python API directly (see example_usage.py)")
        print("2. Start the web API: python api/flask_app.py")
        print("3. Process files programmatically")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing services: {e}")
        print("\nPlease check:")
        print("1. Your .env file configuration")
        print("2. API keys are valid")
        print("3. Network connectivity")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
