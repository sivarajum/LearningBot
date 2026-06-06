# VS Code Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install VS Code
# Download from code.visualstudio.com

# Install extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
```

### 2. **Basic Usage**
- Open folder: File → Open Folder
- Terminal: Ctrl+` (Cmd+` on Mac)
- Command Palette: Ctrl+Shift+P
- Settings: Ctrl+,

### 3. **Key Shortcuts**
- Format: Shift+Alt+F
- Go to Definition: F12
- Find: Ctrl+F
- Replace: Ctrl+H

## Level 2 – Production Patterns

### Debugging
```json
// launch.json
{
    "version": "0.2.0",
    "configurations": [{
        "name": "Python: Current File",
        "type": "python",
        "request": "launch",
        "program": "${file}"
    }]
}
```

### Tasks
```json
// tasks.json
{
    "version": "2.0.0",
    "tasks": [{
        "label": "Run Tests",
        "type": "shell",
        "command": "pytest",
        "group": "test"
    }]
}
```

## Level 3 – Architect Playbook

### Remote Development
```bash
# Install Remote SSH extension
# Connect to remote server
# Edit files remotely
```

### Workspace Settings
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

## Ops Cheat Sheet

| Task | Shortcut | Notes |
| --- | --- | --- |
| Command Palette | Ctrl+Shift+P | All commands |
| Terminal | Ctrl+` | Toggle terminal |
| Find | Ctrl+F | Find in file |
| Go to Line | Ctrl+G | Jump to line |

## Checklist Before Production

- [ ] Install essential extensions
- [ ] Configure workspace settings
- [ ] Set up debugging
- [ ] Configure tasks
- [ ] Set up Git integration
- [ ] Customize keybindings
- [ ] Set up remote development
- [ ] Configure linting and formatting
