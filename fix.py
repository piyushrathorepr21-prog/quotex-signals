import pyquotex.network.login as m
import re, pathlib

f = pathlib.Path(m.__file__)
code = f.read_text()
code = code.replace("home.reason_phrase", "str(home.status_code)")
f.write_text(code)
print("Fixed!")
