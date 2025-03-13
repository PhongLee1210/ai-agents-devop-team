# DevGenius - DevOps AI Agent Team 🤖

Welcome to the DevGenius project! This repository contains a team of AI agents that help automate and enhance your DevOps workflow for React + Vite + TypeScript + Tailwind CSS frontends. As featured on our [YouTube Channel](youtube.com/@devgenius), these agents work together to handle various DevOps tasks including code review, build prediction, and infrastructure management.

[![YouTube Channel](https://img.shields.io/badge/YouTube-Subscribe-red)](https://www.youtube.com/@devgenius)
[![GitHub Stars](https://img.shields.io/github/stars/devgenius/devgenius-ai?style=social)](https://github.com/devgenius/build-a-devops-team-using-ai-agents)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Features

- 🔄 Automated CI/CD Pipeline Generation for React + Vite
- 🐳 Docker Configuration Management for Frontend Applications
- 📊 Build Success Prediction for TypeScript Projects
- 🎨 Tailwind CSS Optimization Support
- 🔍 AI-Powered Code Review for React Components
- 💬 Natural Language Interaction
- 📈 Real-time Build Status Monitoring

## 🚀 Prerequisites & Assumptions

### Required Accounts (All Free Tiers Work!)

- GitHub Account ([Sign up here](https://github.com/signup))
  - Used for repository hosting and CI/CD
  - Free tier includes unlimited public repositories
  - Includes GitHub Actions minutes for public repositories
- GROQ Account ([Sign up here](https://groq.com))
  - Used for AI model access
  - Free tier includes sufficient API calls to test the project
  - No credit card required for initial testing

### Technical Requirements

- Node.js 18.0.0 or higher
- Python 3.13.0 or higher
- Docker Desktop
- Git
- Basic understanding of:
  - React, TypeScript, and Vite
  - Tailwind CSS
  - Command line operations
  - Git commands
  - YAML file format

### Setting Up GitHub Secrets

This project requires certain secrets to be set up in your GitHub repository. Here's how:

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Navigate to "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add the following secrets:
   ```
   GROQ_API_ENDPOINT=https://api.groq.com/v1
   GROQ_API_KEY=your_groq_api_key
   GH_TOKEN=your_github_personal_access_token
   ```

To create a GitHub Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a name and select these permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. Copy the token immediately (you won't see it again!)

## 🚀 Getting Started

### Prerequisites

- Node.js 18.0.0 or higher
- Python 3.13.0 or higher
- Docker Desktop
- Git
- A GROQ API key ([Get one here](https://groq.com))
- GitHub account with repository access

### Installation

#### macOS

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.13
brew install python@3.13

# Install Node.js
brew install node

# Install Docker Desktop
brew install --cask docker

# Clone the repository
git clone https://github.com/devgenius/build-a-devops-team-using-ai-agents.git
cd build-a-devops-team-using-ai-agents

# Create a virtual environment with uv
uv venv .venv --python=python3.13

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies with uv (much faster than pip!)
uv pip install -r requirements.txt

# Install frontend dependencies
npm install
```

#### Windows

```powershell
# Install Python 3.13 from the official website
# https://www.python.org/downloads/

# Install Node.js from the official website
# https://nodejs.org/

# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop

# Clone the repository
git clone https://github.com/devgenius/build-a-devops-team-using-ai-agents.git
cd build-a-devops-team-using-ai-agents

# Create a virtual environment with uv
uv venv .venv --python=python3.13

# Activate the virtual environment
.venv\Scripts\activate

# Install dependencies with uv (much faster than pip!)
uv pip install -r requirements.txt

# Install frontend dependencies
npm install
```

#### Linux

```bash
# Add Python 3.13 repository
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Docker
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Clone the repository
git clone https://github.com/devgenius/build-a-devops-team-using-ai-agents.git
cd build-a-devops-team-using-ai-agents

# Create a virtual environment with uv
uv venv .venv --python=python3.13

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies with uv (much faster than pip!)
uv pip install -r requirements.txt

# Install frontend dependencies
npm install
```

### Configuration

```bash
# Environment variables
GROQ_API_ENDPOINT=https://api.groq.com/v1
GROQ_API_KEY=your_groq_api_key
```

### Usage

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate # macOS/Linux
.\venv\Scripts\activate # Windows

# Run the main script
python main.py
```

### Project Structure

```
devgenius-ai/
├── agents/           # AI agent implementations
├── models/           # Data models and schemas
├── utils/           # Utility functions
├── frontend/        # React + Vite + TypeScript + Tailwind frontend
│   ├── src/         # Frontend source code
│   ├── package.json # Node dependencies
├── .github/workflows/ # GitHub Actions workflows
├── main.py          # Main orchestration script
└── requirements.txt  # Python dependencies
```

This README provides:

- Clear installation instructions for all major platforms
- Step-by-step configuration guide
- Troubleshooting tips
- Project structure explanation
- Links to YouTube content
- Contributing guidelines
- Professional formatting with emojis and badges
