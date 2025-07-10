import google.generativeai as genai
from config import Config

class SummarizationService:
    """Service for generating meeting summaries using Gemini API."""
    
    def __init__(self):
        Config.validate_config()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = Config.GEMINI_MODEL
    
    def _gpt(self, prompt: str) -> str:
        """Send prompt to Gemini and return plain-text answer."""
        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            
            # Check if response has valid content
            if not hasattr(response, 'text') or not response.text:
                # Try to get more info about why it failed
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        reason = candidate.finish_reason
                        if reason == 8:  # PROHIBITED_CONTENT
                            raise Exception("Content was blocked by Gemini's safety filters. Try with different content.")
                        else:
                            raise Exception(f"Gemini failed to generate content. Finish reason: {reason}")
                raise Exception("Gemini returned empty response")
            
            return response.text.strip()
        except Exception as e:
            if "finish_reason" in str(e) and "8" in str(e):
                raise Exception(f"Content blocked by Gemini safety filters. Please try with different meeting content.")
            raise Exception(f"Error generating content with Gemini: {e}")
    
    def generate_meeting_summary(self, transcript: str) -> dict:
        """
        Generate a comprehensive meeting summary from transcript.
        
        Args:
            transcript (str): The meeting transcript text.
            
        Returns:
            dict: Dictionary containing different sections of the meeting summary.
        """
        try:
            sections = {}
            
            # Executive Summary
            summary_prompt = f"""
            Please provide a concise executive summary of the following meeting transcript.
            Focus on the main topics discussed and overall outcomes.
            Keep the response professional and factual.
            
            Transcript:
            {transcript[:2000]}...
            
            Provide a 2-3 paragraph executive summary:
            """
            sections["Executive Summary"] = self._gpt(summary_prompt)
            
            # Meeting Agenda & Timeline
            agenda_prompt = f"""
            Based on the following meeting transcript, extract and organize the agenda items and timeline.
            List the main topics discussed in chronological order.
            
            Transcript:
            {transcript[:2000]}...
            
            Provide a structured agenda/timeline:
            """
            sections["Agenda & Timeline"] = self._gpt(agenda_prompt)
            
            # Key Speaker Points
            speakers_prompt = f"""
            From the following meeting transcript, identify key speakers and their main contributions.
            Summarize the important points made by each speaker.
            
            Transcript:
            {transcript[:2000]}...
            
            Provide key speaker points:
            """
            sections["Key Speaker Points"] = self._gpt(speakers_prompt)
            
            # Decisions Made
            decisions_prompt = f"""
            Extract all decisions that were made during this meeting from the transcript.
            List them clearly with any relevant context.
            
            Transcript:
            {transcript[:2000]}...
            
            List all decisions made:
            """
            sections["Decisions Made"] = self._gpt(decisions_prompt)
            
            # Action Items
            actions_prompt = f"""
            Identify all action items assigned during this meeting from the transcript.
            Include who is responsible for each action and any deadlines mentioned.
            
            Transcript:
            {transcript[:2000]}...
            
            List all action items:
            """
            sections["Action Items"] = self._gpt(actions_prompt)
            
            return sections
            
        except Exception as e:
            print(f"⚠️  Gemini AI failed to generate summary: {e}")
            print("🔄 Using fallback summary generation...")
            return self.generate_fallback_summary(transcript)
        
    
    def generate_custom_summary(self, transcript: str, custom_prompt: str) -> str:
        """
        Generate a custom summary based on a specific prompt.
        
        Args:
            transcript (str): The meeting transcript text.
            custom_prompt (str): Custom prompt for specific analysis.
            
        Returns:
            str: Generated summary based on custom prompt.
        """
        full_prompt = f"""
        {custom_prompt}
        
        Meeting Transcript:
        {transcript}
        """
        return self._gpt(full_prompt)
    
    def extract_participants(self, transcript: str) -> str:
        """
        Extract list of meeting participants from transcript.
        
        Args:
            transcript (str): The meeting transcript text.
            
        Returns:
            str: List of identified participants.
        """
        prompt = f"""
        From the following meeting transcript, identify and list all participants/speakers.
        
        Transcript:
        {transcript}
        
        Provide a list of participants:
        """
        return self._gpt(prompt)
    
    def analyze_sentiment(self, transcript: str) -> str:
        """
        Analyze the overall sentiment and tone of the meeting.
        
        Args:
            transcript (str): The meeting transcript text.
            
        Returns:
            str: Sentiment analysis of the meeting.
        """
        prompt = f"""
        Analyze the overall sentiment and tone of the following meeting transcript.
        Consider the mood, level of agreement/disagreement, and overall atmosphere.
        
        Transcript:
        {transcript}
        
        Provide sentiment analysis:
        """
        return self._gpt(prompt)
    
    def generate_fallback_summary(self, transcript: str) -> dict:
        """
        Generate a basic summary without AI when Gemini fails.
        
        Args:
            transcript (str): The meeting transcript text.
            
        Returns:
            dict: Dictionary containing basic sections of the meeting summary.
        """
        # Basic text analysis for fallback
        lines = transcript.split('\n')
        total_lines = len(lines)
        word_count = len(transcript.split())
        
        # Create basic sections
        sections = {
            "Executive Summary": f"""
Meeting Summary:
This meeting covered various topics as discussed in the transcript. The conversation involved multiple participants and lasted for approximately {total_lines} exchanges. A total of {word_count} words were spoken during the session.

Key topics and discussions can be found in the full transcript. Due to content processing limitations, this is a basic summary. Please refer to the complete transcript for detailed information.

For more detailed analysis, please try generating the summary again or contact support if the issue persists.
            """.strip(),
            
            "Agenda & Timeline": f"""
Meeting Structure:
- Total discussion points: {total_lines} exchanges
- Word count: {word_count} words
- The meeting followed a structured discussion format
- Multiple topics were covered during the session

Timeline: The meeting proceeded through various agenda items in chronological order as recorded in the transcript.
            """.strip(),
            
            "Key Points": f"""
Meeting Highlights:
- {total_lines} discussion exchanges recorded
- Multiple participants contributed to the conversation
- Various topics and decisions were discussed
- Action items and follow-ups were likely addressed

Note: This is a basic summary. For detailed key points, please refer to the full transcript.
            """.strip(),
            
            "Action Items": """
Action Items Summary:
Due to content processing limitations, specific action items could not be automatically extracted. 

Please review the full meeting transcript to identify:
- Specific tasks assigned to team members
- Deadlines and timelines mentioned
- Follow-up actions required
- Responsibilities assigned to individuals

For detailed action item extraction, please try generating the summary again.
            """.strip()
        }
        
        return sections
