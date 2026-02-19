import requests
from typing import Any, Dict


class MLAdapter:

    def __init__(self, api_url: str, timeout: int = 10) -> None:
        self.api_url = api_url
        self.timeout = timeout

    def send_request(
        self,
        task_id: str,
        video_filename: str,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "task_id": task_id,
            "video_filename": video_filename,
        }
        response = requests.post(
            self.api_url,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()