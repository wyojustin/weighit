#!/bin/bash
# Create all missing documentation and configuration files for WeighIt

set -e
cd "$(dirname "$0")"

echo "======================================"
echo "Creating WeighIt Documentation Files"
echo "======================================"
echo ""

# Create .github/workflows directory
echo "Creating .github/workflows/..."
mkdir -p .github/workflows

# Create .github/workflows/test.yml
cat > .github/workflows/test.yml << 'EOF'
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.12']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
EOF
echo "✓ Created .github/workflows/test.yml"

# Create .streamlit directory
echo "Creating .streamlit/..."
mkdir -p .streamlit

# Create .streamlit/secrets.toml.example
cat > .streamlit/secrets.toml.example << 'EOF'
# Email Configuration for Reports
# Copy this file to .streamlit/secrets.toml and fill in your credentials
# DO NOT commit secrets.toml to git!

[email]
# SMTP server address (Gmail example shown)
smtp_server = "smtp.gmail.com"

# SMTP port (587 for TLS, 465 for SSL)
smtp_port = 587

# Your email address
sender_email = "your-email@gmail.com"

# Your email password or app-specific password
# For Gmail: Create an App Password at https://myaccount.google.com/apppasswords
sender_password = "your-app-password-here"

# Default recipient for reports
default_recipient = "recipient@example.com"
EOF
echo "✓ Created .streamlit/secrets.toml.example"

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core Dependencies
streamlit>=1.31.0
pillow>=10.0.0
hidapi>=0.14.0
click>=8.1.0

# Optional but recommended
pytest>=7.4.0
pytest-cov>=4.1.0
EOF
echo "✓ Created requirements.txt"

# Create .gitignore
cat > .gitignore << 'EOF'
# Database files
*.db
*.db-journal
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
venv/
.venv/
env/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/secrets.toml
.streamlit/credentials.toml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
Desktop.ini

# Pytest
.pytest_cache/
.coverage
htmlcov/
.tox/

# Jupyter Notebook
.ipynb_checkpoints

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Logs
*.log
logs/

# Backups
*.backup
*.bak
*.old

# Temporary files
tmp/
temp/
*.tmp
EOF
echo "✓ Created .gitignore"

# Create LICENSE
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 wyojustin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
echo "✓ Created LICENSE"

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="weighit",
    version="1.0.0",
    author="wyojustin",
    description="Food pantry scale system with temperature tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wyojustin/weighit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "streamlit>=1.31.0",
        "pillow>=10.0.0",
        "hidapi>=0.14.0",
        "click>=8.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "weigh=weigh.cli_weigh:main",
        ],
    },
    package_data={
        "weigh": [
            "schema.sql",
            "assets/*.png",
            "assets/*.css",
        ],
    },
    include_package_data=True,
)
EOF
echo "✓ Created setup.py"

echo ""
echo "======================================"
echo "Files Created Successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review the created files"
echo "2. Run: chmod +x install.sh"
echo "3. Copy README.md, CHANGELOG.md, and CONTRIBUTING.md from the artifacts"
echo "4. Run: git add ."
echo "5. Run: git commit -m 'docs: add project documentation and configuration'"
echo "6. Run: git push origin main"
echo ""
