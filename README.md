# Sue-Me: AI-Powered Resume Generator 🚀

A sophisticated Python-based tool designed to craft professional and creative resumes. Features AI-powered content enhancement and an interactive configuration wizard.

![License](https://img.shields.io/badge/license-Proprietary-red)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

## ✨ Features

- 🤖 **AI-powered content improvement**:
  - Enhanced job descriptions
  - Professional summary generation
  - Smart skill suggestions
  - Content optimization
- 📝 **Interactive resume configuration wizard**
- 🎨 **Multiple professional templates**
- 📄 **PDF export functionality**
- 🎯 **Customizable styling options**
- 🔒 **Secure configuration system**

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- API key for AI features (see Configuration)

### Installation

1. Clone this repository (private access only):
   ```bash
   git clone https://github.com/paylenn/sue-me.git
   cd sue-me
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## 🔒 Security

### API Keys and Sensitive Data
- Never commit your `.env` file
- Keep your API keys private
- Use environment variables for sensitive data
- The `.gitignore` file is configured to exclude sensitive files

### Data Privacy
- Resume data is stored locally in your config directory
- No data is sent to external servers except for AI processing
- Templates and outputs are saved in your local directories
- Sensitive information is not logged

## 📖 Usage

### Interactive Mode (Default)
```bash
python resume_generator.py
```

This launches the interactive configuration wizard that guides you through:
- Personal information
- Work experience
- Education
- Skills
- Template customization

### Non-Interactive Mode
```bash
python resume_generator.py --no-interactive
```

### AI Enhancement Options
```bash
python resume_generator.py --no-ai  # Disable AI features
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file with the following settings:
```bash
# Copy from .env.example and fill in your values
AI_API_KEY=your_api_key_here
AI_MODEL=your_model_here
DEBUG=False
```

## 📁 Project Structure
```
sue-me/
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # Documentation
├── requirements.txt     # Python dependencies
├── resume_generator.py  # Main application
├── ai_helper.py         # AI enhancement utilities
├── interactive_config.py # Configuration wizard
├── config/             # Configuration files
│   └── resume_config.json
├── templates/          # Resume templates
└── output/            # Generated resumes (empty, created on demand)
```

## 🔐 License and Usage Restrictions

This project is proprietary and confidential. Unauthorized copying, distribution, or use of this software is strictly prohibited. All rights reserved.

### Usage Restrictions
- Private use only
- No commercial use without permission
- No redistribution
- No derivative works

## 🆘 Support

For support, please contact the project maintainers directly. Do not create public issues or discussions about internal features.

## ⚠️ Security Notice

If you discover any security vulnerabilities, please report them privately to the project maintainers. Do not create public issues for security problems.

---
Created with ❤️ by [paylenn](https://github.com/paylenn)