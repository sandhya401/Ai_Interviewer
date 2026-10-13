
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "site-packages",
    "data",
}

errors = []
checked_files = 0


def resolve_module(module_name):
    """Resolve a local dotted module name to a Python file."""
    parts = module_name.split(".")

    file_path = ROOT.joinpath(*parts).with_suffix(".py")
    package_path = ROOT.joinpath(*parts, "__init__.py")

    if file_path.is_file():
        return file_path

    if package_path.is_file():
        return package_path

    return None


def inspect_file(path):
    global checked_files
    checked_files += 1

    try:
        tree = ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path),
        )
    except (SyntaxError, UnicodeDecodeError) as exc:
        errors.append(f"SYNTAX: {path.relative_to(ROOT)}: {exc}")
        return

    definitions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level != 0 or not node.module:
                continue

            module_path = resolve_module(node.module)

            # Only check imports that point to local modules.
            if module_path is None:
                continue

            try:
                imported_tree = ast.parse(
                    module_path.read_text(encoding="utf-8")
                )
            except (SyntaxError, UnicodeDecodeError):
                continue

            exported = {
                item.name
                for item in imported_tree.body
                if isinstance(
                    item,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                )
            }
            for item in imported_tree.body:
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            exported.add(target.id)
                elif isinstance(item, ast.Import):
                    exported.update(
                        alias.asname or alias.name.split(".")[0]
                        for alias in item.names
                    )
                elif isinstance(item, ast.ImportFrom):
                    exported.update(
                        alias.asname or alias.name
                        for alias in item.names
                    )

            for alias in node.names:
                if alias.name == "*":
                    continue

                if alias.name not in exported:
                    # Permit imported/re-exported names and module attributes.
                    imported_names = {
                        alias.asname or alias.name.split(".")[0]
                        for child in imported_tree.body
                        if isinstance(child, ast.Import)
                        for alias in child.names
                    }

                    reexported_names = {
                        child.asname or child.name
                        for child in imported_tree.body
                        if isinstance(child, ast.ImportFrom)
                        for child in child.names
                    }

                    if alias.name not in imported_names | reexported_names:
                        errors.append(
                            f"IMPORT: {path.relative_to(ROOT)} imports "
                            f"{alias.name!r} from "
                            f"{node.module!r}, but it was not found "
                            f"in {module_path.relative_to(ROOT)}"
                        )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                module_path = resolve_module(alias.name)
                if module_path is None:
                    continue

                # Module existence is confirmed by resolving its path.
                # Attribute/function names cannot be checked for `import x`.

    # Avoid unused-variable warnings; definitions are useful during debugging.
    _ = definitions


def main():
    python_files = [
        path
        for path in ROOT.rglob("*.py")
        if not any(part in IGNORE_DIRS for part in path.parts)
    ]

    for path in python_files:
        inspect_file(path)

    print(f"Python files checked: {checked_files}")

    if errors:
        print(f"\nFound {len(errors)} potential problem(s):")
        for error in errors:
            print(f"- {error}")

        print(
            "\nReview each finding manually; static checks can produce "
            "false positives for dynamic imports and re-exports."
        )
        return 1

    print("No syntax errors or detected local import mismatches.")
    print("This does not prove the application is fully integrated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
