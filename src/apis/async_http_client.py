import json


class AsyncHttpClient:
    @staticmethod
    def get_commit_from_gitlab_api() -> str:
        commits = [
            {
                "id": "f5a1d9f7-a5e2-4d7d-b1c8-b7c42f93c8b8",
                "short_id": "f5a1d9f7",
                "created_at": "2026-08-02T14:32:18",
                "parent_ids": [
                    "c8a72dbe-93c1-41a9-b3b6-2a4d9e2c3f58"
                ],
                "title": "Implement column storage",
                "message": "Implement column storage",

                "author_name": "Eduard Ivanov",
                "author_email": "eduard@example.com",
                "authored_date": "2026-08-02T14:30:41",

                "committer_name": "Eduard Ivanov",
                "committer_email": "eduard@example.com",
                "committed_date": "2026-08-02T14:32:18",

                "web_url": "https://gitlab.example.com/commit/1",

                "trailers": {},
                "extended_trailers": {},
            }
        ]

        return json.dumps(commits)