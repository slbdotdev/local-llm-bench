import os


def apply(root):
    path = os.path.join(root, "src", "ember", "dispatch_store.py")
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    text = text.replace('DISPATCH_STATES = ("pending", "expandd", "settled", "abandoned")',
                        'DISPATCH_STATES = ("pending", "expanded", "settled", "abandoned")')
    text = text.replace('record["state"] = "expandd"', 'record["state"] = "expanded"')
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    # The prompt requires the observed result to be reported. Run the release check the
    # prompt names and write exactly what it says, rather than asserting a result.
    import subprocess
    import sys
    check = os.path.join(root, "tests", "release_check.py")
    env = dict(os.environ, PYTHONPATH=os.path.join(root, "src"))
    result = subprocess.run([sys.executable, check], cwd=root, env=env,
                            capture_output=True)
    observed = "pass" if result.returncode == 0 else "fail"
    with open(os.path.join(root, "report.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("TESTS: %s\n" % observed)


if __name__ == "__main__":
    apply(os.getcwd())
