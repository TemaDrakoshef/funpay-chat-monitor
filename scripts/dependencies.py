import re
import tomllib

deps = (
    tomllib
    .load(open("pyproject.toml", "rb"))
    .get("project", {})
    .get("dependencies", [])
)
open("requirements.txt", "w").write(
    "\n".join(re.sub(r"\s*\(([^)]+)\)", r"\1", d) for d in deps)
)
