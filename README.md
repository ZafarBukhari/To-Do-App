# To-Do CLI Application

A production-ready, cross-platform To-Do CLI application that is fast, reliable, and script-friendly.

## Features

- **Core Task Management**
  - Add, list, edit, delete tasks
  - Mark tasks as completed/incomplete
  - Undo last destructive action

- **Task Attributes**
  - Unique numeric ID
  - Title/description
  - Status (pending/completed)
  - Priority (low, medium, high)
  - Multiple tags
  - Optional project/group name
  - Creation timestamp
  - Optional due date
  - Automatic overdue detection

- **CLI UX**
  - Short, intuitive commands
  - Command aliases for convenience
  - Colorized output (green=done, yellow=pending, red=overdue)
  - Formatted table display
  - Summary statistics
  - `--help` for all commands with examples

- **Additional Features**
  - Search and filter by keyword, tag, project, status
  - Sort by priority, due date, creation time, title
  - Persistent storage with JSON files
  - Automatic backups (last 10 versions)
  - User configuration via `~/.todo/config.toml`

## Installation

### Prerequisites
- Python 3.9 or higher

### Install from Source

```bash
# Clone or download repository
cd "TO-DO App"

# Install in development mode
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Getting Started

### Initialize

```bash
todo init
```

This creates the data directory at `~/.todo/` with:
- `tasks.json` - Your tasks
- `config.toml` - Configuration
- `undo_history.json` - Undo history

### Basic Usage

```bash
# Add a task
python -m todo_cli.main add "Pay electricity bill" --due 2026-01-10 --priority high --tag finance,urgent

# List all tasks
python -m todo_cli.main list

# Mark task as completed
python -m todo_cli.main done 1

# Mark task as incomplete
python -m todo_cli.main undo 1

# Edit a task
python -m todo_cli.main edit 1 --title "New title" --priority medium

# Delete a task
python -m todo_cli.main delete 1

# Search tasks
python -m todo_cli.main search "keyword"
```

## Commands

### Add Task

Create a new task with optional attributes.

```bash
python -m todo_cli.main add "Task title" [OPTIONS]
```

**Aliases:** `new`, `create`

**Options:**
- `--priority`, `-p`: Priority level (low, medium, high) [default: medium]
- `--tag`, `-t`: Task tags (comma-separated)
- `--project`: Project/group name
- `--due`, `-d`: Due date (YYYY-MM-DD, MM-DD, today, tomorrow, +N)

**Examples:**
```bash
# Simple task
python -m todo_cli.main add "Buy groceries"

# Task with priority and tags
python -m todo_cli.main add "Submit report" --priority high --tag work,urgent

# Task with due date
python -m todo_cli.main add "Pay rent" --due 2026-01-15

# Task with project
python -m todo_cli.main add "Fix bug #123" --project "Project Alpha"

# Complex task
python -m todo_cli.main add "Prepare presentation" --due tomorrow --priority high --tag work,meeting --project Q1-Goals
```

### List Tasks

Display tasks with optional filtering and sorting.

```bash
python -m todo_cli.main list [OPTIONS]
```

**Aliases:** `ls`

**Options:**
- `--all`, `-a`: Show all tasks
- `--pending`, `-p`: Show pending tasks only
- `--completed`, `-c`: Show completed tasks only
- `--tag`: Filter by tag
- `--project`: Filter by project
- `--overdue`: Show only overdue tasks
- `--sort`: Sort by field (priority, due_date, created_at, title) [default: priority]
- `--reverse`, `-r`: Reverse sort order

**Examples:**
```bash
# List all tasks
python -m todo_cli.main list

# List pending tasks only
python -m todo_cli.main list --pending
python -m todo_cli.main list -p

# List completed tasks only
python -m todo_cli.main list --completed
python -m todo_cli.main list -c

# Filter by tag
python -m todo_cli.main list --tag finance
python -m todo_cli.main list --tag work

# Filter by project
python -m todo_cli.main list --project "Q1-Goals"

# Show overdue tasks
python -m todo_cli.main list --overdue

# Sort by due date
python -m todo_cli.main list --sort due_date

# Multiple filters
python -m todo_cli.main list --tag work --pending --sort priority
```

### Edit Task

Modify an existing task.

```bash
python -m todo_cli.main edit <task_id> [OPTIONS]
```

**Aliases:** `modify`, `update`

**Options:**
- `--title`: New task title
- `--priority`: New priority (low, medium, high)
- `--tag`, `-t`: Add/replace tags (comma-separated)
- `--project`: Project name
- `--due`: Due date (YYYY-MM-DD, MM-DD, today, tomorrow, +N)

**Examples:**
```bash
# Update title
python -m todo_cli.main edit 1 --title "Updated title"

# Change priority
python -m todo_cli.main edit 1 --priority high

# Add tags
python -m todo_cli.main edit 1 --tag urgent,review

# Update due date
python -m todo_cli.main edit 1 --due tomorrow

# Multiple updates
python -m todo_cli.main edit 1 --title "New title" --priority medium --project "New Project"
```

### Mark Completed

Mark a task as completed.

```bash
python -m todo_cli.main done <task_id>
```

**Aliases:** `complete`, `finish`, `check`

**Examples:**
```bash
python -m todo_cli.main done 1
python -m todo_cli.main complete 5
python -m todo_cli.main finish 10
```

### Mark Incomplete (Undo)

Mark a task as incomplete (undo completion).

```bash
python -m todo_cli.main undo <task_id>
```

**Aliases:** `reopen`, `uncomplete`

**Examples:**
```bash
python -m todo_cli.main undo 1
python -m todo_cli.main reopen 5
python -m todo_cli.main uncomplete 10
```

### Delete Task

Delete a task from the list.

```bash
python -m todo_cli.main delete <task_id> [OPTIONS]
```

**Aliases:** `rm`, `remove`

**Options:**
- `--yes`, `-y`: Skip confirmation prompt

**Examples:**
```bash
# Delete with confirmation
python -m todo_cli.main delete 5

# Delete without confirmation
python -m todo_cli.main delete 5 --yes
python -m todo_cli.main rm 5 -y

# Using alias
python -m todo_cli.main remove 10
```

### Search Tasks

Search for tasks by keyword or filter criteria.

```bash
python -m todo_cli.main search [keyword] [OPTIONS]
```

**Aliases:** `find`

**Options:**
- `--tag`: Filter by tag
- `--project`: Filter by project

**Examples:**
```bash
# Search by keyword
python -m todo_cli.main search "electricity"
python -m todo_cli.main find "report"

# Filter by tag
python -m todo_cli.main search --tag finance
python -m todo_cli.main search --tag work

# Filter by project
python -m todo_cli.main search --project "Q1-Goals"

# Combine keyword and filters
python -m todo_cli.main search "meeting" --tag work --project "Q1"
```

### Undo Last Action

Undo the last destructive action (delete, edit, complete).

```bash
todo undo-last
```

**Examples:**
```bash
todo undo-last
```

### Configuration

Set or view configuration values.

```bash
# View current configuration
todo config

# Set configuration value
todo config set <key> <value>
```

**Configuration Keys:**
- `default_priority`: Default priority for new tasks (low, medium, high)
- `color_enabled`: Enable/disable color output (true/false)
- `date_format`: Date display format (default: %Y-%m-%d)
- `editor`: Default text editor (defaults to $EDITOR)
- `sort_by`: Default sort field (priority, due_date, created_at, title)

**Examples:**
```bash
# View configuration
todo config

# Set default priority
todo config set default_priority high

# Disable colors
todo config set color_enabled false

# Set custom editor
todo config set editor vim

# Change date format
todo config set date_format "%d/%m/%Y"
```

### Initialize

Initialize the To-Do application (create data directory).

```bash
todo init
```

This command creates necessary files and directories if they don't exist.

## Configuration File

Configuration is stored at `~/.todo/config.toml`:

```toml
[data_dir]
path = "~/.todo"

[defaults]
priority = "medium"
tags = []
show_completed = true

[display]
color_enabled = true
date_format = "%Y-%m-%d"

[editor]
command = null  # Uses $EDITOR if null

[sorting]
by = "priority"
reverse = false
```

## Task Storage

Tasks are stored in JSON format at `~/.todo/tasks.json`:

```json
{
  "version": "1.0.0",
  "last_modified": "2026-01-06T18:40:00",
  "tasks": [
    {
      "id": 1,
      "title": "Pay electricity bill",
      "status": "pending",
      "priority": "high",
      "tags": ["finance", "urgent"],
      "project": "bills",
      "created_at": "2026-01-05T10:30:00",
      "due_date": "2026-01-10T00:00:00"
    }
  ],
  "next_id": 2
}
```

## Backups

Automatic backups are maintained at `~/.todo/backups/`:
- Last 10 versions are kept
- Timestamped format: `tasks.json.YYYY-MM-DD_HH-MM-SS`

## Date Formats

Supported date formats:

| Format | Example | Description |
|---------|-----------|-------------|
| YYYY-MM-DD | 2026-01-15 | Full date with year |
| MM-DD | 01-15 | Current year (assumed) |
| today | today | Today's date |
| tomorrow | tomorrow | Tomorrow's date |
| +N | +7 | N days from now |

## Common Workflows

### Daily Task Management

```bash
# Add morning tasks
todo add "Check emails" --priority low
todo add "Team standup" --due 2026-01-07T09:00:00 --priority medium --tag meeting
todo add "Submit report" --priority high --tag work,urgent

# Mark completed
todo done 1

# View remaining tasks
todo list --pending
```

### Project-Based Organization

```bash
# Add tasks for different projects
todo add "Design API" --project "Project Alpha" --tag development,backend
todo add "Write tests" --project "Project Alpha" --tag testing
todo add "Update docs" --project "Project Beta" --tag documentation

# View tasks by project
todo list --project "Project Alpha"
todo list --project "Project Beta"

### Tag-Based Filtering

```bash
# Add tagged tasks
todo add "Pay bills" --tag finance --priority high
todo add "Code review" --tag work,review --priority medium
todo add "Buy groceries" --tag personal --priority low

# Filter by specific tag
todo list --tag finance
todo list --tag work
todo list --tag personal

# Search across tags
todo search --tag review
```

### Due Date Management

```bash
# Add tasks with due dates
todo add "Submit report" --due 2026-01-10 --priority high
todo add "Renew license" --due tomorrow --tag urgent
todo add "Plan vacation" --due +30 --priority low

# View overdue tasks
todo list --overdue

# Sort by due date
todo list --sort due_date
```

## Command Reference

| Command | Aliases |
|---------|----------|
| add | new, create |
| list | ls |
| edit | modify, update |
| done | complete, finish, check |
| undo | reopen, uncomplete |
| delete | rm, remove |
| search | find |
| config | config set |
| undo-last | Undo last action |
| init | Initialize |
| --help | Show help |

## Color Scheme

- **Green**: Completed tasks
- **Yellow**: Pending tasks
- **Red**: Overdue tasks
- **Blue**: Info messages
- **Magenta**: Table headers
- **Cyan**: Tags

## Platform Notes

- **Windows**: Uses ASCII characters `[+], [X], [!], [i]` for icons to avoid encoding issues
- **macOS/Linux**: Uses Unicode icons `✓, ✗, ⚠, ℹ` for better UX

## License

MIT

Copyright (c) 2026 Syed Zafar Abbas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation of rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

For major changes, please open an issue first to discuss the proposed changes.

---

**Code Style**
- Follow PEP 8 style guidelines
- Use type hints for all functions, methods, and classes
- Add docstrings to all public functions, classes, and modules
- Keep functions focused and single-purpose

**Testing**
- Add tests for new features
- Ensure all tests pass before submitting pull requests
- Use pytest for unit tests

---

**Development Setup**

1. Forks the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Make your changes
6. Run tests: `pytest -v`
7. Deactivate when done: `deactivate`
