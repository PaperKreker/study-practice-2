import os
import random

from locust import HttpUser, between, task
from locust.exception import StopUser


SEARCH_QUERIES = [
    "университет",
    "поиск документов",
    "Elasticsearch",
    "молекулярная физика",
    "нанооптика",
    "лекция",
    "оптические свойства",
    "квантовая механика",
    "эксперимент",
    "формула",
]


class SearchUser(HttpUser):
    """Authenticated user repeatedly requesting the first search page."""

    wait_time = between(0.2, 1.0)

    def on_start(self) -> None:
        self.token = os.getenv("QA_ACCESS_TOKEN")
        if self.token:
            return

        credentials = {
            "username": os.getenv("QA_USERNAME", "qa-load"),
            "password": os.getenv("QA_PASSWORD", "qa-load-password"),
        }
        with self.client.post(
            "/api/v1/users/login",
            json=credentials,
            name="/api/v1/users/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    "Set QA_ACCESS_TOKEN or create the configured QA load user"
                )
                raise StopUser()

            try:
                self.token = response.json()["access_token"]
            except (KeyError, ValueError):
                response.failure("Login response does not contain access_token")
                raise StopUser()

    @task
    def search(self) -> None:
        query = random.choice(SEARCH_QUERIES)
        with self.client.get(
            "/api/v1/search",
            params={"q": query, "page": 1, "size": 10},
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/v1/search",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected HTTP {response.status_code}")
                return

            try:
                payload = response.json()
            except ValueError:
                response.failure("Search response is not JSON")
                return

            if not isinstance(payload, dict) or not isinstance(
                payload.get("items"), list
            ):
                response.failure("Search response does not match SearchResponse")
