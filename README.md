# Sue-Me: AI-Powered Resume Generator 🚀

A sophisticated Python-based tool designed to craft professional and creative resumes. Features intelligent content enhancement and an interactive configuration wizard.

![License](https://img.shields.io/badge/license-Proprietary-red)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

## ✨ Features

- 🤖 **Intelligent content improvement**:
  - Enhanced job descriptions
  - Professional summary generation
  - Smart skill suggestions
  - Content optimization
- 📝 **Interactive resume configuration wizard**
- 🎨 **Multiple professional templates**
- 📄 **PDF export functionality**
- 🎯 **Customizable styling options**
- 🔒 **Secure configuration system**

## 🎥 Demo
![Demo of Sue-Me in action](@demo_final.gif)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

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

## 🔒 Security

### Data Privacy
- Resume data is stored locally in your config directory
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

### Enhancement Options
```bash
python resume_generator.py --no-enhance  # Disable enhancement features
```

## 📁 Project Structure
```
sue-me/
├── .gitignore           # Git ignore rules
├── README.md            # Documentation
├── requirements.txt     # Python dependencies
├── resume_generator.py  # Main application
├── ai_helper.py         # Enhancement utilities
├── interactive_config.py # Configuration wizard
├── config/             # Configuration files
│   └── resume_config.json
├── templates/          # Resume templates
└── output/            # Generated resumes
```

## 🔐 License and Usage Restrictions

This project is proprietary and confidential. Unauthorized copying, distribution, or use of this software is strictly prohibited. All rights reserved. lol jk

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