import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import json
import logging
import os

console = Console()

class InteractiveConfig:
    def __init__(self):
        self.console = Console()

    def _get_personal_info(self, existing=None):
        existing = existing or {}
        console.print(Panel.fit("📝 Personal Information", style="bold blue"))
        
        return {
            "name": Prompt.ask("Full Name", default=existing.get("name", "")),
            "email": Prompt.ask("Email", default=existing.get("email", "")),
            "phone": Prompt.ask("Phone", default=existing.get("phone", "")),
            "address": Prompt.ask("Location (City, State)", default=existing.get("address", "")),
            "linkedin": Prompt.ask("LinkedIn URL (optional)", default=existing.get("linkedin", "")),
            "github": Prompt.ask("GitHub URL (optional)", default=existing.get("github", ""))
        }

    def _get_experience(self, existing=None):
        existing = existing or []
        experiences = []
        console.print(Panel.fit("💼 Work Experience", style="bold blue"))
        
        if existing:
            console.print("\nExisting experience entries:")
            for i, exp in enumerate(existing, 1):
                console.print(f"\n[bold]#{i} {exp['position']} at {exp['company']}[/bold]")
                console.print(f"Location: {exp['location']}")
                console.print(f"Duration: {exp['start_date']} - {exp['end_date']}")
                console.print("\nHighlights:")
                for highlight in exp['highlights']:
                    console.print(f"• {highlight}")
                
                if Confirm.ask(f"\nKeep this experience entry?", default=True):
                    experiences.append(exp)
                else:
                    console.print("Entry removed.")

        while True:
            if Confirm.ask("\nAdd a new experience entry?", default=True):
                exp = {
                    "company": Prompt.ask("Company Name"),
                    "position": Prompt.ask("Position/Title"),
                    "location": Prompt.ask("Location"),
                    "start_date": Prompt.ask("Start Date (YYYY-MM)"),
                    "end_date": Prompt.ask("End Date (YYYY-MM or 'Present')"),
                    "highlights": []
                }
                
                console.print("\nEnter job highlights (achievements, responsibilities)")
                while True:
                    highlight = Prompt.ask("Add highlight (or press enter to finish)")
                    if not highlight:
                        break
                    exp["highlights"].append(highlight)
                
                experiences.append(exp)
            else:
                break
        
        return experiences

    def _get_education(self, existing=None):
        existing = existing or []
        education = []
        console.print(Panel.fit("🎓 Education", style="bold blue"))
        
        if existing:
            console.print("\nExisting education entries:")
            for i, edu in enumerate(existing, 1):
                console.print(f"\n[bold]#{i} {edu['degree']} in {edu['field']}[/bold]")
                console.print(f"Institution: {edu['institution']}")
                console.print(f"Graduation: {edu['graduation_date']}")
                if edu.get('gpa'):
                    console.print(f"GPA: {edu['gpa']}")
                
                if Confirm.ask(f"\nKeep this education entry?", default=True):
                    education.append(edu)
                else:
                    console.print("Entry removed.")

        while True:
            if Confirm.ask("\nAdd a new education entry?", default=True):
                edu = {
                    "institution": Prompt.ask("Institution Name"),
                    "degree": Prompt.ask("Degree Type"),
                    "field": Prompt.ask("Field of Study"),
                    "graduation_date": Prompt.ask("Graduation Date (YYYY-MM)"),
                    "gpa": Prompt.ask("GPA (optional)", default="")
                }
                education.append(edu)
            else:
                break
        
        return education

    def _get_skills(self, existing=None):
        existing = existing or {"technical": [], "soft": []}
        console.print(Panel.fit("🔧 Skills", style="bold blue"))
        
        skills = {
            "technical": [],
            "soft": []
        }
        
        if existing.get("technical"):
            console.print("\n[bold]Existing Technical Skills:[/bold]")
            for i, skill in enumerate(existing["technical"], 1):
                console.print(f"{i}. {skill}")
            
            if Confirm.ask("\nWould you like to keep these technical skills?", default=True):
                skills["technical"].extend(existing["technical"])
            else:
                console.print("Technical skills cleared.")

        if Confirm.ask("\nAdd new technical skills?", default=True):
            console.print("\nEnter new technical skills (programming languages, tools, etc.)")
            while True:
                skill = Prompt.ask("Add technical skill (or press enter to finish)")
                if not skill:
                    break
                skills["technical"].append(skill)
        
        if existing.get("soft"):
            console.print("\n[bold]Existing Soft Skills:[/bold]")
            for i, skill in enumerate(existing["soft"], 1):
                console.print(f"{i}. {skill}")
            
            if Confirm.ask("\nWould you like to keep these soft skills?", default=True):
                skills["soft"].extend(existing["soft"])
            else:
                console.print("Soft skills cleared.")

        if Confirm.ask("\nAdd new soft skills?", default=True):
            console.print("\nEnter new soft skills (leadership, communication, etc.)")
            while True:
                skill = Prompt.ask("Add soft skill (or press enter to finish)")
                if not skill:
                    break
                skills["soft"].append(skill)
        
        return skills

    def _get_volunteer_work(self, existing=None):
        """Get volunteer work information."""
        existing = existing or []
        volunteer_work = []
        
        console.print(Panel.fit("🤝 Volunteer Work", style="bold blue"))
        
        if existing:
            console.print("\nExisting volunteer work:")
            for i, work in enumerate(existing, 1):
                console.print(f"\n{i}. {work['organization']}")
                console.print(f"   Role: {work['role']}")
                console.print(f"   Duration: {work['start_date']} - {work['end_date']}")
                console.print("   Contributions:")
                for contribution in work['contributions']:
                    console.print(f"   • {contribution}")
            
            if not Confirm.ask("\nWould you like to keep this volunteer work?"):
                existing = []
            else:
                volunteer_work.extend(existing)
        
        while Confirm.ask("\nWould you like to add volunteer work?"):
            work = {}
            work["organization"] = Prompt.ask("Organization name")
            work["role"] = Prompt.ask("Your role")
            work["start_date"] = Prompt.ask("Start date (YYYY-MM)")
            work["end_date"] = Prompt.ask("End date (YYYY-MM or 'Present')")
            
            contributions = []
            while Confirm.ask("Would you like to add a contribution?"):
                contribution = Prompt.ask("Enter contribution")
                contributions.append(contribution)
            work["contributions"] = contributions
            
            volunteer_work.append(work)
        
        return volunteer_work

    def _generate_ai_summary(self, config):
        """Generate a summary using AI based on experience and skills."""
        experience = config.get("experience", [])
        skills = config.get("skills", {})
        
        if not experience:
            return "Experienced professional with expertise in..."
            
        latest_role = experience[0]
        tech_skills = skills.get("technical", [])
        soft_skills = skills.get("soft", [])
        
        return f"Dedicated healthcare professional with {len(experience)} years of experience, specializing in {latest_role['position']} at {latest_role['company']}. Proven expertise in {', '.join(tech_skills[:3])} with strong capabilities in {', '.join(soft_skills[:3])}. Demonstrated track record of providing exceptional care and maintaining high standards of service delivery."

    def _get_summary(self, existing=None, config=None):
        existing = existing or ""
        console.print(Panel.fit("💡 Professional Summary", style="bold blue"))
        
        if existing and existing != "Experienced professional with expertise in...":
            console.print("\nCurrent summary:")
            console.print(f"[italic]{existing}[/italic]")
            
            if Confirm.ask("Would you like to enhance this summary using AI?"):
                return self._generate_ai_summary(config)
            elif Confirm.ask("Would you like to enter a custom summary?"):
                return Prompt.ask("Enter your professional summary")
            return existing
        else:
            if Confirm.ask("Would you like to generate a professional summary using AI?"):
                return self._generate_ai_summary(config)
            elif Confirm.ask("Would you like to enter a custom summary?"):
                return Prompt.ask("Enter your professional summary")
            return self._generate_ai_summary(config)

    def _configure_template(self, existing=None, web_mode=False):
        existing = existing or {
            'name': 'modern',
            'colors': {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'text': '#333333'
            },
            'font': {
                'main': 'Arial',
                'heading': 'Helvetica'
            }
        }
        
        console.print("\n[bold blue]Template Configuration[/bold blue]")
        template = {'colors': {}, 'font': {}}
        
        # Template selection
        template_options = {
            'modern': 'Modern and clean design with emphasis on readability',
            'minimal': 'Simple and elegant layout with minimal styling',
            'professional': 'Traditional professional layout with subtle enhancements',
            'creative': 'Bold two-column design with a colored sidebar',
            'executive': 'Sophisticated design for senior positions with gold accents',
            'medical': 'Healthcare-focused design with medical-themed colors',
            'elegant': 'Refined layout with serif fonts and classic styling',
            'compact': 'Space-efficient design that fits more content',
            'contemporary': 'Fresh and modern look with gradient accents',
            'traditional': 'Classic resume layout with timeless appeal'
        }
        
        console.print("\nAvailable Templates:")
        for name, description in template_options.items():
            console.print(f"[bold]{name}[/bold]: {description}")
        
        template['name'] = Prompt.ask(
            "Select template",
            choices=list(template_options.keys()),
            default=existing.get('name', 'modern')
        )

        # Web template selection (only if in web mode)
        if web_mode:
            web_template_options = {
                'modern': 'Modern card-based design with gradient header',
                'minimal': 'Clean and simple centered layout',
                'creative': 'Unique sidebar design with timeline'
            }
            
            console.print("\nAvailable Web Templates:")
            for name, description in web_template_options.items():
                console.print(f"[bold]{name}[/bold]: {description}")
            
            template['web_template'] = Prompt.ask(
                "Select web template",
                choices=list(web_template_options.keys()),
                default=existing.get('web_template', 'modern')
            )
        else:
            # Keep existing web template if present
            if 'web_template' in existing:
                template['web_template'] = existing['web_template']
        
        # Color schemes based on template
        color_schemes = {
            'modern': {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'text': '#333333'
            },
            'minimal': {
                'primary': '#000000',
                'secondary': '#666666',
                'text': '#333333'
            },
            'professional': {
                'primary': '#1a4367',
                'secondary': '#2c88d9',
                'text': '#2c3e50'
            },
            'creative': {
                'primary': '#2c3e50',
                'secondary': '#e74c3c',
                'text': '#2c3e50'
            },
            'executive': {
                'primary': '#2c3e50',
                'secondary': '#c0a080',
                'text': '#333333'
            },
            'medical': {
                'primary': '#005f73',
                'secondary': '#0a9396',
                'text': '#001219'
            },
            'elegant': {
                'primary': '#2b2d42',
                'secondary': '#8d99ae',
                'text': '#2b2d42'
            },
            'compact': {
                'primary': '#2b2d42',
                'secondary': '#8d99ae',
                'text': '#2b2d42'
            },
            'contemporary': {
                'primary': '#2563eb',
                'secondary': '#4f46e5',
                'text': '#1f2937'
            },
            'traditional': {
                'primary': '#14213d',
                'secondary': '#284b63',
                'text': '#14213d'
            }
        }
        
        default_colors = color_schemes[template['name']]
        
        if Confirm.ask("\nWould you like to customize the colors?", default=False):
            template['colors']['primary'] = Prompt.ask(
                "Primary Color (hex code)",
                default=default_colors['primary']
            )
            template['colors']['secondary'] = Prompt.ask(
                "Secondary Color (hex code)",
                default=default_colors['secondary']
            )
            template['colors']['text'] = Prompt.ask(
                "Text Color (hex code)",
                default=default_colors['text']
            )
        else:
            template['colors'] = default_colors

        # Font configuration
        font_options = {
            'modern': {'main': 'Roboto', 'heading': 'Roboto'},
            'minimal': {'main': 'Inter', 'heading': 'Inter'},
            'professional': {'main': 'Source Sans Pro', 'heading': 'Source Sans Pro'},
            'creative': {'main': 'Montserrat', 'heading': 'Montserrat'},
            'executive': {'main': 'Libre Baskerville', 'heading': 'Libre Baskerville'},
            'medical': {'main': 'Source Sans Pro', 'heading': 'Source Sans Pro'},
            'elegant': {'main': 'Cormorant Garamond', 'heading': 'Cormorant Garamond'},
            'compact': {'main': 'Open Sans', 'heading': 'Open Sans'},
            'contemporary': {'main': 'Poppins', 'heading': 'Poppins'},
            'traditional': {'main': 'Crimson Text', 'heading': 'Crimson Text'}
        }

        default_fonts = font_options[template['name']]
        
        if Confirm.ask("\nWould you like to customize the fonts?", default=False):
            template['font'] = {
                'main': Prompt.ask("Main Font", default=default_fonts['main']),
                'heading': Prompt.ask("Heading Font", default=default_fonts['heading'])
            }
        else:
            template['font'] = default_fonts
        
        return template

    def save_config(self, config_path, config):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        console.print("[dim]Configuration saved[/dim]")

    def run(self, config_path, existing_config=None, web_mode=False):
        """Run interactive configuration"""
        if existing_config:
            config = existing_config
        else:
            config = {}

        # Personal Information
        config["personal_info"] = self._get_personal_info(config.get("personal_info"))
        self.save_config(config_path, config)

        # Experience
        config["experience"] = self._get_experience(config.get("experience"))
        self.save_config(config_path, config)

        # Education
        config["education"] = self._get_education(config.get("education"))
        self.save_config(config_path, config)

        # Volunteer Work
        config["volunteer_work"] = self._get_volunteer_work(config.get("volunteer_work"))
        self.save_config(config_path, config)

        # Skills
        config["skills"] = self._get_skills(config.get("skills"))
        self.save_config(config_path, config)

        # Summary (pass the full config for AI generation)
        config["summary"] = self._get_summary(config.get("summary"), config)
        self.save_config(config_path, config)

        # Template
        config["template"] = self._configure_template(config.get("template"), web_mode)
        self.save_config(config_path, config)

        return config

    def load_config(self, config_path):
        """Load existing configuration"""
        try:
            with open(config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            console.print(f"\n❌ Error loading configuration: {str(e)}", style="bold red")
            raise

@click.command()
@click.option('--config', default='config/resume_config.json', help='Path to configuration file')
@click.option('--web-mode', is_flag=True, help='Enable web template selection')
def main(config, web_mode):
    """Interactive resume configuration tool"""
    try:
        config_tool = InteractiveConfig()
        existing_config = config_tool.load_config(config)
        config_tool.run(config, existing_config, web_mode)
    except KeyboardInterrupt:
        console.print("\n\nConfiguration cancelled by user", style="bold yellow")
        exit(0)
    except Exception as e:
        console.print(f"\nError: {str(e)}", style="bold red")
        exit(1)

if __name__ == '__main__':
    main()
