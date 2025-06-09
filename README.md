# GitGen CommandLine Tool

**Translate natural language into git commands and execute them seamlessly.**

## Overview

`GitGen` is a Python-based command-line interface (CLI) tool that leverages a large language model (LLM) to convert natural-language intents into sequential git commands, execute them, and handle errors automatically by querying the LLM for fixes.

---

## Features

* **Natural Language Intent**: Describe what you want (`"push my code"`, `"create a new branch called feature"`), and GitGen generates the corresponding git commands.
* **Interactive Prompts**: For operations requiring user input (e.g., commit messages), GitGen will prompt you seamlessly.
* **Dry-Run Mode**: Preview the commands without executing them.
* **Error Recovery**: On command failure, GitGen captures the stderr output and asks the LLM for a single-line fix, then retries.
* **Cross-Platform**: Runs on macOS, Linux, and Windows (via WSL or compatible shells).

---

## Prerequisites

* Python 3.8+
* Git
* OpenAI API key
* [Conda](https://docs.conda.io/) (optional but recommended for isolated environments)

---

## Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/<YOUR_USERNAME>/GitGen-CommandLine-Tool.git
   cd GitGen-CommandLine-Tool
   ```

2. **(Optional) Create a Conda environment**

   ```bash
   conda create -n gitgen-commandline-tool python=3.10 -y
   conda activate gitgen-commandline-tool
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Make the CLI executable**

   ```bash
   chmod +x gitgen.py
   ```

---

## Usage

### Basic Intent

```bash
./gitgen.py "add all changes and commit with message 'initial import'"
```

GitGen will:

1. Ask for any needed input (e.g., commit message)
2. Run `git add .`
3. Run `git commit -m "initial import"`
4. Confirm completion

### Dry-Run Mode

Preview generated steps without executing:

```bash
./gitgen.py "push my code" --dry-run
```

### Error Handling

If a command fails, GitGen captures the error and asks the LLM for a one-line fix. For example:

```
$ git push origin main
Error: non-fast-forward
🤖 Asking for fix...
$ git pull --rebase origin main
$ git push origin main
✅ Done!
```

---

## Configuration

Set your OpenAI API key in your shell environment:

```bash
export OPENAI_API_KEY="sk-..."
```
