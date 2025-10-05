import os
from contextlib import asynccontextmanager
import yaml
from fastmcp import FastMCP
from variables import resolve_variables


@asynccontextmanager
async def lifespan(server: FastMCP, variables: dict = None):
    if variables is None:
        with open("config.yml", "r") as f:
            variables = yaml.safe_load(f)

    resolved_variables = resolve_variables(variables)
    server.state = {"variables": resolved_variables}
    yield


mcp = FastMCP("Demo 🚀", lifespan=lifespan)
