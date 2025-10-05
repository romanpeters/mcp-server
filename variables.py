import os
import subprocess
from dotenv import load_dotenv

def resolve_variables(variables: dict) -> dict:
    """
    Resolves variables that are defined as environment variables.

    Args:
        variables: A dictionary of variables.

    Returns:
        A dictionary with the environment variables resolved.
    """
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    if value.startswith("$(") and value.endswith(")"):
                        command = value[2:-1]
                        try:
                            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
                            os.environ[key] = result.stdout.strip()
                        except subprocess.CalledProcessError as e:
                            print(f"Error executing command for {key}: {e.stderr}")
                    else:
                        os.environ[key] = value

    load_dotenv()
    resolved_variables = {}
    for key, value in variables.items():
        if isinstance(value, str) and value.startswith("env:"):
            env_var_name = value.split("env:", 1)[1]
            resolved_variables[key] = os.getenv(env_var_name)
        else:
            resolved_variables[key] = value
    return resolved_variables
