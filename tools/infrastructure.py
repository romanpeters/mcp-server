import datetime
import boto3
import yaml
import json
import requests
from mcp_instance import mcp
from fastmcp.server import Context


def get_storage_client(ctx: Context):
    variables = ctx.fastmcp.state["variables"]
    return boto3.client(
        "s3",
        endpoint_url=variables["aws_endpoint"],
        aws_access_key_id=variables["aws_access_key_id"],
        aws_secret_access_key=variables["aws_secret_access_key"],
    )


@mcp.tool()
def get_hosts(ctx: Context) -> dict:
    """List all hosts in the homelab, the DNS name under which they are reachable, their IP, MAC address, VLAN tag and OS (if they are managed)

    Primary info: name, ip
    Secondary info: dns, mac, vlan, os
    """
    storage_client = get_storage_client(ctx)
    bucket = ctx.fastmcp.state["variables"]["aws_bucket"]
    dns_domain = ctx.fastmcp.state["variables"]["dns_domain"]
    obj = storage_client.get_object(Bucket=bucket, Key="hosts.yml")
    yaml_content = obj["Body"].read().decode("utf-8")
    hosts = yaml.safe_load(yaml_content)
    for name, data in hosts.items():
        data["dns"] = f"{name}.{dns_domain}"
    return hosts


@mcp.tool()
def get_services(ctx: Context) -> dict:
    """List all services in the homelab and on which host they are running, the URL under which they are reachable, whether they are running as a docker container, their local port on the host, whether they use SSL locally
    
    Primary info: name, url
    Secondary info: docker, host, port, ssl
    """
    storage_client = get_storage_client(ctx)
    bucket = ctx.fastmcp.state["variables"]["aws_bucket"]
    domain_name = ctx.fastmcp.state["variables"]["domain_name"]
    obj = storage_client.get_object(Bucket=bucket, Key="services.yml")
    yaml_content = obj["Body"].read().decode("utf-8")
    services = yaml.safe_load(yaml_content)
    for name, service in services.items():
        service["url"] = f"https://{name}.{domain_name}"
    return services
