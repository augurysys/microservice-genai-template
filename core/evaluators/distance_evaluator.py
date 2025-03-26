import Levenshtein
from pydantic import BaseModel

from utils.log_wrapper import LogWrapper


class Item(BaseModel):
    suggestion: str
    output: str


def evaluate_distance(item: Item):
    delta = Levenshtein.distance(item.suggestion, item.output)
    return delta


def evaluate_distance_bulk(items: [Item], logger: LogWrapper):
    deltas = []
    high_delta_docs = []
    medium_delta_docs = []
    high_delta_threshold = 120
    medium_delta_threshold = 80
    total = 0

    for item in items:
        suggestion = item.Suggestion

        if not suggestion or suggestion == "":
            logger.info("skip no suggestion")
            continue

        output_text = item.Output

        if not output_text or output_text == "":
            logger.info("skip no output_text")
            continue

        delta = Levenshtein.distance(suggestion, output_text)
        deltas.append(delta)
        total += 1

        if delta > high_delta_threshold:
            high_delta_docs.append(item)
        if delta > medium_delta_threshold:
            medium_delta_docs.append(item)

    avg_delta = sum(deltas) / len(deltas) if deltas else 0

    logger.info(f"High delta threshold= ~{high_delta_threshold / 8} < words are different")
    logger.info(f"Medium delta threshold= ~{medium_delta_threshold / 8} < words are different")
    logger.info(f"In average ~{avg_delta / 8} words are different:")
    logger.info(f"High delta percentage: {(len(high_delta_docs) / total) * 100.0}%", )
    return {"avg_delta_items": avg_delta, "high_delta_items": high_delta_docs, "medium_delta_items": medium_delta_docs}
