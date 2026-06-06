# Git Version Control Interview Questions and Answers

## Beginner Level Questions

### Q1: What is Git Version Control and what problem does it solve?

**Answer:**

Git is a distributed version control system for tracking changes in source code during software development. It is designed for coordinating work among programmers, but it can be used to track changes in any set of files.

**Key Use Cases:**
- Use case 1
- Use case 2
- Use case 3

### Q2: What are the core features of Git Version Control?

**Answer:**

The core features include:

## Beginner Level Questions

### What is Git and how does it differ from other version control systems?

**Answer:**

Git is a distributed version control system (DVCS) that allows multiple developers to work on the same project simultaneously. Unlike centralized systems like SVN, Git gives every developer a complete copy of the repository, enabling offline work and faster operations. Key differences: distributed architecture, branching and merging capabilities, cryptographic integrity, and performance.

## Beginner Level Questions

### Explain the difference between Git and GitHub.

**Answer:**

Git is the version control software that runs locally on your machine, while GitHub is a cloud-based hosting service for Git repositories. Git handles version control operations (commit, branch, merge), while GitHub provides remote storage, collaboration features (pull requests, issues), and web-based interface for Git repositories.

## Intermediate Level Questions

### What is the difference between git merge and git rebase?

**Answer:**

Git merge creates a merge commit that combines two branches, preserving the complete history. Git rebase replays commits from one branch onto another, creating a linear history. Merge preserves context but creates a more complex history. Rebase creates cleaner history but rewrites commit history. Use merge for public branches, rebase for local feature branches.

## Intermediate Level Questions

### How do you resolve merge conflicts?

**Answer:**

1. Identify conflicted files with `git status`. 2. Open files and look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`). 3. Manually edit to resolve conflicts, keeping desired changes. 4. Stage resolved files with `git add`. 5. Complete merge with `git commit`. Use `git merge --abort` to cancel merge, or tools like `git mergetool` for visual resolution.

## Advanced Level Questions

### Explain Git internals: objects, refs, and the index.

**Answer:**

Git stores data as objects: blobs (file content), trees (directory structure), commits (snapshots), and tags. Refs are pointers to commits (branches, HEAD). The index (staging area) is a binary file that stores information about what will go into the next commit. Objects are stored in `.git/objects/`, refs in `.git/refs/`, and the index is `.git/index`.


## References

- Official documentation
- Community resources
