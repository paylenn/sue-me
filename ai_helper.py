import os
from dotenv import load_dotenv
import pytgpt.phind as phind
import json
import logging
import re

load_dotenv()

class ResumeAIHelper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai = phind.PHIND()
        
    def _clean_ai_response(self, response):
        """Clean AI response from welcome messages and extra text"""
        if not response:
            return ""
            
        # Remove common AI welcome/prefix messages
        prefixes = [
            r"Here's a professional summary:",
            r"Here are the enhanced bullet points:",
            r"Here's your enhanced description:",
            r"Here's a suggestion:",
            r"Here's the JSON:",
            r"I'll help you with that\.",
            r"Let me help you with that\.",
            r"I'd be happy to help\.",
            r"Here's what I suggest:",
            r"Sure, I can help with that\.",
            r"Based on the information provided,",
            r"Hello! ",
            r"Hi! ",
        ]
        
        cleaned = response
        for prefix in prefixes:
            cleaned = re.sub(fr"^{prefix}\s*", "", cleaned, flags=re.IGNORECASE)
            
        # Remove any lines that look like AI conversation
        lines = cleaned.split('\n')
        cleaned_lines = [
            line for line in lines
            if not any(phrase in line.lower() for phrase in [
                "i can help",
                "i'll help",
                "i'd be happy",
                "here's what",
                "let me",
                "based on",
                "you can use",
                "would you like",
            ])
        ]
        
        return '\n'.join(cleaned_lines).strip()
        
    def _clean_bullet_points(self, points):
        """Clean bullet points from any AI artifacts"""
        if not points:
            return []
            
        # If it's a string, split it into lines
        if isinstance(points, str):
            points = points.split('\n')
            
        cleaned_points = []
        for point in points:
            # Remove bullet point markers and clean
            clean_point = re.sub(r'^[-*•●■⚫⬤◆◇◈○●]|\d+\.|^\s*\w+\)', '', point)
            clean_point = self._clean_ai_response(clean_point)
            
            # Skip if empty or too short
            if clean_point and len(clean_point) > 5:
                cleaned_points.append(clean_point.strip())
                
        return cleaned_points
        
    def enhance_job_description(self, description):
        """Convert long job descriptions into impactful bullet points"""
        prompt = f"""
        Convert the following job description into 3-5 concise, impactful bullet points.
        Each bullet point should:
        - Start with a strong action verb
        - Include specific achievements or metrics when possible
        - Be no longer than 15 words
        - Focus on accomplishments, not just duties
        
        Description:
        {description}
        
        Format each bullet point on a new line starting with a dash (-)
        """
        try:
            response = self.ai.chat(prompt)
            response = self._clean_ai_response(response)
            
            # Split response into bullet points and clean them up
            bullet_points = [
                point.strip().strip('-').strip() 
                for point in response.split('\n') 
                if point.strip() and point.strip().startswith('-')
            ]
            
            # Clean the bullet points
            bullet_points = self._clean_bullet_points(bullet_points)
            
            # Take only the first 5 bullet points
            return bullet_points[:5]
        except Exception as e:
            self.logger.error(f"Error enhancing job description: {str(e)}")
            # If AI fails, split the original description into sentences
            sentences = description.split('.')
            return self._clean_bullet_points([s.strip() for s in sentences[:3] if s.strip()])
            
    def generate_summary(self, experience, skills):
        """Generate a professional summary based on experience and skills"""
        latest_role = experience[0] if experience else {}
        prompt = f"""
        Write a powerful 2-sentence professional summary for a {latest_role.get('position', 'professional')}.
        First sentence: Highlight years of experience and key achievements.
        Second sentence: Focus on top skills and value provided.
        Keep it under 50 words total.
        
        Experience highlights:
        {', '.join(latest_role.get('highlights', [])[:2])}
        
        Key skills:
        Technical: {', '.join(skills['technical'][:3])}
        Soft: {', '.join(skills['soft'][:3])}
        """
        
        try:
            response = self.ai.chat(prompt)
            return self._clean_ai_response(response)
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return ""
            
    def suggest_skills(self, experience, current_skills):
        """Suggest additional relevant skills based on experience"""
        # Clean up current skills - remove duplicates and placeholders
        cleaned_skills = {
            'technical': list(set(s for s in current_skills['technical'] if not s.startswith('Skill '))),
            'soft': list(set(s for s in current_skills['soft'] if not s.startswith('Skill ')))
        }
        
        experience_text = "\n".join([
            f"Position: {exp['position']} at {exp['company']}"
            for exp in experience
        ])
        
        prompt = f"""
        Based on this healthcare professional's experience, suggest relevant skills.
        Return only a JSON object with two lists: "technical" and "soft".
        Focus on healthcare-specific technical skills and relevant soft skills.
        
        Current technical skills: {', '.join(cleaned_skills['technical'])}
        Current soft skills: {', '.join(cleaned_skills['soft'])}
        
        Experience:
        {experience_text}
        """
        
        try:
            response = self.ai.chat(prompt)
            response = self._clean_ai_response(response)
            
            try:
                # Try to find JSON-like content in the response
                json_match = re.search(r'\{[^}]+\}', response)
                if json_match:
                    response = json_match.group(0)
                    
                skills = json.loads(response)
                # Remove any duplicates with current skills
                suggested = {
                    'technical': list(set(skills.get('technical', [])) - set(cleaned_skills['technical'])),
                    'soft': list(set(skills.get('soft', [])) - set(cleaned_skills['soft']))
                }
                return suggested
            except json.JSONDecodeError:
                return {'technical': [], 'soft': []}
        except Exception as e:
            self.logger.error(f"Error suggesting skills: {str(e)}")
            return {'technical': [], 'soft': []}
            
    def improve_resume(self, resume_data):
        """Improve an entire resume with AI suggestions"""
        # Clean up skills first
        resume_data['skills']['technical'] = list(set(
            s for s in resume_data['skills']['technical'] 
            if not s.startswith('Skill ')
        ))
        resume_data['skills']['soft'] = list(set(
            s for s in resume_data['skills']['soft']
        ))
        
        # Remove placeholder education entries
        resume_data['education'] = [
            edu for edu in resume_data['education']
            if not (edu['institution'] == "University Name" or 
                   edu['field'] == "Field of Study")
        ]
        
        # Enhance job descriptions
        for exp in resume_data['experience']:
            if isinstance(exp['highlights'], list):
                if len(exp['highlights']) == 1 and len(exp['highlights'][0]) > 200:
                    # If it's one long paragraph, convert to bullet points
                    exp['highlights'] = self.enhance_job_description(exp['highlights'][0])
            else:
                exp['highlights'] = self.enhance_job_description(str(exp['highlights']))
        
        # Generate or improve summary
        if not resume_data.get('summary') or resume_data['summary'] == "Experienced professional with expertise in...":
            resume_data['summary'] = self.generate_summary(
                resume_data['experience'],
                resume_data['skills']
            )
        
        # Suggest additional skills
        suggested_skills = self.suggest_skills(
            resume_data['experience'],
            resume_data['skills']
        )
        
        # Add suggested skills
        for skill_type in ['technical', 'soft']:
            current_skills = set(resume_data['skills'][skill_type])
            suggested = set(suggested_skills[skill_type])
            new_skills = suggested - current_skills
            resume_data['skills'][skill_type].extend(list(new_skills))
            
            # Final cleanup of skills
            resume_data['skills'][skill_type] = sorted(list(set(
                skill for skill in resume_data['skills'][skill_type]
                if not skill.startswith('Skill ') and len(skill) > 2
            )))
        
        return resume_data
