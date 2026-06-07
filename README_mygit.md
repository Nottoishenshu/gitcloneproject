# mygit — Minimal Python Git Clone

This is a small Git-like implementation in Python using a `.mygit` directory.

## Commands

- `python mygit.py init`
  - Creates `.mygit` and initializes the object/ref database.
- `python mygit.py hash-object <file> -w`
  - Hashes a file and stores it as a blob object.
- `python mygit.py cat-file <sha1|ref>`
  - Prints an object’s contents or tree listing.
- `python mygit.py ls-tree <tree|commit>`
  - Lists a tree object or a commit’s tree.
- `python mygit.py write-tree`
  - Creates a tree object from the current directory.
- `python mygit.py commit-tree <tree> -m "message"`
  - Creates a commit object from a tree and updates `HEAD`.
- `python mygit.py commit -m "message"`
  - Creates a commit from the current directory.
- `python mygit.py log`
  - Prints commit history from `HEAD`.
- `python mygit.py branch`
  - Lists branches.
- `python mygit.py branch <name>`
  - Creates a new branch at `HEAD`.
- `python mygit.py branch -d <name>`
  - Deletes a branch.
- `python mygit.py checkout <branch|commit>`
  - Restores the working tree and switches `HEAD`.
- `python mygit.py checkout -b <name>`
  - Creates and switches to a new branch from `HEAD`.
- `python mygit.py tag`
  - Lists tags.
- `python mygit.py tag <name> [object]`
  - Creates a lightweight tag.
- `python mygit.py show-ref`
  - Shows refs and object IDs.
- `python mygit.py rev-parse --verify <name>`
  - Resolves a ref or object name to a SHA.

## Example workflow

1. Initialize:

```bash
python mygit.py init
```

2. Commit the current directory:

```bash
python mygit.py commit -m "Initial commit"
```

3. Create a new branch:

```bash
python mygit.py branch newfeature
```

4. Switch to it:

```bash
python mygit.py checkout newfeature
```

5. View commit history:

```bash
python mygit.py log
```

6. Show refs:

```bash
python mygit.py show-ref
```

## What it can do

- Store blobs, trees, and commit objects.
- Compute SHA-1 object IDs like Git.
- Keep refs in `.mygit/refs` and `HEAD`.
- Create and list branches and tags.
- Checkout commits and branches by restoring the working tree.
- Resolve object names with `rev-parse`.

This is a learning tool, not a production Git replacement.

## Demo URL

To publish a demo URL for this project, push it to GitHub and enable GitHub Pages from the `main` branch using the `/docs` folder.

Then the site will be available at:

```text
https://<YOUR_USERNAME>.github.io/<YOUR_REPO>/
```

Replace `<YOUR_USERNAME>` and `<YOUR_REPO>` with your GitHub username and repository name.
