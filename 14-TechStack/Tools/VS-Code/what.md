# Visual Studio Code Guide

## VS Code Fundamentals

### What is Visual Studio Code?

Visual Studio Code (VS Code) is a free, open-source code editor developed by Microsoft. It provides a rich development experience with built-in support for debugging, task running, version control, and extensions for additional languages and tools.

### Key Characteristics

- **Cross-platform**: Runs on Windows, macOS, and Linux
- **Extensible**: Thousands of extensions available
- **Lightweight**: Fast startup and low resource usage
- **Integrated Terminal**: Built-in command line interface
- **Git Integration**: Native Git support with GUI
- **IntelliSense**: Smart code completion and navigation
- **Customizable**: Themes, keybindings, and settings

### Core Features

```json
// VS Code User Settings (settings.json)
{
  "editor.fontSize": 14,
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.wordWrap": "on",
  "editor.minimap.enabled": true,
  "editor.lineNumbers": "on",
  "workbench.editor.enablePreview": false,
  "files.autoSave": "afterDelay",
  "terminal.integrated.shell.osx": "/bin/zsh"
}
```

## Installation and Setup

### Installing VS Code

```bash
# macOS with Homebrew
brew install --cask visual-studio-code

# Ubuntu/Debian
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt install apt-transport-https
sudo apt update
sudo apt install code

# CentOS/RHEL/Fedora
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
sudo dnf install code

# Windows - Download from https://code.visualstudio.com/download
```

### Initial Setup

```bash
# Launch VS Code
code

# Install essential extensions
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension ms-python.python
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-json

# Open specific file or directory
code /path/to/file.txt
code /path/to/project

# Open current directory
code .
```

### User Interface Overview

```json
// VS Code UI Layout
{
  "Activity Bar": {
    "Explorer": "File navigation",
    "Search": "Find in files",
    "Source Control": "Git integration",
    "Run and Debug": "Debugger",
    "Extensions": "Extension marketplace"
  },
  "Side Bar": {
    "Dynamic content based on activity"
  },
  "Editor": {
    "Main coding area",
    "Multiple tabs",
    "Split view support"
  },
  "Panel": {
    "Terminal": "Integrated terminal",
    "Output": "Command output",
    "Problems": "Errors and warnings",
    "Debug Console": "Debug output"
  },
  "Status Bar": {
    "File encoding, line endings, language mode",
    "Git branch, errors, warnings"
  }
}
```

## Extensions Management

### Essential Extensions

```bash
# Language Support
code --install-extension ms-vscode.vscode-typescript-next  # TypeScript
code --install-extension ms-python.python                  # Python
code --install-extension ms-vscode.vscode-json             # JSON
code --install-extension ms-vscode.vscode-yaml             # YAML
code --install-extension redhat.java                       # Java

# Development Tools
code --install-extension esbenp.prettier-vscode            # Code formatting
code --install-extension ms-vscode.vscode-eslint            # JavaScript linting
code --install-extension ms-vscode.vscode-jshint            # JavaScript validation
code --install-extension eamodio.gitlens                    # Git enhancements

# Productivity
code --install-extension ms-vscode.vscode-icons             # File icons
code --install-extension christian-kohler.path-intellisense # Path completion
code --install-extension formulahendry.auto-rename-tag      # HTML tag renaming
code --install-extension bradlc.vscode-tailwindcss          # Tailwind CSS

# Frameworks
code --install-extension ms-vscode.vscode-react-native       # React Native
code --install-extension angular.ng-template                # Angular
code --install-extension ms-vscode.vscode-vue                # Vue.js
```

### Extension Development

```json
// package.json for VS Code extension
{
  "name": "my-extension",
  "displayName": "My Extension",
  "description": "A sample VS Code extension",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.70.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [
    "onCommand:myExtension.helloWorld"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "myExtension.helloWorld",
        "title": "Hello World"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.70.0",
    "@types/node": "16.x",
    "typescript": "^4.7.4"
  }
}
```

```typescript
// extension.ts - Main extension file
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  console.log('Extension "my-extension" is now active!');

  let disposable = vscode.commands.registerCommand('myExtension.helloWorld', function () {
    vscode.window.showInformationMessage('Hello World from my-extension!');
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
```

## Workspace and Projects

### Workspace Configuration

```json
// .vscode/settings.json - Workspace settings
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.pythonPath": "venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  }
}
```

```json
// .vscode/tasks.json - Build and test tasks
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "npm",
      "script": "build",
      "group": "build",
      "presentation": {
        "panel": "shared"
      },
      "problemMatcher": ["$tsc"]
    },
    {
      "type": "npm",
      "script": "test",
      "group": {
        "kind": "test",
        "isDefault": true
      }
    },
    {
      "label": "Run Python Tests",
      "type": "shell",
      "command": "python",
      "args": ["-m", "pytest"],
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

```json
// .vscode/launch.json - Debug configurations
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Node.js",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/app.js",
      "skipFiles": [
        "<node_internals>/**"
      ]
    },
    {
      "name": "Debug Python",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Chrome Debug",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/src"
    }
  ]
}
```

### Multi-root Workspaces

```json
// project.code-workspace - Multi-root workspace
{
  "folders": [
    {
      "name": "Client App",
      "path": "client"
    },
    {
      "name": "Server API",
      "path": "server"
    },
    {
      "name": "Shared Library",
      "path": "shared"
    }
  ],
  "settings": {
    "typescript.preferences.importModuleSpecifier": "relative"
  },
  "extensions": {
    "recommendations": [
      "ms-vscode.vscode-typescript-next",
      "esbenp.prettier-vscode"
    ]
  }
}
```

## Code Editing Features

### IntelliSense and Code Completion

```typescript
// TypeScript example with IntelliSense
interface User {
  id: number;
  name: string;
  email: string;
}

function createUser(userData: Partial<User>): User {
  return {
    id: Date.now(),
    name: userData.name || 'Anonymous',
    email: userData.email || ''
  };
}

// IntelliSense shows:
// - Parameter hints
// - Method signatures
// - Auto-completion
// - Quick info on hover
const user = createUser({
  name: 'John Doe',
  email: 'john@example.com'
});
```

### Code Navigation

```typescript
// Go to Definition (F12)
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// Go to References (Shift+F12)
const total = calculateTotal(cartItems);

// Peek Definition (Alt+F12)
const result = calculateTotal(/* peek here */);

// Symbol search (Ctrl+Shift+O)
class ShoppingCart {
  // @ symbol search
}

// Breadcrumb navigation
// File > Class > Method > Variable
```

### Refactoring

```typescript
// Extract Method (Ctrl+Shift+R)
function processOrder(order: Order) {
  // Select code and extract
  validateOrder(order);
  calculateTax(order);
  sendConfirmation(order);
}

// Rename Symbol (F2)
const userName = 'John'; // Rename to customerName

// Extract Variable
const total = items.reduce((sum, item) => sum + item.price, 0);

// Extract Interface
interface OrderProcessor {
  process(order: Order): Promise<Result>;
  validate(order: Order): boolean;
}
```

### Code Actions

```typescript
// Quick fixes and refactorings
import * as fs from 'fs'; // Shows "Convert to ES6 import"

// Auto-fixable issues
function example() {
  console.log('Hello'); // Shows "Add semicolon"
}

// Source actions
// - Organize imports
// - Sort imports
// - Remove unused imports
// - Add missing imports
```

## Integrated Terminal

### Terminal Configuration

```json
// Terminal settings
{
  "terminal.integrated.shell.osx": "/bin/zsh",
  "terminal.integrated.shell.linux": "/bin/bash",
  "terminal.integrated.shell.windows": "C:\\Windows\\System32\\cmd.exe",
  "terminal.integrated.fontSize": 12,
  "terminal.integrated.lineHeight": 1.2,
  "terminal.integrated.cursorStyle": "line",
  "terminal.integrated.cursorBlinking": true
}
```

### Terminal Commands

```bash
# Open integrated terminal
# Ctrl+` (backtick)

# Create new terminal
# Ctrl+Shift+`

# Split terminal
# Ctrl+Shift+5

# Run commands
npm install
python app.py
git status

# Terminal tasks
# Configure in tasks.json for complex commands
```

### Terminal Integration

```json
// tasks.json with terminal integration
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build and Run",
      "type": "shell",
      "command": "npm",
      "args": ["run", "dev"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "isBackground": true,
      "problemMatcher": ["$tsc"]
    }
  ]
}
```

## Git Integration

### Source Control Panel

```bash
# Git commands in VS Code
# Ctrl+Shift+G to open Source Control

# Stage changes
# Click + next to files or use Git: Stage Changes

# Commit
# Enter message and Ctrl+Enter

# Push/Pull
# Use buttons in status bar or command palette

# View diff
# Click on file in Source Control panel

# Create branch
# Git: Create Branch

# Merge
# Git: Merge Branch
```

### GitLens Extension

```json
// GitLens configuration
{
  "gitlens.currentLine.enabled": true,
  "gitlens.hovers.currentLine.over": "line",
  "gitlens.hovers.enabled": true,
  "gitlens.codeLens.enabled": true,
  "gitlens.blame.heatmap.enabled": false,
  "gitlens.views.repositories.files.layout": "list"
}
```

```typescript
// GitLens features
// Hover over code to see:
// - Last commit that modified the line
// - Author and date
// - Commit message

// CodeLens shows:
// - Recent commits for the file
// - Authors who modified the file

// GitLens view:
// - File history
// - Line history
// - Commit search
```

## Debugging

### Debug Configurations

```json
// launch.json examples
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Node.js",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/server.js",
      "skipFiles": [
        "<node_internals>/**"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    },
    {
      "name": "Debug React App",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    },
    {
      "name": "Attach to Process",
      "type": "node",
      "request": "attach",
      "processId": "${command:PickProcess}"
    }
  ]
}
```

### Debug Features

```typescript
// Breakpoints
function calculateTotal(items) {
  let total = 0;
  for (let item of items) {
    total += item.price; // Set breakpoint here
  }
  return total;
}

// Conditional breakpoints
if (user.age > 18) { // Break only when condition is true
  processUser(user);
}

// Logpoints
console.log(`Processing user: ${user.name}`); // Log without stopping

// Watch expressions
// Add expressions to watch during debugging
// - user.name
// - items.length
// - total > 100
```

### Debug Console

```javascript
// Debug console commands
> items.length
4

> items[0]
{ id: 1, name: "Item 1", price: 10 }

> calculateTotal(items)
40

// Evaluate expressions
> items.filter(item => item.price > 5)
[{ id: 1, name: "Item 1", price: 10 }, { id: 2, name: "Item 2", price: 15 }]

// Modify variables
> items[0].price = 20
20
```

## Customization

### Themes and Appearance

```json
// Theme configuration
{
  "workbench.colorTheme": "Dark Modern",
  "workbench.iconTheme": "vs-seti",
  "editor.fontFamily": "'Fira Code', 'Courier New', monospace",
  "editor.fontLigatures": true,
  "editor.fontSize": 14,
  "editor.lineHeight": 1.5,
  "workbench.fontAliasing": "antialiased"
}
```

### Keybindings

```json
// keybindings.json
[
  {
    "key": "ctrl+shift+l",
    "command": "editor.action.selectHighlights",
    "when": "editorFocus"
  },
  {
    "key": "ctrl+d",
    "command": "editor.action.addSelectionToNextFindMatch",
    "when": "editorFocus"
  },
  {
    "key": "alt+up",
    "command": "editor.action.moveLinesUpAction",
    "when": "editorTextFocus && !editorReadonly"
  },
  {
    "key": "ctrl+shift+t",
    "command": "workbench.action.reopenClosedEditor"
  }
]
```

### Snippets

```json
// javascript.json - User snippets
{
  "Console Log": {
    "prefix": "cl",
    "body": [
      "console.log('$1', $1);"
    ],
    "description": "Console log with variable"
  },
  "React Functional Component": {
    "prefix": "rfc",
    "body": [
      "import React from 'react';",
      "",
      "function ${1:ComponentName}() {",
      "  return (",
      "    <div>",
      "      $2",
      "    </div>",
      "  );",
      "}",
      "",
      "export default ${1:ComponentName};"
    ],
    "description": "React functional component"
  }
}
```

## Language-Specific Features

### Python Development

```json
// Python settings
{
  "python.pythonPath": "venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

```python
# Python code with VS Code features
def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0

    total = sum(numbers)  # IntelliSense shows sum() signature
    return total / len(numbers)

# Debugging
result = calculate_average([1, 2, 3, 4, 5])  # Set breakpoint
print(f"Average: {result}")  # Debug console
```

### JavaScript/TypeScript Development

```json
// JavaScript/TypeScript settings
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "javascript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  },
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  }
}
```

```typescript
// TypeScript with full IntelliSense
interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
}

class ProductService {
  private products: Product[] = [];

  addProduct(product: Product): void {
    this.products.push(product);
  }

  getProductsByCategory(category: string): Product[] {
    return this.products.filter(p => p.category === category);
  }

  getTotalValue(): number {
    return this.products.reduce((sum, p) => sum + p.price, 0);
  }
}

// Usage with code completion
const service = new ProductService();
service.addProduct({
  id: 1,
  name: "Laptop",
  price: 999,
  category: "Electronics"
});

const electronics = service.getProductsByCategory("Electronics");
const total = service.getTotalValue();
```

## Remote Development

### Remote SSH

```json
// Remote SSH configuration
{
  "remote.SSH.configFile": "~/.ssh/config",
  "remote.SSH.showLoginTerminal": true,
  "remote.SSH.useLocalServer": true
}
```

```bash
# SSH config file (~/.ssh/config)
Host myserver
    HostName 192.168.1.100
    User developer
    IdentityFile ~/.ssh/id_rsa

Host dev-server
    HostName dev.example.com
    User vscode
    ProxyCommand ssh proxy.example.com -W %h:%p
```

### Dev Containers

```json
// .devcontainer/devcontainer.json
{
  "name": "Python 3",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},
    "ghcr.io/devcontainers/features/docker-in-docker:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-vscode.vscode-json"
      ],
      "settings": {
        "python.pythonPath": "/usr/local/bin/python"
      }
    }
  },
  "forwardPorts": [3000, 8000],
  "postCreateCommand": "pip install -r requirements.txt"
}
```

### WSL Development

```json
// WSL configuration
{
  "remote.WSL.fileWatcher.polling": false,
  "remote.WSL.server.connectThroughLocalhost": true,
  "terminal.integrated.shell.windows": "C:\\Windows\\System32\\wsl.exe"
}
```

## Performance and Troubleshooting

### Performance Optimization

```json
// Performance settings
{
  "editor.largeFileOptimizations": true,
  "files.exclude": {
    "**/node_modules": true,
    "**/.git": true,
    "**/.DS_Store": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/*.log": true
  },
  "editor.minimap.enabled": false,
  "editor.renderWhitespace": "boundary",
  "workbench.editor.limit.enabled": true,
  "workbench.editor.limit.value": 10
}
```

### Troubleshooting

```bash
# Check VS Code version
code --version

# List installed extensions
code --list-extensions

# Disable all extensions for testing
code --disable-extensions

# Clear extension cache
# Windows: %USERPROFILE%\.vscode\extensions
# macOS: ~/.vscode/extensions
# Linux: ~/.vscode/extensions

# Reset settings
# Remove settings.json and keybindings.json

# Check for updates
# Help > Check for Updates
```

### Common Issues

```json
// Fix common problems
{
  // Extension host issues
  "extensions.experimental.affinity": {
    "ms-vscode.vscode-typescript-next": 1
  },

  // Performance issues
  "editor.cursorBlinking": "solid",
  "editor.smoothScrolling": false,

  // Git issues
  "git.autofetch": false,
  "git.confirmSync": false,

  // Large workspace issues
  "workbench.editor.enablePreview": false,
  "explorer.openEditors.visible": 0
}
```

## Advanced Features

### Command Palette

```bash
# Essential commands
# Ctrl+Shift+P (Cmd+Shift+P on Mac)

# File operations
> File: New File
> File: Open Folder
> File: Save All

# Navigation
> Go to File
> Go to Symbol
> Go to Line/Column

# Git commands
> Git: Clone
> Git: Commit
> Git: Push

# Extension management
> Extensions: Install Extensions
> Extensions: Show Recommended Extensions
```

### Multi-Cursor Editing

```javascript
// Multi-cursor examples
const users = [
  { name: 'Alice', age: 25 },
  { name: 'Bob', age: 30 },
  { name: 'Charlie', age: 35 }
];

// Select all 'name' and edit
// Ctrl+D to select next occurrence
// Ctrl+Shift+L to select all occurrences

// Column selection
// Alt+Shift+Click or Alt+Shift+Drag

// Add cursor above/below
// Ctrl+Alt+Up/Down
```

### Emmet Integration

```html
<!-- Emmet abbreviations -->
<!-- Type abbreviation and press Tab -->

<!-- Basic HTML -->
html:5
<!-- Expands to full HTML5 document -->

<!-- Elements -->
div.container
<!-- <div class="container"></div> -->

<!-- Nesting -->
ul>li*3
<!-- <ul>
       <li></li>
       <li></li>
       <li></li>
     </ul> -->

<!-- Sibling -->
div+p+bq
<!-- <div></div>
     <p></p>
     <blockquote></blockquote> -->

<!-- Climbing up -->
div>p>span^div
<!-- <div>
       <p><span></span></p>
     </div>
     <div></div> -->
```

This comprehensive guide covers VS Code from basic usage to advanced features, customization, and development workflows.
