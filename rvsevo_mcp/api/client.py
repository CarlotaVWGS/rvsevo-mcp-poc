import base64
import json
import ssl
import urllib.request
import urllib.parse
from rvsevo_mcp.schemas.investigation import InvestigationResult

from rvsevo_mcp.core.config import (
    RVSEVO_BASE_URL,
    RVSEVO_USERNAME,
    RVSEVO_PASSWORD,
    require_rvs_evo_config,
)


class RvsEvoClient:
    """Client responsible for communication with the rvsEVO REST API."""

    def __init__(self):
        require_rvs_evo_config()

        self.base_url = RVSEVO_BASE_URL
        self.username = RVSEVO_USERNAME
        self.password = RVSEVO_PASSWORD

        # PoC only: certificate validation will be handled properly later.
        self.ssl_context = ssl._create_unverified_context()

    def _authenticate(self) -> str:
        """Authenticate against rvsEVO and return the Bearer token."""

        credentials = f"{self.username}:{self.password}"

        basic_auth = base64.b64encode(
            credentials.encode("ascii")
        ).decode("ascii")

        request = urllib.request.Request(
            f"{self.base_url}/rvs/sessions",
            data=b"{}",
            method="POST",
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(
            request,
            context= self.ssl_context,
        ) as response:
            token = response.headers.get("Authorization")

        if not token:
            raise RuntimeError(
                "rvsEVO authentication succeeded but no Authorization token was returned."
            )

        return token

    def get_job(self, job_id: str) -> dict:
        """Retrieve the details of a specific rvsEVO Job."""

        token = self._authenticate()

        request = urllib.request.Request(
            f"{self.base_url}/rvs/api/job/{job_id}",
            method="GET",
            headers={
                "Authorization": token,
            },
        )

        with urllib.request.urlopen(
            request,
            context=self.ssl_context,
        ) as response:
            job = json.loads(
                response.read().decode("utf-8")
            )

        return job

    def search_jobs_by_vdsn(self, vdsn: str) -> dict:
        """Retrieve rvsEVO Jobs associated with a specific VDSN."""

        token = self._authenticate()

        encoded_vdsn = urllib.parse.quote(vdsn, safe="")

        request = urllib.request.Request(
            f"{self.base_url}/rvs/api/jobs?filter=vdsn:{encoded_vdsn}",
            method="GET",
            headers={
                "Authorization": token,
            },
        )

        with urllib.request.urlopen(
            request,
            context=self.ssl_context,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        return data

    def get_vdsn_history(self, vdsn: str) -> dict:
        """Retrieve and normalize the Job history for a specific VDSN."""

        data = self.search_jobs_by_vdsn(vdsn)

        jobs = []

        for row in data.get("rows", []):
            job_id = row[0]

            # Retrieve full Job details
            job_detail = self.get_job(job_id)

            jobs.append({
                "id": job_detail.get("id"),
                "status": job_detail.get("status"),
                "destination": job_detail.get("destination"),
                "transmissionStartTime": job_detail.get("transmissionStartTime"),
                "nerpReasonCode": job_detail.get("nerpReasonCode"),
            })

        successful_jobs = sum(
            1 for job in jobs
            if job["status"] == "ENDED"
        )

        failed_jobs = sum(
            1 for job in jobs
            if job["status"] and job["status"].startswith("FAILED")
        )

        return {
            "vdsn": vdsn,
            "totalJobs": len(jobs),
            "successfulJobs": successful_jobs,
            "failedJobs": failed_jobs,
            "jobs": jobs,
        }

    def get_monitor(self, transmission_start_time: str) -> dict:
        """Retrieve the rvsEVO monitor file for the Job transmission date."""

        token = self._authenticate()

        date = transmission_start_time[:10]
        monitor_file = f"monitor.log.{date}.1"

        request = urllib.request.Request(
            f"{self.base_url}/rvs/api/monitor/{monitor_file}",
            method="GET",
            headers={
                "Authorization": token,
            },
        )

        with urllib.request.urlopen(
            request,
            context=self.ssl_context,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        return {
            "file": monitor_file,
            "data": data,
        }

    def get_job_monitor(
        self,
        job_id: str,
        transmission_start_time: str,
    ) -> dict:
        """Retrieve and normalize monitor events for a specific rvsEVO Job."""

        monitor = self.get_monitor(transmission_start_time)

        rows = monitor["data"].get("rows", [])

        events = []

        for row in rows:
            if job_id not in [str(value) for value in row]:
                continue

            events.append({
                "timestamp": row[1],
                "level": row[2],
                "component": row[3],
                "event": row[4],
                "session": row[5],
                "station": row[6],
                "jobId": row[7],
                "message": row[8],
            })

        return {
            "file": monitor["file"],
            "eventCount": len(events),
            "events": events,
        }

    def investigate_job(self, job_id: str) -> InvestigationResult:
        """Collect all available rvsEVO evidence for a Job investigation."""

        limitations = []

        # 1. Retrieve the Job
        job = self.get_job(job_id)

        # Keep only the fields required by the investigation schema
        job_evidence = {
            "id": job.get("id"),
            "status": job.get("status"),
            "type": job.get("type"),
            "direction": job.get("direction"),
            "originator": job.get("originator"),
            "destination": job.get("destination"),
            "vdsn": job.get("vdsn"),
            "transmissionStartTime": job.get("transmissionStartTime"),
            "transmissionEndTime": job.get("transmissionEndTime"),
            "lastChange": job.get("lastChange"),
            "retryCount": job.get("retryCount"),
            "errorNumber": job.get("errorNumber"),
            "nerpReasonCode": job.get("nerpReasonCode"),
            "nerpReasonText": job.get("nerpReasonText"),
            "nerpCreatorOdetteId": job.get("nerpCreatorOdetteId"),
            "erpState": job.get("erpState"),
        }

        # 2. Retrieve VDSN history
        vdsn_history = None

        if job.get("vdsn"):
            try:
                vdsn_history = self.get_vdsn_history(job["vdsn"])
            except Exception:
                limitations.append(
                    "VDSN history could not be retrieved."
                )
        else:
            limitations.append(
                "The Job does not contain a VDSN."
            )

        # 3. Retrieve monitor evidence
        monitor = None

        if job.get("transmissionStartTime"):
            try:
                monitor = self.get_job_monitor(
                    job_id,
                    job["transmissionStartTime"],
                )
            except Exception:
                limitations.append(
                    "Monitor evidence could not be retrieved."
                )
        else:
            limitations.append(
                "The Job does not contain transmissionStartTime."
            )

        return InvestigationResult(
            job=job_evidence,
            vdsn_history=vdsn_history,
            monitor=monitor,
            limitations=limitations,
        )