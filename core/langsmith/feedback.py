

def send_feedback(run_id: str, key: str, score: float, comment: str) -> dict:
    from langsmith import Client
    client = Client()
    result = client.create_feedback(
        run_id,
        key=key,
        score=score,
        comment=comment,
    )
    return result
