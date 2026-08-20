# CrewAI Crash Course

A small multi-agent CrewAI project that researches a technical topic using YouTube channel content and writes a blog article in markdown.

## What this project does

- Uses a research agent to gather topic context
- Uses a writing agent to turn the research into a polished article
- Uses a YouTube channel search tool to look for relevant educational content
- Writes the final article to `new-blog-post.md`

## Project structure

- `agents.py` - defines the research and writing agents
- `tasks.py` - defines the research task and final writing task
- `tools.py` - contains the YouTube tool and fallback behavior
- `crew.py` - starts the CrewAI workflow
- `.env` - environment variables for OpenAI configuration
- `new-blog-post.md` - generated article output

## Requirements

- Python 3.10+
- A virtual environment
- An OpenAI API key

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-4o-mini
```

## Run the project

Run the project using the project venv, not the base Python:

```powershell
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python crew.py
```

This keeps Windows terminal output stable and avoids `charmap` encoding noise.

## YouTube tool behavior

The `crewai_tools` YouTube channel search relies on `pytube` under the hood. In some environments, the upstream `pytube` channel parsing fails against newer YouTube page layouts.

This project includes a resilient fallback mechanism and a compatibility patch that maps `pytubefix` to `pytube` before the tool is created, so the real YouTube content search can work more reliably in this environment.

## Troubleshooting

### `ModuleNotFoundError: No module named 'crewai'`

Use the project venv Python instead of the system/base Python:

```powershell
.\.venv\Scripts\python crew.py
```

### `charmap` encoding errors on Windows

Set the console encoding before running:

```powershell
$env:PYTHONIOENCODING = "utf-8"
```

## Example output

The generated blog article is written to:

```text
new-blog-post.md
```

## Notes

This project is intended as a learning/demo project for CrewAI multi-agent orchestration and tool usage, not as a production-ready publishing pipeline.
