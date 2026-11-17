from rvsevo_mcp.api.client import RvsEvoClient
from rvsevo_mcp.schemas.investigation import InvestigationResult

_client = None


def _get_client() -> RvsEvoClient:
    """Create the rvsEVO client lazily so imports do not fail during startup."""
    global _client
    if _client is None:
        _client = RvsEvoClient()
    return _client


def get_job(job_id: str) -> dict:
    """
    Retrieve the operational details of a specific rvsEVO Job.

    Args:
        job_id: rvsEVO Job identifier.

    Returns:
        Job data returned by rvsEVO.
    """
    return _get_client().get_job(job_id)


def investigate_job(job_id: str) -> InvestigationResult:
    """
    Collect all available rvsEVO evidence required to investigate a Job.

    This function collects evidence only.
    It does not determine the root cause or provide diagnostic conclusions.

    Args:
        job_id: rvsEVO Job identifier.

    Returns:
        Structured evidence collected from rvsEVO.
    """
    return _get_client().investigate_job(job_id)