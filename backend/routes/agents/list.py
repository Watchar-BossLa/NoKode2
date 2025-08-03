"""
API to return list of agents with status.  This file was originally located at
`api/agents/list.py`.  It should expose an endpoint that returns the list of
registered AI agents and their current health/status.
"""

from typing import List, Dict


def list_agents() -> List[Dict[str, str]]:
    """Return a list of available AI agents with their status.

    :returns: A list of dictionaries describing each agent.
    """
    # In a real implementation this would query running agents and return their
    # status (e.g. online/offline, last heartbeat).  For now we return
    # placeholder data.
    return [
        {"name": "FrontendAgent", "status": "unknown"},
        {"name": "BackendAgent", "status": "unknown"},
        {"name": "DBAgent", "status": "unknown"},
        {"name": "QAAgent", "status": "unknown"},
        {"name": "DeploymentAgent", "status": "unknown"},
    ]
