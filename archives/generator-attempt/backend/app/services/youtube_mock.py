import random


class YouTubeClient:
    async def get_analytics(self, video_id: str) -> dict[str, float | int]:
        rng = random.Random(video_id)
        return {
            "views": rng.randint(1000, 50000),
            "ctr": round(rng.uniform(0.04, 0.12), 4),
            "avg_view_duration": rng.randint(30, 55),
        }
