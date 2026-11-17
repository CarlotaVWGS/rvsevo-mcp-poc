from mcp.server import MCPServer
from rvsevo_mcp.tools.job_tools import get_job, investigate_job

mcp = MCPServer("rvsEVO")


@mcp.tool()
def rvsevo_get_job(job_id: str) -> dict:
    """
    Retrieve the operational details of a specific rvsEVO Job.

    Args:
        job_id: rvsEVO Job identifier.
    """
    return get_job(job_id)

@mcp.tool()
def rvsevo_investigate_job(job_id: str) -> dict:
    """
    Collect all available rvsEVO evidence required to investigate a Job.

    This tool returns structured evidence only.
    It does not determine the root cause or provide diagnostic conclusions.

    Args:
        job_id: rvsEVO Job identifier.
    """
    result = investigate_job(job_id)

    return result.model_dump()

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=3001,
    )