import argparse
import hashlib
import os
import shutil
import stat
import sys
import time
import zlib
from pathlib import Path

GIT_DIR_NAME = ".mygit"


def repo_path() -> Path:
    cwd = Path.cwd()
    dot_git_dir = cwd / GIT_DIR_NAME
    legacy_git_dir = cwd / "mygit"
    if dot_git_dir.is_dir():
        return dot_git_dir
    if legacy_git_dir.is_dir():
        return legacy_git_dir
    return dot_git_dir


def repo_exists() -> bool:
    return repo_path().is_dir()


def init_repo() -> None:
    path = repo_path()
    if path.exists():
        print(f"Repository already exists at {path}")
        return
    (path / "objects").mkdir(parents=True)
    (path / "refs" / "heads").mkdir(parents=True)
    (path / "refs" / "tags").mkdir(parents=True)
    (path / "logs").mkdir(parents=True)
    (path / "info").mkdir(parents=True)
    (path / "HEAD").write_text("refs: refs/heads/main\n")
    print(f"Initialized empty mygit repository in {path}")


def object_path(sha1: str) -> Path:
    return repo_path() / "objects" / sha1[:2] / sha1[2:]


def is_valid_sha1(value: str) -> bool:
    return len(value) == 40 and all(c in "0123456789abcdef" for c in value)


def hash_object(data: bytes, obj_type: str, write: bool = True) -> str:
    header = f"{obj_type} {len(data)}\0".encode()
    store = header + data
    sha1 = hashlib.sha1(store).hexdigest()
    if write:
        path = object_path(sha1)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(zlib.compress(store))
    return sha1


def read_object(sha1: str) -> tuple[str, bytes]:
    path = object_path(sha1)
    if not path.exists():
        raise FileNotFoundError(f"Object {sha1} does not exist")
    raw = zlib.decompress(path.read_bytes())
    nul = raw.index(b"\0")
    header = raw[:nul].decode()
    obj_type, size_str = header.split(" ", 1)
    size = int(size_str)
    data = raw[nul + 1 :]
    if size != len(data):
        raise ValueError(f"Malformed object {sha1}: bad length")
    return obj_type, data


def cat_file(sha1: str) -> None:
    obj_type, data = read_object(sha1)
    if obj_type in {"commit", "blob"}:
        sys.stdout.buffer.write(data)
    elif obj_type == "tree":
        ls_tree_object(sha1)
    else:
        print(f"Unknown object type: {obj_type}")


def parse_tree(tree_sha: str) -> list[tuple[str, str, str]]:
    obj_type, data = read_object(tree_sha)
    if obj_type == "commit":
        commit = parse_commit(data.decode())
        tree_sha = commit["tree"]
        obj_type, data = read_object(tree_sha)
    if obj_type != "tree":
        raise ValueError("Object is not a tree")
    entries: list[tuple[str, str, str]] = []
    i = 0
    while i < len(data):
        space = data.index(b" ", i)
        mode = data[i:space].decode()
        nul = data.index(b"\0", space)
        name = data[space + 1 : nul].decode()
        sha = data[nul + 1 : nul + 21].hex()
        entries.append((mode, sha, name))
        i = nul + 21
    return entries


def ls_tree_object(tree_sha: str) -> None:
    for mode, sha, name in parse_tree(tree_sha):
        print(f"{mode} {sha}\t{name}")


def is_ignored(path: Path) -> bool:
    return any(part in {GIT_DIR_NAME, "mygit"} for part in path.parts)


def write_tree(directory: Path) -> str:
    entries: list[bytes] = []
    for entry in sorted(directory.iterdir(), key=lambda p: p.name):
        if is_ignored(entry):
            continue
        if entry.is_dir():
            if entry.name == GIT_DIR_NAME:
                continue
            tree_sha = write_tree(entry)
            entries.append(b"40000 " + entry.name.encode() + b"\0" + bytes.fromhex(tree_sha))
        elif entry.is_file():
            data = entry.read_bytes()
            sha1 = hash_object(data, "blob")
            entries.append(b"100644 " + entry.name.encode() + b"\0" + bytes.fromhex(sha1))
    tree_data = b"".join(entries)
    return hash_object(tree_data, "tree")


def get_ref(name: str) -> str | None:
    ref_path = repo_path() / name
    if ref_path.exists():
        return ref_path.read_text().strip()
    return None


def update_ref(name: str, sha1: str) -> None:
    ref_path = repo_path() / name
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_path.write_text(sha1 + "\n")


def get_head_content() -> str:
    return (repo_path() / "HEAD").read_text().strip()


def resolve_head() -> str | None:
    content = get_head_content()
    if content.startswith("refs:"):
        ref = content.split(None, 1)[1]
        return get_ref(ref)
    return content


def get_current_branch() -> str | None:
    content = get_head_content()
    if content.startswith("refs:"):
        ref = content.split(None, 1)[1]
        if ref.startswith("refs/heads/"):
            return ref[len("refs/heads/") :]
    return None


def set_head_ref(ref: str) -> None:
    (repo_path() / "HEAD").write_text(f"refs: {ref}\n")


def set_head_detached(sha1: str) -> None:
    (repo_path() / "HEAD").write_text(f"{sha1}\n")


def list_refs(prefix: str = "") -> list[tuple[str, str]]:
    base = repo_path() / "refs" / prefix
    refs: list[tuple[str, str]] = []
    if not base.exists():
        return refs
    for path in sorted(base.rglob("*")):
        if path.is_file():
            rel = path.relative_to(repo_path()).as_posix()
            refs.append((rel, path.read_text().strip()))
    return refs


def resolve_object(name: str) -> str:
    if name == "HEAD":
        value = resolve_head()
        if value:
            return value
        raise ValueError("HEAD is not valid")
    if name.startswith("refs/"):
        value = get_ref(name)
        if value:
            return value
        raise ValueError(f"Ref '{name}' not found")
    branch_ref = get_ref(f"refs/heads/{name}")
    if branch_ref:
        return branch_ref
    tag_ref = get_ref(f"refs/tags/{name}")
    if tag_ref:
        return tag_ref
    if is_valid_sha1(name) and object_path(name).exists():
        return name
    if len(name) >= 4:
        candidates: list[str] = []
        prefix = name.lower()
        base = repo_path() / "objects"
        if len(prefix) <= 2:
            object_dirs = [d for d in base.iterdir() if d.is_dir() and d.name.startswith(prefix)]
        else:
            object_dirs = [base / prefix[:2]]
        for obj_dir in object_dirs:
            if not obj_dir.exists():
                continue
            for file in obj_dir.iterdir():
                sha = obj_dir.name + file.name
                if sha.startswith(prefix):
                    candidates.append(sha)
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise ValueError(f"Ambiguous object name '{name}'")
    raise ValueError(f"Object or ref '{name}' not found")


def commit_tree(tree_sha: str, message: str, author: str, parent: str | None = None) -> str:
    lines = [f"tree {tree_sha}"]
    if parent:
        lines.append(f"parent {parent}")
    timestamp = int(time.time())
    timezone = time.strftime("%z")
    lines.append(f"author {author} {timestamp} {timezone}")
    lines.append(f"committer {author} {timestamp} {timezone}")
    lines.append("")
    lines.append(message)
    body = "\n".join(lines).encode()
    commit_sha = hash_object(body, "commit")
    head = get_head_content()
    if head.startswith("refs:"):
        ref_name = head.split(None, 1)[1]
        update_ref(ref_name, commit_sha)
    return commit_sha


def parse_commit(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if line == "":
            break
        key, value = line.split(" ", 1)
        result[key] = value
    return result


def get_commit(sha1: str) -> dict[str, str]:
    obj_type, data = read_object(sha1)
    if obj_type != "commit":
        raise ValueError("Object is not a commit")
    return parse_commit(data.decode())


def log_commits(start: str | None) -> None:
    if start is None:
        print("No commits yet")
        return
    sha = start
    while sha:
        commit = get_commit(sha)
        print(f"commit {sha}")
        if "author" in commit:
            print(f"Author: {commit['author']}")
        print()
        print(commit.get("message", ""))
        print()
        sha = commit.get("parent")


def clear_working_directory(directory: Path) -> None:
    for entry in sorted(directory.iterdir(), key=lambda p: p.name, reverse=True):
        if is_ignored(entry):
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def checkout_tree(tree_sha: str, directory: Path) -> None:
    clear_working_directory(directory)
    for mode, sha, name in parse_tree(tree_sha):
        path = directory / name
        if mode == "40000":
            path.mkdir(parents=True, exist_ok=True)
            checkout_tree(sha, path)
        else:
            obj_type, data = read_object(sha)
            if obj_type != "blob":
                raise ValueError("Tree contains non-blob entry")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if mode == "100755":
                path.chmod(path.stat().st_mode | stat.S_IEXEC)


def create_branch(name: str, start_point: str | None = None) -> None:
    start_sha = resolve_object(start_point) if start_point else resolve_head()
    if not start_sha:
        raise ValueError("No starting point for branch")
    if get_ref(f"refs/heads/{name}"):
        raise ValueError(f"Branch '{name}' already exists")
    update_ref(f"refs/heads/{name}", start_sha)


def delete_branch(name: str) -> None:
    ref = repo_path() / "refs" / "heads" / name
    if not ref.exists():
        raise ValueError(f"Branch '{name}' does not exist")
    ref.unlink()


def checkout_target(target: str, new_branch: bool = False) -> None:
    if new_branch:
        if get_ref(f"refs/heads/{target}"):
            raise ValueError(f"Branch '{target}' already exists")
        head_commit = resolve_head()
        if not head_commit:
            raise ValueError("Cannot create branch from empty HEAD")
        update_ref(f"refs/heads/{target}", head_commit)
        set_head_ref(f"refs/heads/{target}")
        checkout_tree(parse_commit(read_object(head_commit)[1].decode())["tree"], Path.cwd())
        return
    if get_ref(f"refs/heads/{target}"):
        sha = resolve_object(f"refs/heads/{target}")
        set_head_ref(f"refs/heads/{target}")
    else:
        sha = resolve_object(target)
        set_head_detached(sha)
    commit = get_commit(sha)
    checkout_tree(commit["tree"], Path.cwd())


def tag_object(name: str, object_name: str | None = None) -> None:
    target = resolve_object(object_name) if object_name else resolve_head()
    if not target:
        raise ValueError("No object to tag")
    update_ref(f"refs/tags/{name}", target)


def list_branches() -> None:
    current = get_current_branch()
    for _, sha in list_refs("heads"):
        branch_name = _.replace("refs/heads/", "")
        prefix = "* " if branch_name == current else "  "
        print(f"{prefix}{branch_name}")


def list_tags() -> None:
    for _, sha in list_refs("tags"):
        tag_name = _.replace("refs/tags/", "")
        print(f"{tag_name}")


def show_refs() -> None:
    for ref, sha in list_refs("heads") + list_refs("tags"):
        print(f"{sha} {ref}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal Python Git-like tool")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize a .mygit repository")

    hash_parser = subparsers.add_parser("hash-object", help="Hash object and optionally write")
    hash_parser.add_argument("path", help="File path to hash")
    hash_parser.add_argument("--type", choices=["blob", "tree", "commit"], default="blob")
    hash_parser.add_argument("-w", action="store_true", help="Write object to the database")

    cat_parser = subparsers.add_parser("cat-file", help="Print contents of an object")
    cat_parser.add_argument("sha1", help="Object SHA1 or ref name")

    ls_parser = subparsers.add_parser("ls-tree", help="List tree contents")
    ls_parser.add_argument("tree", help="Tree SHA1 or commit ref")

    write_tree_parser = subparsers.add_parser("write-tree", help="Write current directory to a tree object")
    write_tree_parser.add_argument("path", nargs="?", default=".")

    commit_parser = subparsers.add_parser("commit-tree", help="Commit a tree object")
    commit_parser.add_argument("tree", help="Tree SHA1")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.add_argument("--author", default="You <you@example.com>", help="Author name and email")
    commit_parser.add_argument("--parent", help="Parent commit SHA1")

    commit_root_parser = subparsers.add_parser("commit", help="Commit the current directory")
    commit_root_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_root_parser.add_argument("--author", default="You <you@example.com>", help="Author name and email")

    subparsers.add_parser("log", help="Show commit log")

    branch_parser = subparsers.add_parser("branch", help="List, create, or delete branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name")
    branch_parser.add_argument("-d", "--delete", action="store_true", help="Delete a branch")

    checkout_parser = subparsers.add_parser("checkout", help="Switch branches or restore a commit")
    checkout_parser.add_argument("-b", "--branch", action="store_true", help="Create and switch to a new branch")
    checkout_parser.add_argument("target", help="Branch or commit to checkout")

    tag_parser = subparsers.add_parser("tag", help="List or create tags")
    tag_parser.add_argument("name", nargs="?", help="Tag name")
    tag_parser.add_argument("object", nargs="?", help="Object SHA1 or ref to tag")

    subparsers.add_parser("show-ref", help="List refs and their object IDs")

    rev_parser = subparsers.add_parser("rev-parse", help="Resolve an object name")
    rev_parser.add_argument("--verify", action="store_true", help="Verify the name resolves")
    rev_parser.add_argument("name", help="Object name or ref")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "init":
        init_repo()
        return
    if not repo_exists():
        print("Error: repository not initialized. Run 'python mygit.py init' first.")
        return

    try:
        if args.command == "hash-object":
            data = Path(args.path).read_bytes()
            sha1 = hash_object(data, args.type, write=args.w)
            print(sha1)
        elif args.command == "cat-file":
            sha = resolve_object(args.sha1)
            cat_file(sha)
        elif args.command == "ls-tree":
            sha = resolve_object(args.tree)
            ls_tree_object(sha)
        elif args.command == "write-tree":
            tree_sha = write_tree(Path(args.path))
            print(tree_sha)
        elif args.command == "commit-tree":
            parent = resolve_object(args.parent) if args.parent else resolve_head()
            commit_sha = commit_tree(args.tree, args.message, args.author, parent)
            print(commit_sha)
        elif args.command == "commit":
            tree_sha = write_tree(Path.cwd())
            commit_sha = commit_tree(tree_sha, args.message, args.author, resolve_head())
            print(commit_sha)
        elif args.command == "log":
            start = resolve_head()
            log_commits(start)
        elif args.command == "branch":
            if args.name:
                if args.delete:
                    delete_branch(args.name)
                else:
                    create_branch(args.name)
            else:
                list_branches()
        elif args.command == "checkout":
            checkout_target(args.target, args.branch)
        elif args.command == "tag":
            if args.name:
                tag_object(args.name, args.object)
            else:
                list_tags()
        elif args.command == "show-ref":
            show_refs()
        elif args.command == "rev-parse":
            sha = resolve_object(args.name)
            if args.verify:
                print(sha)
            else:
                print(sha)
        else:
            print("No command specified. Use -h for help.")
    except Exception as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
