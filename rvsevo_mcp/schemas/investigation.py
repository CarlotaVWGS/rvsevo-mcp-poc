from typing import Optional

from pydantic import BaseModel


class JobEvidence(BaseModel):
    """Operational evidence retrieved for the Job being investigated."""

    id: str
    status: str
    type: Optional[str] = None
    direction: Optional[str] = None

    originator: Optional[str] = None
    destination: Optional[str] = None
    vdsn: Optional[str] = None

    transmissionStartTime: Optional[str] = None
    transmissionEndTime: Optional[str] = None
    lastChange: Optional[str] = None

    retryCount: Optional[int] = None

    errorNumber: Optional[str] = None
    nerpReasonCode: Optional[str] = None
    nerpReasonText: Optional[str] = None
    nerpCreatorOdetteId: Optional[str] = None
    erpState: Optional[str] = None

class HistoricalJobEvidence(BaseModel):
    """Relevant evidence from another Job with the same VDSN."""

    id: str
    status: str

    destination: Optional[str] = None
    transmissionStartTime: Optional[str] = None

    nerpReasonCode: Optional[str] = None


class VdsnHistoryEvidence(BaseModel):
    """Transmission history for the VDSN associated with the investigated Job."""

    vdsn: str

    totalJobs: int
    successfulJobs: int
    failedJobs: int

    jobs: list[HistoricalJobEvidence]

class MonitorEventEvidence(BaseModel):
    """A normalized rvsEVO monitor event related to the investigated Job."""

    timestamp: str

    level: Optional[str] = None
    component: Optional[str] = None
    event: Optional[str] = None
    session: Optional[str] = None
    station: Optional[str] = None
    jobId: Optional[str] = None
    message: Optional[str] = None


class MonitorEvidence(BaseModel):
    """Monitor evidence collected for the investigated Job."""

    file: Optional[str] = None
    eventCount: int = 0

    events: list[MonitorEventEvidence]

class InvestigationResult(BaseModel):
    """
    Complete evidence package collected for an rvsEVO Job investigation.

    This model contains evidence only.
    It must not contain diagnostic conclusions or root-cause assumptions.
    """

    job: JobEvidence

    vdsn_history: Optional[VdsnHistoryEvidence] = None

    monitor: Optional[MonitorEvidence] = None

    limitations: list[str] = []