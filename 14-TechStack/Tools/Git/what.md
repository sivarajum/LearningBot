# Git Version Control Guide

## Git Fundamentals

### What is Git?

Git is a distributed version control system that tracks changes in source code during software development. It allows multiple developers to collaborate on projects, maintain version history, and manage code branches efficiently.

### Key Characteristics

- **Distributed**: Every developer has a full copy of the repository
- **Branching**: Lightweight branching and merging capabilities
- **Performance**: Fast operations with local repository access
- **Integrity**: Cryptographic integrity checking of content
- **Flexibility**: Supports various workflows and branching strategies
- **Open Source**: Free and widely adopted

### Core Concepts

```bash
# Repository - Project directory with .git folder
git init                    # Initialize new repository
git clone <url>            # Clone existing repository

# Working Directory - Current state of files
# Staging Area - Files ready to be committed
# Repository - Committed snapshots

# Basic workflow
git add <file>             # Stage file changes
git commit -m "message"    # Commit staged changes
git push origin main       # Push to remote repository
git pull origin main       # Pull from remote repository
```

## Installation and Setup

### Installing Git

```bash
# macOS with Homebrew
brew install git

# Ubuntu/Debian
sudo apt update
sudo apt install git

# CentOS/RHEL
sudo yum install git

# Windows - Download from https://git-scm.com/download/win
# Or use Chocolatey: choco install git

# Verify installation
git --version
```

### Initial Configuration

```bash
# Set user identity
git config --global user.name "John Doe"
git config --global user.email "john.doe@example.com"

# Set default editor
git config --global core.editor "vim"
git config --global core.editor "code --wait"  # VS Code

# Set default branch name
git config --global init.defaultBranch main

# Enable colored output
git config --global color.ui auto

# Set line ending preferences
git config --global core.autocrlf input    # Linux/Mac
git config --global core.autocrlf true     # Windows

# View configuration
git config --list
git config --global --list
```

### SSH Key Setup

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "john.doe@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub

# Add to GitHub/GitLab/etc. in Settings > SSH Keys
```

## Basic Operations

### Creating Repositories

```bash
# Initialize new repository
mkdir my-project
cd my-project
git init

# Clone existing repository
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git  # SSH

# Clone specific branch
git clone -b develop https://github.com/user/repo.git

# Clone with shallow depth (last n commits)
git clone --depth 1 https://github.com/user/repo.git
```

### Working with Files

```bash
# Check repository status
git status

# Add files to staging area
git add file.txt                    # Single file
git add *.txt                       # Pattern matching
git add .                           # All files
git add -A                          # All files including deleted

# Remove files from staging
git reset HEAD file.txt            # Unstage file
git reset HEAD                      # Unstage all

# Discard working directory changes
git checkout -- file.txt           # Discard changes to file
git checkout -- .                  # Discard all changes

# Rename/move files
git mv old_name.txt new_name.txt

# Remove files
git rm file.txt                    # Remove and stage deletion
git rm --cached file.txt           # Remove from staging only
```

### Committing Changes

```bash
# Commit staged changes
git commit -m "Add user authentication feature"

# Commit with detailed message
git commit -m "Add user authentication

- Implement login form
- Add password validation
- Create user session management"

# Amend last commit
git commit --amend -m "Updated commit message"

# Commit all tracked files
git commit -a -m "Update all files"

# Interactive staging
git add -i                         # Interactive add
git add -p                         # Patch mode for hunks
```

### Viewing History

```bash
# View commit history
git log
git log --oneline                  # Compact format
git log --graph --decorate         # With branch graph
git log --author="John"            # Filter by author
git log --since="2023-01-01"       # Filter by date
git log --grep="bug"               # Search commit messages

# View specific commit
git show <commit-hash>
git show HEAD                      # Latest commit
git show HEAD~1                    # Previous commit

# View file history
git log --follow file.txt
git blame file.txt                 # Who changed what line

# Compare commits
git diff HEAD~1 HEAD              # Compare last two commits
git diff <commit1> <commit2>      # Compare specific commits
```

## Branching and Merging

### Branch Operations

```bash
# List branches
git branch                         # Local branches
git branch -a                      # All branches (local + remote)
git branch -r                      # Remote branches only

# Create branch
git branch feature/login           # Create branch
git checkout -b feature/login      # Create and switch
git switch -c feature/login        # Create and switch (Git 2.23+)

# Switch branches
git checkout feature/login
git switch feature/login           # Git 2.23+

# Rename branch
git branch -m old-name new-name

# Delete branch
git branch -d feature/login        # Safe delete (merged)
git branch -D feature/login        # Force delete (unmerged)

# Compare branches
git diff main..feature/login
git log main..feature/login        # Commits in feature not in main
```

### Merging Branches

```bash
# Merge feature branch into main
git checkout main
git merge feature/login

# Merge with custom commit message
git merge feature/login -m "Merge login feature"

# Abort merge (if conflicts)
git merge --abort

# Fast-forward vs merge commit
git merge --no-ff feature/login    # Always create merge commit
git merge --ff-only feature/login  # Only fast-forward

# Squash merge
git merge --squash feature/login
git commit -m "Add login feature"
```

### Rebasing

```bash
# Rebase current branch onto main
git checkout feature/login
git rebase main

# Interactive rebase (last 3 commits)
git rebase -i HEAD~3

# Rebase with conflict resolution
git rebase --continue             # After resolving conflicts
git rebase --skip                 # Skip current patch
git rebase --abort                # Abort rebase

# Rebase onto different branch
git rebase --onto main develop feature/login
```

## Remote Repositories

### Working with Remotes

```bash
# Add remote repository
git remote add origin https://github.com/user/repo.git

# View remotes
git remote -v                     # List remotes
git remote show origin            # Show remote details

# Change remote URL
git remote set-url origin https://github.com/user/repo.git

# Remove remote
git remote remove origin

# Rename remote
git remote rename origin upstream
```

### Pushing and Pulling

```bash
# Push branch to remote
git push origin feature/login

# Push and set upstream
git push -u origin feature/login

# Push all branches
git push --all origin

# Push tags
git push --tags

# Pull changes
git pull origin main              # Fetch and merge
git pull --rebase origin main     # Fetch and rebase

# Fetch without merging
git fetch origin
git fetch --all                   # Fetch all remotes

# Pull from different remote
git pull upstream main
```

### Tracking Branches

```bash
# Set upstream branch
git branch --set-upstream-to=origin/main main

# View tracking branches
git branch -vv

# Unset upstream
git branch --unset-upstream

# Push new local branch
git push -u origin new-branch
```

## Advanced Operations

### Stashing Changes

```bash
# Stash working directory changes
git stash                         # Stash changes
git stash save "Work in progress" # Stash with message

# List stashes
git stash list

# Apply stash
git stash apply                   # Apply latest stash
git stash apply stash@{1}         # Apply specific stash

# Apply and drop stash
git stash pop

# Create branch from stash
git stash branch feature/fix stash@{0}

# Drop stashes
git stash drop stash@{0}          # Drop specific stash
git stash clear                   # Drop all stashes
```

### Tagging

```bash
# Create lightweight tag
git tag v1.0

# Create annotated tag
git tag -a v1.0 -m "Version 1.0 release"

# Tag specific commit
git tag -a v0.9 9fceb02

# List tags
git tag
git tag -l "v1.*"                 # Pattern matching

# Show tag details
git show v1.0

# Push tags
git push origin v1.0
git push origin --tags

# Delete tags
git tag -d v1.0                   # Local
git push origin --delete v1.0     # Remote
```

### Cherry Picking

```bash
# Cherry pick single commit
git cherry-pick <commit-hash>

# Cherry pick multiple commits
git cherry-pick <hash1> <hash2>

# Cherry pick range
git cherry-pick <start>..<end>

# Cherry pick with edit
git cherry-pick -e <commit-hash>

# Continue after conflict resolution
git cherry-pick --continue

# Abort cherry pick
git cherry-pick --abort
```

### Reflog

```bash
# View reference log
git reflog

# Show detailed reflog
git reflog --all

# Recover lost commits
git checkout <commit-hash>        # From reflog
git branch recover-branch <commit-hash>

# Clean reflog (dangerous)
git reflog expire --expire=now --all
git gc --prune=now
```

## Conflict Resolution

### Merge Conflicts

```bash
# During merge/rebase, conflicts occur
# Git marks conflict areas in files

# View conflicted files
git status

# View conflict details
git diff

# Resolve conflicts manually
# Edit files, remove conflict markers (<<<<<<<, =======, >>>>>>>)

# Mark as resolved
git add <resolved-file>

# Complete merge
git commit                        # For merge
git rebase --continue            # For rebase
```

### Advanced Conflict Resolution

```bash
# Use mergetool
git mergetool

# Configure mergetool
git config --global merge.tool vimdiff
git config --global mergetool.vimdiff.cmd 'vimdiff $MERGED'

# Accept different sides
git checkout --ours file.txt     # Accept our changes
git checkout --theirs file.txt   # Accept their changes

# For rebase conflicts
git rebase --skip               # Skip conflicting commit
git rebase --abort              # Abort rebase
```

## Git Workflows

### Git Flow

```bash
# Initialize git flow
git flow init

# Feature branches
git flow feature start login
git flow feature finish login

# Release branches
git flow release start 1.0
git flow release finish 1.0

# Hotfix branches
git flow hotfix start urgent-fix
git flow hotfix finish urgent-fix

# Support branches
git flow support start 1.x 1.0
```

### GitHub Flow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commits
git add .
git commit -m "Implement new feature"

# Push feature branch
git push -u origin feature/new-feature

# Create Pull Request on GitHub

# After approval, merge via GitHub
# Or merge locally
git checkout main
git pull origin main
git merge feature/new-feature
git push origin main

# Delete feature branch
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### Trunk-Based Development

```bash
# Work on main branch
git checkout main
git pull origin main

# Create short-lived feature branch
git checkout -b feature/small-change

# Make small, frequent commits
git add .
git commit -m "Small change 1"
git push origin feature/small-change

# Merge back quickly
git checkout main
git pull origin main
git merge feature/small-change
git push origin main
git branch -d feature/small-change
```

## Performance and Maintenance

### Repository Maintenance

```bash
# Clean untracked files
git clean -n                     # Dry run
git clean -f                     # Remove files
git clean -fd                    # Remove files and directories

# Garbage collection
git gc                           # Basic cleanup
git gc --aggressive              # Aggressive cleanup
git gc --prune=now               # Prune all loose objects

# Repack repository
git repack -a -d                 # Repack all objects

# Verify repository integrity
git fsck                         # Check for corruption
git fsck --full                  # Full check
```

### Large File Handling

```bash
# Git LFS setup
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "*.zip"

# Add .gitattributes
git add .gitattributes
git commit -m "Track large files with LFS"

# Migrate existing large files
git lfs migrate import --include="*.psd"

# View LFS files
git lfs ls-files
```

### Performance Optimization

```bash
# Shallow clone for large repos
git clone --depth 1 <url>
git fetch --unshallow            # Convert to full clone

# Sparse checkout
git sparse-checkout init
git sparse-checkout set folder1 folder2

# Delta compression
git config --global core.compression 9
git config --global core.loosecompression 9

# Parallel operations
git config --global pack.threads 0  # Use all CPU cores
```

## Git Hooks

### Local Hooks

```bash
# Pre-commit hook - runs before commit
#!/bin/sh
# .git/hooks/pre-commit

# Run tests
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi

# Check code style
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting failed. Commit aborted."
  exit 1
fi
```

```bash
# Commit-msg hook - validates commit message
#!/bin/sh
# .git/hooks/commit-msg

commit_msg=$(cat $1)
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore): "; then
  echo "Commit message must start with type: feat, fix, docs, style, refactor, test, chore"
  exit 1
fi
```

```bash
# Pre-push hook - runs before push
#!/bin/sh
# .git/hooks/pre-push

# Run full test suite
npm run test:full
if [ $? -ne 0 ]; then
  echo "Full tests failed. Push aborted."
  exit 1
fi
```

### Installing Hooks

```bash
# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg

# Copy hooks to new repositories
# Option 1: Manual copy
cp .git/hooks/* /path/to/new/repo/.git/hooks/

# Option 2: Use templates
git config --global init.templatedir ~/.git-templates
mkdir -p ~/.git-templates/hooks
cp hooks/* ~/.git-templates/hooks/
chmod +x ~/.git-templates/hooks/*
```

## Advanced Configuration

### Git Configuration Files

```bash
# System-wide config (/etc/gitconfig)
git config --system user.name "System User"

# Global config (~/.gitconfig)
git config --global user.name "John Doe"
git config --global user.email "john@example.com"

# Repository-specific config (.git/config)
git config user.name "Project User"

# Environment variables
GIT_AUTHOR_NAME="John Doe"
GIT_AUTHOR_EMAIL="john@example.com"
GIT_COMMITTER_NAME="Jane Smith"
GIT_COMMITTER_EMAIL="jane@example.com"
```

### Advanced Config Options

```bash
# Performance settings
git config --global core.preloadindex true
git config --global core.fscache true
git config --global gc.auto 256

# Diff and merge settings
git config --global diff.algorithm histogram
git config --global merge.conflictstyle diff3

# Push settings
git config --global push.default simple
git config --global push.followTags true

# Pull settings
git config --global pull.rebase true
git config --global pull.ff only

# Alias settings
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
```

## Git with IDEs

### VS Code Integration

```bash
# Configure VS Code as Git editor
git config --global core.editor "code --wait"

# VS Code Git settings (settings.json)
{
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "git.autofetch": true,
  "git.enableCommitSigning": false,
  "git.useEditorAsCommitInput": true,
  "git.untrackedChanges": "mixed",
  "git.ignoreLimitWarning": true
}
```

### IntelliJ IDEA Integration

```bash
# Configure IntelliJ as Git editor
git config --global core.editor "idea --wait"

# IntelliJ Git settings
# File > Settings > Version Control > Git
# - Set Git executable path
# - Configure SSH executable
# - Set commit message template
```

## Troubleshooting

### Common Issues

```bash
# Fix "fatal: refusing to merge unrelated histories"
git pull origin main --allow-unrelated-histories

# Fix "fatal: The current branch has no upstream branch"
git push -u origin <branch-name>

# Fix "error: failed to push some refs"
git pull --rebase origin main
git push origin main

# Fix "fatal: Not a git repository"
git init  # If not initialized
cd /correct/path  # If in wrong directory

# Fix "fatal: remote origin already exists"
git remote remove origin
git remote add origin <url>
```

### Recovery Scenarios

```bash
# Recover deleted branch
git reflog
git checkout -b recovered-branch <commit-hash>

# Recover lost commits
git reflog --all
git cherry-pick <commit-hash>

# Fix detached HEAD
git checkout main  # Or any branch

# Recover from bad rebase
git rebase --abort

# Recover from bad merge
git merge --abort
```

### Repository Repair

```bash
# Fix corrupted repository
git fsck --full
git gc --prune=now

# Recover from disk full
git gc --aggressive --prune=now

# Fix line ending issues
git add --renormalize .

# Clean up large files
git filter-branch --tree-filter 'rm -rf large-file.zip' HEAD
```

## Git Best Practices

### Commit Guidelines

```bash
# Good commit messages
git commit -m "feat: add user authentication system

- Implement JWT token-based auth
- Add login/logout endpoints
- Create user registration flow
- Add password reset functionality"

# Bad commit messages
git commit -m "fix"
git commit -m "update"
git commit -m "changes"

# Conventional commits
<type>[optional scope]: <description>

[jira-ticket] <type>: <description>
```

### Branch Naming

```bash
# Feature branches
feature/user-authentication
feature/payment-integration
feature/ui-redesign

# Bug fixes
bugfix/login-validation
bugfix/memory-leak
hotfix/security-patch

# Release branches
release/v1.2.0
release/v2.0.0-beta

# Environment branches
develop
staging
production
```

### Repository Organization

```bash
# Directory structure
project/
├── .git/
├── .gitignore
├── README.md
├── docs/
├── src/
├── tests/
├── scripts/
└── .github/
    └── workflows/
```

### Security Practices

```bash
# Avoid committing secrets
# Use .gitignore for sensitive files
echo "*.key" >> .gitignore
echo ".env" >> .gitignore
echo "secrets/" >> .gitignore

# Use SSH keys instead of passwords
# Enable commit signing
git config --global commit.gpgsign true
git config --global user.signingkey <key-id>

# Regular security audits
git log --all --full-history -- secrets.txt
```

This comprehensive guide covers Git from basic operations to advanced features, workflows, and best practices for effective version control in software development.
