import subprocess


def run_cmd(cmd_str: str):
    """
    Function that executes a given command-line as a string and captures stdout, stderr, and the return code.

    Args:
        cmd_str: A string containing the command to be executed.

    Returns:
        A tuple containing stdout, stderr, and the return code of the executed command.
    """
    result = subprocess.run(
        cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout = result.stdout.decode("utf-8").strip() or "No Output"
    stderr = result.stderr.decode("utf-8").strip() or "No Output"

    return stdout, stderr, result.returncode

