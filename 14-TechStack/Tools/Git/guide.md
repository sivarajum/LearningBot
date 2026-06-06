# Git Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initialize repository
git init

# Clone repository
git clone https://github.com/user/repo.git
```

### 2. **Basic Operations**
```bash
# Add files
git add file.txt
git add .

# Commit
git commit -m "Initial commit"

# Status
git status

# Log
git log
```

### 3. **Branching**
```bash
# Create branch
git branch feature-branch

# Switch branch
git checkout feature-branch

# Merge
git merge feature-branch
```

## Level 2 – Production Patterns

### Advanced Branching
```bash
# Rebase
git rebase main

# Cherry-pick
git cherry-pick commit-hash
```

### Collaboration
```bash
# Remote
git remote add origin https://github.com/user/repo.git

# Push
git push origin main

# Pull
git pull origin main

# Fetch
git fetch origin
```

## Level 3 – Architect Playbook

### Workflows
```bash
# Git Flow
git flow init
git flow feature start new-feature
git flow feature finish new-feature

# GitHub Flow
# Create branch → Make changes → Open PR → Merge
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Status | `git status` | Check status |
| Add | `git add .` | Stage files |
| Commit | `git commit -m "msg"` | Commit changes |
| Push | `git push` | Push to remote |
| Pull | `git pull` | Pull from remote |

## Checklist Before Production

- [ ] Set up proper branching strategy
- [ ] Configure .gitignore
- [ ] Set up hooks
- [ ] Implement code review process
- [ ] Set up CI/CD
- [ ] Document workflow
- [ ] Train team on Git
- [ ] Set up backup strategy
