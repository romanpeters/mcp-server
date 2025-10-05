
import paramiko
from io import StringIO
from mcp_instance import mcp
from fastmcp.server import Context

def get_ssh_client(host: str, ctx: Context) -> paramiko.SSHClient:
    """Get an SSH client for a given host."""
    variables = ctx.fastmcp.state["variables"]
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        username=variables["ssh_user"],
        pkey=paramiko.Ed25519Key.from_private_key(StringIO(variables["ssh_private_key"])),
    )
    return client

@mcp.tool()
def run_ssh_command(host: str, command: str, ctx: Context) -> str:
    """Run a one-shot command over SSH on a given host."""
    client = None
    try:
        client = get_ssh_client(host, ctx)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        if error:
            return f"Error: {error}"
        return output
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if client:
            client.close()


@mcp.tool()
def ask_ai(prompt: str, ctx: Context) -> str:
    """Ask a one-shot question to the general AI. This AI knows about everything but is sometimes not helpful."""
    client = None
    try:
        variables = ctx.fastmcp.state["variables"]
        client = get_ssh_client(variables["ssh_host"], ctx)
        stdin, stdout, stderr = client.exec_command(f'echo $(shortcuts run "Apple AI" <<< "{prompt}")')
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        if output:
            return output
        elif error:
            return f"Error: {error}"
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if client:
            client.close()


@mcp.tool()
def ask_code_ai(prompt: str, ctx: Context) -> str:
    """Ask a one-shot question to the coding AI. This AI has studied computer science."""
    client = None
    try:
        variables = ctx.fastmcp.state["variables"]
        client = get_ssh_client(variables["ssh_host"], ctx)
        command = f'mkdir -p /tmp/ask_code_ai && cd /tmp/ask_code_ai && /opt/homebrew/bin/gemini -y -p "{prompt}. Do not edit any files, just output your answer."'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        if output:
            return output
        elif error:
            return f"Error: {error}"
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if client:
            client.close()
