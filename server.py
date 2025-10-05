from mcp_instance import mcp
import app
from fastmcp.utilities.logging import configure_logging
import yaml

if __name__ == "__main__":
    configure_logging(level="DEBUG")
    
    with open("config.yml", "r") as f:
        variables = yaml.safe_load(f)
    port = variables.get("port", 13316)

    mcp.run(transport="http", host="0.0.0.0", port=port, log_level="DEBUG")