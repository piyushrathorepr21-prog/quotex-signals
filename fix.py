import pathlib, importlib

# Find and fix all pyquotex files
import pyquotex
pkg_dir = pathlib.Path(pyquotex.__file__).parent

for py_file in pkg_dir.rglob("*.py"):
    try:
        code = py_file.read_text()
        if "reason_phrase" in code:
            fixed = code.replace("home.reason_phrase", "str(home.status_code)")
            py_file.write_text(fixed)
            print(f"Fixed: {py_file.name}")
    except:
        pass

print("All files patched!")
