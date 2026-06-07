# MyGitclone

A minimal Git clone built entirely in Python as a learning project to understand how version control systems work behind the scenes.

## 📖 Overview

MyGit is a simplified implementation of Git that recreates many of its core concepts, including object storage, commits, branches, tags, references, and repository management.

Instead of simply using Git, I challenged myself to build a version control system from scratch to learn how Git actually works internally.

---

# ✨ Features

- Initialize repositories
- Store objects using SHA-1 hashes
- Create and manage commits
- Generate tree objects from directories
- View commit history
- Create and switch branches
- Create tags
- Resolve object references
- Checkout commits and branches
- Compressed object storage

---

# 🛠️ Built With

- Python
- argparse
- hashlib
- pathlib
- zlib
- shutil
- file system operations

---

# 🚀 Usage

## Initialize Repository

```bash
python mygit.py init
```

## Create a Commit

```bash
python mygit.py commit -m "Initial Commit"
```

## View Commit History

```bash
python mygit.py log
```

## Create a Branch

```bash
python mygit.py branch feature
```

## Switch Branches

```bash
python mygit.py checkout feature
```

## Create a Tag

```bash
python mygit.py tag v1.0
```

---

# 📂 How It Works

MyGit stores repository data inside a hidden `.mygit` folder.

```text
.mygit/
├── objects/
├── refs/
│   ├── heads/
│   └── tags/
├── logs/
├── info/
└── HEAD
```

Objects are stored using SHA-1 hashes and compressed before being written to disk, similar to how Git manages its object database.

---

# 📚 What I Learned

Building MyGit taught me a lot about both Python and version control systems.

### Git Internals

- How Git stores data as objects
- How SHA-1 hashing identifies content
- How commits connect through parent references
- How trees represent directories
- How branches are actually pointers to commits
- How tags work as named references

### Python Skills

- Working with binary data
- Reading and writing files
- Recursive directory traversal
- Data compression and decompression
- Building command-line applications
- Managing project structure

### Biggest Realization

Before this project, I knew how to use Git.

After this project, I understood *why Git works*.

---

# ⚠️ Challenges & Mistakes

This project was one of the most challenging things I have built so far.

## Mistakes I Made

- I originally thought branches stored separate copies of files.
- I struggled to understand how commit history was connected.
- I made bugs while writing and reading objects.
- I underestimated how difficult checkout functionality would be.
- I had several issues caused by incorrect object references.
- I spent a lot of time debugging recursive directory traversal.

## Challenges I Faced

- Understanding Git's architecture
- Designing an object database
- Creating commit relationships
- Managing references and HEAD
- Restoring files from stored trees
- Handling file system edge cases

Every bug helped me understand Git a little better.

---

# 🌱 Future Improvements

Features I would like to add:

- Staging area (Index)
- Status command
- Diff command
- Merge support
- Remote repositories
- Push and Pull functionality
- Ignore file support (`.mygitignore`)
- Better commit logs
- Improved error handling

---

# 🎯 Why I Built This

I built MyGit because I wanted to learn how one of the most important developer tools actually works.

Rather than treating Git as a black box, I wanted to explore the concepts behind commits, branches, object storage, and version history.

This project helped me strengthen my Python skills and gave me a much deeper understanding of software development tools.

---

# ⭐ Note

This is a learning project and is not intended to replace Git. The goal is educational exploration and understanding how version control systems work internally.

If this project taught me anything, it's that rebuilding existing tools is one of the best ways to truly understand them.
This repository contains a minimal Git-like learning project implemented in Python.


