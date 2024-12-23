import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
import pytgpt.phind as phind
import os
import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from interactive_config import InteractiveConfig
from datetime import datetime
import webbrowser
import re

console = Console()
bot = phind.PHIND()

def display_menu():
    """Display the main menu options."""
    table = Table(title="Resume Generator Menu", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="green")
    
    table.add_row("1", "Create/Update Resume")
    table.add_row("2", "Generate PDF/HTML Output")
    table.add_row("3", "AI Resume Enhancement")
    table.add_row("4", "Template Management")
    table.add_row("5", "Ask AI Assistant")
    table.add_row("6", "Exit")
    
    console.print(table)

def parse_ai_suggestions(suggestions):
    """Parse AI suggestions and convert them into actionable changes."""
    sections = {}
    current_section = None
    current_content = []
    
    # Split suggestions into lines and process each line
    for line in suggestions.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a new section header (numbered or not)
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
            section_name = line.split('.', 1)[1].strip().split(':', 1)[0].lower()
            if current_section and current_content:
                sections[current_section] = current_content
            current_section = section_name
            current_content = []
        elif line.startswith('-'):
            if current_section:
                current_content.append(line[1:].strip())
    
    # Add the last section
    if current_section and current_content:
        sections[current_section] = current_content
        
    return sections

def apply_ai_suggestions(config, sections):
    """Apply parsed AI suggestions to the resume configuration."""
    changes_made = []
    
    # Apply summary suggestions
    if 'summary' in sections:
        summary_prompt = (
            "Based on these suggestions:\n" + 
            "\n".join(f"- {s}" for s in sections['summary']) +
            f"\n\nRewrite this summary to incorporate the suggestions:\n{config.get('summary', '')}"
        )
        new_summary = bot.chat(summary_prompt)
        if new_summary and new_summary != config.get('summary', ''):
            config['summary'] = new_summary
            changes_made.append("Updated summary based on AI suggestions")
    
    # Apply experience suggestions
    if 'experience' in sections:
        exp_suggestions = sections['experience']
        for exp in config.get('experience', []):
            exp_prompt = (
                "Based on these suggestions:\n" +
                "\n".join(f"- {s}" for s in exp_suggestions) +
                f"\n\nEnhance these experience highlights for {exp['position']} at {exp['company']}:\n" +
                "\n".join(exp['highlights'])
            )
            enhanced_highlights = bot.chat(exp_prompt)
            if enhanced_highlights:
                try:
                    # Try to parse as a list if it looks like one
                    if enhanced_highlights.strip().startswith('['):
                        new_highlights = eval(enhanced_highlights)
                    else:
                        new_highlights = [h.strip() for h in enhanced_highlights.split('\n') if h.strip()]
                    
                    if new_highlights and new_highlights != exp['highlights']:
                        exp['highlights'] = new_highlights
                        changes_made.append(f"Enhanced highlights for {exp['company']}")
                except:
                    console.print(f"[yellow]Warning: Could not parse enhanced highlights for {exp['company']}[/yellow]")
    
    # Apply skills suggestions
    if 'skills' in sections:
        skills_prompt = (
            "Based on these suggestions:\n" +
            "\n".join(f"- {s}" for s in sections['skills']) +
            f"\n\nEnhance and organize these skills:\n{config.get('skills', {})}\n" +
            "Return the result as a Python dictionary with categories as keys and lists of skills as values."
        )
        enhanced_skills = bot.chat(skills_prompt)
        if enhanced_skills:
            try:
                new_skills = eval(enhanced_skills)
                if isinstance(new_skills, dict) and new_skills != config.get('skills', {}):
                    config['skills'] = new_skills
                    changes_made.append("Updated and reorganized skills based on AI suggestions")
            except:
                console.print("[yellow]Warning: Could not parse enhanced skills[/yellow]")
    
    # Apply volunteer work suggestions
    if 'volunteer work' in sections and 'volunteer_work' in config:
        vol_suggestions = sections['volunteer work']
        for vol in config['volunteer_work']:
            vol_prompt = (
                "Based on these suggestions:\n" +
                "\n".join(f"- {s}" for s in vol_suggestions) +
                f"\n\nEnhance these volunteer contributions for {vol['organization']}:\n" +
                "\n".join(vol['contributions'])
            )
            enhanced_contributions = bot.chat(vol_prompt)
            if enhanced_contributions:
                try:
                    if enhanced_contributions.strip().startswith('['):
                        new_contributions = eval(enhanced_contributions)
                    else:
                        new_contributions = [c.strip() for c in enhanced_contributions.split('\n') if c.strip()]
                    
                    if new_contributions and new_contributions != vol['contributions']:
                        vol['contributions'] = new_contributions
                        changes_made.append(f"Enhanced volunteer work for {vol['organization']}")
                except:
                    console.print(f"[yellow]Warning: Could not parse enhanced contributions for {vol['organization']}[/yellow]")
    
    # Apply education suggestions if present
    if 'education' in sections and 'education' in config:
        edu_suggestions = sections['education']
        for edu in config['education']:
            edu_prompt = (
                "Based on these suggestions:\n" +
                "\n".join(f"- {s}" for s in edu_suggestions) +
                f"\n\nEnhance this education entry for {edu.get('institution', '')}:\n{edu}"
            )
            enhanced_edu = bot.chat(edu_prompt)
            if enhanced_edu:
                try:
                    new_edu = eval(enhanced_edu)
                    if isinstance(new_edu, dict) and new_edu != edu:
                        edu.update(new_edu)
                        changes_made.append(f"Enhanced education details for {edu.get('institution', '')}")
                except:
                    console.print(f"[yellow]Warning: Could not parse enhanced education for {edu.get('institution', '')}[/yellow]")
    
    return config, changes_made

def ai_enhance_resume(config):
    """Use AI to enhance the resume content."""
    console.print(Panel.fit("🤖 AI Resume Enhancement", style="bold blue"))
    
    options = [
        "Enhance Summary",
        "Improve Experience Descriptions",
        "Optimize Skills Section",
        "Review Entire Resume",
        "Back to Main Menu"
    ]
    
    table = Table(title="Enhancement Options", show_header=True)
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="green")
    
    for i, option in enumerate(options, 1):
        table.add_row(str(i), option)
    
    console.print(table)
    
    choice = Prompt.ask("Select an option", choices=[str(i) for i in range(1, len(options) + 1)])
    
    if choice == "1":
        if 'summary' not in config:
            console.print("[red]No summary found in your resume. Please add a summary first.[/red]")
            return config
            
        console.print("\n[bold]Current Summary:[/bold]")
        console.print(config['summary'])
        
        prompt = (
            "As a professional resume writer, enhance this summary to be more impactful and engaging "
            "while maintaining its core message. Focus on strong action verbs and quantifiable achievements. "
            f"Here's the current summary:\n\n{config['summary']}"
        )
        
        console.print("\n[bold]Generating enhanced summary...[/bold]")
        enhanced = bot.chat(prompt)
        
        console.print("\n[bold]Enhanced Summary:[/bold]")
        console.print(enhanced)
        
        if Confirm.ask("\nWould you like to use the enhanced summary?", default=True):
            config['summary'] = enhanced
            console.print("[green]✓ Summary updated successfully![/green]")
    
    elif choice == "2":
        if 'experience' not in config or not config['experience']:
            console.print("[red]No experience entries found in your resume. Please add work experience first.[/red]")
            return config
            
        for exp in config['experience']:
            console.print(f"\n[bold]Current highlights for {exp['company']} - {exp['position']}:[/bold]")
            for highlight in exp['highlights']:
                console.print(f"• {highlight}")
            
            prompt = (
                "As a professional resume writer, enhance these job highlights to be more impactful. "
                "Focus on quantifiable achievements, leadership, and specific skills. "
                "Format each highlight as a bullet point starting with a strong action verb. "
                f"Current position: {exp['position']}\n"
                f"Company: {exp['company']}\n"
                "Current highlights:\n" +
                "\n".join(f"• {h}" for h in exp['highlights'])
            )
            
            console.print("\n[bold]Generating enhanced highlights...[/bold]")
            enhanced = bot.chat(prompt)
            
            # Extract bullet points
            enhanced_points = [
                point.strip().lstrip('•-*').strip()
                for point in enhanced.split('\n')
                if point.strip() and not point.strip().startswith(('Here', 'Enhanced', 'Improved'))
            ]
            
            if enhanced_points:
                console.print("\n[bold]Enhanced highlights:[/bold]")
                for point in enhanced_points:
                    console.print(f"• {point}")
                
                if Confirm.ask(f"\nWould you like to use these enhanced highlights for {exp['company']}?", default=True):
                    exp['highlights'] = enhanced_points
                    console.print(f"[green]✓ Highlights updated for {exp['company']}![/green]")
    
    elif choice == "3":
        if 'skills' not in config:
            console.print("[red]No skills section found in your resume. Please add skills first.[/red]")
            return config
            
        console.print("\n[bold]Current Skills:[/bold]")
        for category, skills in config['skills'].items():
            console.print(f"\n{category}:")
            for skill in skills:
                console.print(f"• {skill}")
        
        prompt = (
            "As a professional resume writer, optimize and reorganize these skills. "
            "Group them into clear categories, prioritize the most relevant ones, "
            "and ensure they align with current industry standards. "
            "Return the result as a formatted list with categories and bullet points. "
            f"Current skills:\n{json.dumps(config['skills'], indent=2)}"
        )
        
        console.print("\n[bold]Optimizing skills...[/bold]")
        enhanced = bot.chat(prompt)
        
        # Parse the enhanced skills
        enhanced_skills = {}
        current_category = None
        
        for line in enhanced.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.endswith(':'):  # This is a category
                current_category = line[:-1].strip()
                enhanced_skills[current_category] = []
            elif line.startswith(('•', '-', '*')) and current_category:
                skill = line.lstrip('•-* ').strip()
                enhanced_skills[current_category].append(skill)
        
        if enhanced_skills:
            console.print("\n[bold]Enhanced Skills:[/bold]")
            for category, skills in enhanced_skills.items():
                console.print(f"\n{category}:")
                for skill in skills:
                    console.print(f"• {skill}")
            
            if Confirm.ask("\nWould you like to use these enhanced skills?", default=True):
                config['skills'] = enhanced_skills
                console.print("[green]✓ Skills updated successfully![/green]")
    
    elif choice == "4":
        prompt = (
            "As a professional resume writer, review this resume and provide specific, actionable improvements "
            "for each section. Focus on impact, clarity, and modern resume best practices. "
            "Format your response with clear section headers and bullet points. "
            f"Resume content:\n{json.dumps(config, indent=2)}"
        )
        
        console.print("\n[bold]Analyzing resume...[/bold]")
        suggestions = bot.chat(prompt)
        
        console.print("\n[bold]AI Suggestions:[/bold]")
        console.print(suggestions)
        
        if Confirm.ask("\nWould you like me to automatically apply these suggestions?", default=True):
            sections = parse_ai_suggestions(suggestions)
            config, changes = apply_ai_suggestions(config, sections)
            
            if changes:
                console.print("\n[bold green]Changes Applied:[/bold green]")
                for change in changes:
                    console.print(f"✓ {change}")
            else:
                console.print("[yellow]No changes were necessary based on the suggestions.[/yellow]")
    
    return config

def clean_template_html(html_content):
    """Clean template HTML by removing markdown and code block wrappers."""
    # Remove markdown code block syntax
    html_content = re.sub(r'```html\s*', '', html_content)
    html_content = re.sub(r'\s*```', '', html_content)
    
    # Remove any "Here's a..." introductory text
    html_content = re.sub(r'^.*?<!DOCTYPE', '<!DOCTYPE', html_content, flags=re.DOTALL)
    
    # Remove any trailing explanation text
    html_content = re.sub(r'</html>.*$', '</html>', html_content, flags=re.DOTALL)
    
    return html_content.strip()

def generate_ai_template(style_description):
    """Generate a custom HTML template using AI."""
    prompt = f"""Create a modern, professional HTML template for a resume with the following style: {style_description}
    The template should:
    1. Use modern CSS with Flexbox/Grid
    2. Be responsive
    3. Include print-friendly styles
    4. Use professional fonts and colors
    5. Support all standard resume sections
    
    Return ONLY the complete HTML template with embedded CSS. The template should use Jinja2 templating syntax for dynamic content.
    Include placeholders for: name, contact info, summary, experience (company, position, dates, highlights), education, skills, and volunteer work.
    """
    
    template_html = bot.chat(prompt)
    return template_html

def save_ai_template(template_name, template_html, force_upgrade=False):
    """Save AI generated template."""
    # Clean the template HTML
    template_html = clean_template_html(template_html)
    
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    # Save template
    template_path = os.path.join('templates', f'{template_name}.html')
    
    if os.path.exists(template_path) and not force_upgrade:
        raise FileExistsError(f"Template '{template_name}' already exists")
    
    with open(template_path, 'w') as f:
        f.write(template_html)
    
    return template_path

def get_available_templates():
    """Get all available templates including both built-in and AI-generated ones."""
    template_dir = os.path.join(os.getcwd(), 'templates')
    templates = [f[:-5] for f in os.listdir(template_dir) if f.endswith('.html')]
    
    # Define built-in templates with descriptions
    built_in_templates = {
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
    
    # Add any AI-generated templates
    ai_templates = [t for t in templates if t not in built_in_templates]
    for t in ai_templates:
        built_in_templates[t] = 'AI-generated custom template'
    
    return built_in_templates

def select_template():
    """Select and configure template"""
    template_options = get_available_templates()
    
    console.print("\n[bold blue]Template Selection[/bold blue]")
    console.print("\nAvailable Templates:")
    
    # Create a table to display templates
    table = Table(show_header=True)
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Type", style="yellow")
    
    for name, description in template_options.items():
        template_type = "AI-Generated" if description == 'AI-generated custom template' else "Built-in"
        table.add_row(name, description, template_type)
    
    console.print(table)
    
    template_name = Prompt.ask(
        "\nSelect template",
        choices=list(template_options.keys()),
        default="professional"
    )
    
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
            'primary': '#2f3640',
            'secondary': '#c5a47e',
            'text': '#2f3640'
        },
        'medical': {
            'primary': '#005f73',
            'secondary': '#0a9396',
            'text': '#001219'
        },
        'elegant': {
            'primary': '#1b1b1b',
            'secondary': '#7c7c7c',
            'text': '#1b1b1b'
        },
        'compact': {
            'primary': '#34495e',
            'secondary': '#16a085',
            'text': '#2c3e50'
        },
        'contemporary': {
            'primary': '#4834d4',
            'secondary': '#686de0',
            'text': '#130f40'
        },
        'traditional': {
            'primary': '#2c3e50',
            'secondary': '#95a5a6',
            'text': '#2c3e50'
        }
    }
    
    # Font combinations based on template
    font_options = {
        'modern': {
            'main': 'Roboto',
            'heading': 'Roboto'
        },
        'minimal': {
            'main': 'Arial',
            'heading': 'Arial'
        },
        'professional': {
            'main': 'Georgia',
            'heading': 'Georgia'
        },
        'creative': {
            'main': 'Montserrat',
            'heading': 'Montserrat'
        },
        'executive': {
            'main': 'Cormorant Garamond',
            'heading': 'Cormorant Garamond'
        },
        'medical': {
            'main': 'Source Sans Pro',
            'heading': 'Source Sans Pro'
        },
        'elegant': {
            'main': 'Playfair Display',
            'heading': 'Playfair Display'
        },
        'compact': {
            'main': 'Open Sans',
            'heading': 'Open Sans'
        },
        'contemporary': {
            'main': 'Poppins',
            'heading': 'Poppins'
        },
        'traditional': {
            'main': 'Times New Roman',
            'heading': 'Times New Roman'
        }
    }
    
    # For AI-generated templates, create a default font combination
    if template_name not in font_options:
        font_options[template_name] = {
            'main': 'Arial',
            'heading': 'Arial'
        }
    
    template = {
        'name': template_name,
        'colors': color_schemes[template_name].copy(),
        'font': font_options[template_name].copy()
    }
    
    if Confirm.ask("\nWould you like to customize the colors?", default=False):
        template['colors']['primary'] = Prompt.ask(
            "Primary Color (hex code)",
            default=template['colors']['primary']
        )
        template['colors']['secondary'] = Prompt.ask(
            "Secondary Color (hex code)",
            default=template['colors']['secondary']
        )
        template['colors']['text'] = Prompt.ask(
            "Text Color (hex code)",
            default=template['colors']['text']
        )
    
    if Confirm.ask("\nWould you like to customize the fonts?", default=False):
        template['font']['main'] = Prompt.ask(
            "Main Font",
            default=template['font']['main']
        )
        template['font']['heading'] = Prompt.ask(
            "Heading Font",
            default=template['font']['heading']
        )
    
    return template

def template_management():
    """Manage resume templates."""
    console.print(Panel.fit("🎨 Template Management", style="bold blue"))
    
    options = [
        "View Available Templates",
        "Generate New AI Template",
        "Preview Template",
        "Customize Colors",
        "Customize Fonts",
        "Back to Main Menu"
    ]
    
    table = Table(title="Template Options", show_header=True)
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="green")
    
    for i, option in enumerate(options, 1):
        table.add_row(str(i), option)
    
    console.print(table)
    
    choice = Prompt.ask("Select an option", choices=[str(i) for i in range(1, len(options) + 1)])
    
    if choice == "1":
        # View available templates
        template_dir = os.path.join(os.getcwd(), 'templates')
        templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        
        table = Table(title="Available Templates")
        table.add_column("Template Name", style="cyan")
        table.add_column("Last Modified", style="green")
        table.add_column("Type", style="yellow")
        
        built_in_templates = get_available_templates()
        
        for template in templates:
            path = os.path.join(template_dir, template)
            modified_timestamp = os.path.getmtime(path)
            modified_date = datetime.fromtimestamp(modified_timestamp)
            modified = modified_date.strftime('%Y-%m-%d %H:%M')
            
            template_name = template[:-5]  # Remove .html extension
            template_type = "Built-in" if template_name in built_in_templates else "AI-Generated"
            
            table.add_row(template_name, modified, template_type)
        
        console.print(table)
    
    elif choice == "2":
        # Generate new AI template
        console.print("\n[bold]Generate New AI Template[/bold]")
        
        # Ask for template name first
        while True:
            template_name = Prompt.ask("Enter a name for your template")
            template_path = os.path.join(os.getcwd(), 'templates', f'{template_name}.html')
            
            if os.path.exists(template_path):
                if Confirm.ask(
                    f"\n[yellow]Template '{template_name}' already exists.[/yellow]\nWould you like to upgrade it?",
                    default=False
                ):
                    break
            else:
                break
        
        # Choose style
        console.print("\nChoose a style or describe your own:")
        style_options = [
            "Modern Minimalist",
            "Creative Professional",
            "Executive Classic",
            "Tech-Focused",
            "Healthcare Professional",
            "Custom Style"
        ]
        
        for i, style in enumerate(style_options, 1):
            console.print(f"{i}. {style}")
        
        style_choice = Prompt.ask(
            "Select a style",
            choices=[str(i) for i in range(1, len(style_options) + 1)]
        )
        
        if style_choice == str(len(style_options)):  # Custom Style
            style_description = Prompt.ask("Describe your desired template style")
        else:
            style_description = style_options[int(style_choice) - 1]
            
            # Add specific details for each pre-defined style
            style_details = {
                "Modern Minimalist": "Clean and minimal design with plenty of white space, subtle borders, and modern typography.",
                "Creative Professional": "Bold design with creative layout, accent colors, and unique section separators.",
                "Executive Classic": "Sophisticated design with traditional layout, serif fonts, and professional color scheme.",
                "Tech-Focused": "Modern design with code-like elements, monospace fonts for technical details, and tech-inspired accents.",
                "Healthcare Professional": "Clean and professional design with medical-themed colors, clear typography, and organized sections."
            }
            
            style_description = style_details.get(style_description, style_description)
        
        console.print(f"\n[bold]Generating template for style:[/bold] {style_description}")
        
        while True:
            # Generate the template
            template_html = generate_ai_template(style_description)
            
            try:
                # Save the template
                template_path = save_ai_template(template_name, template_html, force_upgrade=True)
                console.print(f"\n[green]✓ Template {'upgraded' if os.path.exists(template_path) else 'saved'} as:[/green] {template_path}")
                
                # Preview option
                if Confirm.ask("\nWould you like to preview this template?", default=True):
                    preview_template(template_path)
                
                # Ask if changes are needed
                if Confirm.ask("\nWould you like to make any changes to the template?", default=False):
                    console.print("\nWhat would you like to change?")
                    changes = Prompt.ask("Describe the changes you want")
                    style_description = f"{style_description}\n\nPlease make the following changes: {changes}"
                    console.print("\n[bold]Regenerating template with changes...[/bold]")
                    continue
                
                break
                
            except Exception as e:
                console.print(f"[red]Error saving template: {str(e)}[/red]")
                if not Confirm.ask("\nWould you like to try again?", default=True):
                    break
    
    elif choice == "3":
        # Preview template
        template_dir = os.path.join(os.getcwd(), 'templates')
        templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        
        if not templates:
            console.print("[yellow]No templates available. Generate one first![/yellow]")
            return choice
        
        table = Table(title="Available Templates")
        table.add_column("Number", style="cyan", width=4)
        table.add_column("Template Name", style="green")
        table.add_column("Type", style="yellow")
        
        built_in_templates = get_available_templates()
        
        for i, template in enumerate(templates, 1):
            template_name = template[:-5]  # Remove .html extension
            template_type = "Built-in" if template_name in built_in_templates else "AI-Generated"
            table.add_row(str(i), template_name, template_type)
        
        console.print(table)
        
        template_choice = Prompt.ask(
            "Select a template to preview",
            choices=[str(i) for i in range(1, len(templates) + 1)]
        )
        
        template_path = os.path.join(template_dir, templates[int(template_choice) - 1])
        preview_template(template_path)
    
    elif choice in ["4", "5"]:
        # Customize colors or fonts
        console.print("[yellow]This feature will be implemented soon![/yellow]")
    
    return choice

def preview_template(template_path):
    """Generate a preview of the template with sample data."""
    sample_data = {
        "name": "John Doe",
        "contact": {
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "location": "New York, NY"
        },
        "summary": "Experienced professional with expertise in...",
        "experience": [
            {
                "company": "Sample Corp",
                "position": "Senior Role",
                "start_date": "2020",
                "end_date": "Present",
                "highlights": ["Achievement 1", "Achievement 2"]
            }
        ],
        "education": [
            {
                "institution": "Sample University",
                "degree": "Bachelor's Degree",
                "field": "Computer Science",
                "graduation_date": "2019"
            }
        ],
        "skills": {
            "technical": ["Skill 1", "Skill 2"],
            "soft": ["Leadership", "Communication"]
        }
    }
    
    # Load and render template
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    preview_html = template.render(**sample_data)
    
    # Clean the rendered HTML
    preview_html = clean_template_html(preview_html)
    
    # Save preview
    preview_path = os.path.join(os.getcwd(), 'preview.html')
    with open(preview_path, 'w') as f:
        f.write(preview_html)
    
    # Open in browser
    webbrowser.open(f'file://{preview_path}')
    console.print(f"\n[green]✓ Preview saved to:[/green] {preview_path}")

def get_or_update_config(config_path, web_mode=False):
    """Get or update resume configuration"""
    config = {}
    config_tool = InteractiveConfig()
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if Confirm.ask("\nWould you like to select a different template?", default=True):
            config = config_tool.run(config_path, config, web_mode)
        elif Confirm.ask("\nWould you like to update your resume details?", default=True):
            config = config_tool.run(config_path, config, web_mode)
    else:
        console.print("\n[yellow]No configuration found. Let's create one![/yellow]")
        config = config_tool.run(config_path, web_mode=web_mode)
    
    return config

def save_config(config_path, config):
    """Save the resume configuration."""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def generate_resume_output(config_path, output_path):
    """Generate resume output with template selection."""
    if not os.path.exists(config_path):
        console.print("[red]No configuration found. Please create a resume first.[/red]")
        return
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # Template Selection
    template_options = get_available_templates()
    
    console.print("\n[bold blue]Template Selection[/bold blue]")
    
    # Create a table to display templates
    table = Table(show_header=True)
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Type", style="yellow")
    
    for name, description in template_options.items():
        template_type = "AI-Generated" if description == 'AI-generated custom template' else "Built-in"
        table.add_row(name, description, template_type)
    
    console.print(table)
    
    template_name = Prompt.ask(
        "\nSelect template",
        choices=list(template_options.keys()),
        default="professional"
    )
    
    # Color schemes and fonts
    color_schemes = {
        'modern': {'primary': '#2c3e50', 'secondary': '#3498db', 'text': '#333333'},
        'minimal': {'primary': '#000000', 'secondary': '#666666', 'text': '#333333'},
        'professional': {'primary': '#1a4367', 'secondary': '#2c88d9', 'text': '#2c3e50'},
        'creative': {'primary': '#2c3e50', 'secondary': '#e74c3c', 'text': '#2c3e50'},
        'executive': {'primary': '#2f3640', 'secondary': '#c5a47e', 'text': '#2f3640'},
        'medical': {'primary': '#005f73', 'secondary': '#0a9396', 'text': '#001219'},
        'elegant': {'primary': '#1b1b1b', 'secondary': '#7c7c7c', 'text': '#1b1b1b'},
        'compact': {'primary': '#34495e', 'secondary': '#16a085', 'text': '#2c3e50'},
        'contemporary': {'primary': '#4834d4', 'secondary': '#686de0', 'text': '#130f40'},
        'traditional': {'primary': '#2c3e50', 'secondary': '#95a5a6', 'text': '#2c3e50'}
    }
    
    font_options = {
        'modern': {'main': 'Roboto', 'heading': 'Roboto'},
        'minimal': {'main': 'Arial', 'heading': 'Arial'},
        'professional': {'main': 'Georgia', 'heading': 'Georgia'},
        'creative': {'main': 'Montserrat', 'heading': 'Montserrat'},
        'executive': {'main': 'Cormorant Garamond', 'heading': 'Cormorant Garamond'},
        'medical': {'main': 'Source Sans Pro', 'heading': 'Source Sans Pro'},
        'elegant': {'main': 'Playfair Display', 'heading': 'Playfair Display'},
        'compact': {'main': 'Open Sans', 'heading': 'Open Sans'},
        'contemporary': {'main': 'Poppins', 'heading': 'Poppins'},
        'traditional': {'main': 'Times New Roman', 'heading': 'Times New Roman'}
    }
    
    # For AI-generated templates, use default styles
    if template_name not in color_schemes:
        color_schemes[template_name] = {'primary': '#2c3e50', 'secondary': '#3498db', 'text': '#333333'}
    if template_name not in font_options:
        font_options[template_name] = {'main': 'Arial', 'heading': 'Arial'}
    
    # Allow customization
    if Confirm.ask("\nWould you like to customize the colors?", default=False):
        color_schemes[template_name]['primary'] = Prompt.ask("Primary Color (hex code)", default=color_schemes[template_name]['primary'])
        color_schemes[template_name]['secondary'] = Prompt.ask("Secondary Color (hex code)", default=color_schemes[template_name]['secondary'])
        color_schemes[template_name]['text'] = Prompt.ask("Text Color (hex code)", default=color_schemes[template_name]['text'])
    
    if Confirm.ask("\nWould you like to customize the fonts?", default=False):
        font_options[template_name]['main'] = Prompt.ask("Main Font", default=font_options[template_name]['main'])
        font_options[template_name]['heading'] = Prompt.ask("Heading Font", default=font_options[template_name]['heading'])
    
    # Update config with template settings
    config_data['template'] = {
        'name': template_name,
        'colors': color_schemes[template_name],
        'font': font_options[template_name]
    }
    
    try:
        # Generate resume
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(f'{template_name}.html')
        
        # Render template
        html_content = template.render(**config_data)
        
        # Clean the rendered HTML
        html_content = clean_template_html(html_content)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Save HTML version
        html_path = os.path.join(output_path, 'resume.html')
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Generate PDF
        pdf_path = os.path.join(output_path, 'resume.pdf')
        HTML(string=html_content).write_pdf(pdf_path)
        
        console.print("\n✨ Generated resume:")
        console.print(f"PDF: {pdf_path}")
        console.print(f"HTML: {html_path}")
        
        # Preview option
        if Confirm.ask("\nWould you like to preview the generated resume?", default=True):
            webbrowser.open(f'file://{html_path}')
            
    except Exception as e:
        console.print(f"[red]Error generating resume: {str(e)}[/red]")
        if "template not found" in str(e).lower():
            console.print("[yellow]Tip: Make sure the template file exists in the templates directory.[/yellow]")

@click.command()
@click.option('--config', default='config/resume_config.json', help='Path to config file')
@click.option('--output', default='output', help='Output directory')
@click.option('--web', is_flag=True, help='Generate web version')
def main(config, output, web):
    """Interactive resume generator with AI assistance."""
    config_path = os.path.join(os.getcwd(), config)
    output_path = os.path.join(os.getcwd(), output)
    
    while True:
        display_menu()
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            # Create/Update Resume
            config_data = get_or_update_config(config_path, web)
            save_config(config_path, config_data)
            console.print("[green]Resume configuration updated successfully![/green]")
        
        elif choice == "2":
            # Generate Output
            generate_resume_output(config_path, output_path)
        
        elif choice == "3":
            # AI Enhancement
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                config_data = ai_enhance_resume(config_data)
                save_config(config_path, config_data)
            else:
                console.print("[red]No configuration found. Please create a resume first.[/red]")
        
        elif choice == "4":
            # Template Management
            template_choice = template_management()
            if template_choice != "6":  # Not "Back to Main Menu"
                console.print("[yellow]Template updated![/yellow]")
        
        elif choice == "5":
            # Ask AI Assistant
            question = Prompt.ask("\nWhat would you like to ask the AI assistant about your resume?")
            response = bot.chat(question)
            console.print("\n[bold]AI Assistant:[/bold]")
            console.print(response)
        
        elif choice == "6":
            # Exit
            console.print("[yellow]Thank you for using Resume Generator![/yellow]")
            break

if __name__ == '__main__':
    main()