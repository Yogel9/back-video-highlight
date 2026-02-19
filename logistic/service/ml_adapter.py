import requests
from typing import Any, Dict, Optional


class MLAdapter:

    def __init__(self, api_url: str, timeout: int = 10) -> None:
        self.api_url = api_url
        self.timeout = timeout

    def send_request(
        self,
        minio_file_url: str,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # payload: Dict[str, Any] = {"file_url": minio_file_url}
        #
        # if extra_payload:
        #     payload.update(extra_payload)
        #
        # response = requests.post(
        #     self.api_url,
        #     json=payload,
        #     timeout=self.timeout,
        # )
        # response.raise_for_status()
        #
        # return response.json()

        # Заглушка для разработки/тестов
        return {
            "file_url": minio_file_url,
            "extra_payload": extra_payload or {},
            "highlights": [
                {
                    "event_type": "goal",
                    "start_time": 10,
                    "end_time": 20,
                    "confidence": 0.95,
                    "description": "Тестовый гол",
                    "highlight": "https://example.com/highlight1",
                },
                {
                    "event_type": "corner",
                    "start_time": 35,
                    "end_time": 40,
                    "confidence": 0.85,
                    "description": "Тестовый угловой",
                    "highlight": "https://example.com/highlight2",
                },
            ],
        }