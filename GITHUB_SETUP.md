# GitHub Repository Setup Guide

## Repository Details

**Repository Name:** `chatgpt-mcp-hello-world`

**Description:**
```
Minimal ChatGPT MCP (Model Context Protocol) server with custom widget support. A lightweight starter template for building ChatGPT integrations without heavy frameworks.
```

**License:** MIT

**Topics/Tags:**
```
chatgpt, mcp, model-context-protocol, openai, chatgpt-plugin, widgets, nodejs, fastify, minimal, starter-template
```

---

## Step-by-Step GitHub Setup

### 1. Initialize Git Repository

```bash
cd chatgpt-mcp-app
git init
git add .
git commit -m "Initial commit: Minimal ChatGPT MCP server with HelloWorld widget"
```

### 2. Create GitHub Repository

**Option A: Using GitHub CLI (gh)**
```bash
gh repo create chatgpt-mcp-hello-world --public --source=. --remote=origin --push
gh repo edit --add-topic chatgpt --add-topic mcp --add-topic model-context-protocol --add-topic openai --add-topic nodejs --add-topic fastify
```

**Option B: Using GitHub Web Interface**
1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `chatgpt-mcp-hello-world`
   - **Description:** `Minimal ChatGPT MCP (Model Context Protocol) server with custom widget support. A lightweight starter template for building ChatGPT integrations without heavy frameworks.`
   - **Visibility:** Public (or Private)
   - **Initialize:** Leave unchecked (we already have files)
   - **License:** MIT License
3. Click "Create repository"

### 3. Connect Local Repo to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/chatgpt-mcp-hello-world.git
git branch -M main
git push -u origin main
```

### 4. Add Topics (if using web interface)

1. Go to your repository page
2. Click the gear icon ⚙️ next to "About"
3. Add topics: `chatgpt`, `mcp`, `model-context-protocol`, `openai`, `chatgpt-plugin`, `widgets`, `nodejs`, `fastify`, `minimal`, `starter-template`
4. Click "Save changes"

### 5. Update package.json

Replace `YOUR_USERNAME` in `package.json` with your actual GitHub username:

```bash
# macOS/Linux
sed -i '' 's/YOUR_USERNAME/your-actual-username/g' package.json

# Or manually edit package.json
```

### 6. Create a Release (Optional)

```bash
git tag -a v1.0.0 -m "Initial release: Minimal MCP server"
git push origin v1.0.0
```

---

## Repository Settings Recommendations

### Branch Protection (for main branch)
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging

### Security
- ✅ Enable Dependabot alerts
- ✅ Enable Dependabot security updates

### Features to Enable
- ✅ Issues
- ✅ Projects
- ✅ Wiki (optional)
- ✅ Discussions (optional)

---

## README Badges (Optional)

Add these to the top of your README.md:

```markdown
# ChatGPT MCP Hello World

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![MCP SDK](https://img.shields.io/badge/MCP%20SDK-1.19.1-blue)](https://modelcontextprotocol.io/)
```

---

## Quick Commands Reference

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/chatgpt-mcp-hello-world.git

# Install dependencies
cd chatgpt-mcp-hello-world
npm install

# Run the server
npm run dev

# Create a new branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

---

## Alternative Repository Names

If `chatgpt-mcp-hello-world` is taken, try:
- `mcp-chatgpt-starter`
- `chatgpt-widget-starter`
- `minimal-mcp-server`
- `simple-chatgpt-mcp`
- `mcp-server-template`
