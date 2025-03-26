from utils.log_wrapper import LogWrapper
from langchain.evaluation import load_evaluator, EvaluatorType
from langchain_core.language_models import BaseLanguageModel


def evaluate_semantic_distance(llm: BaseLanguageModel, string1: str, string2: str):
    criterion = """Evaluate the semantic similarity between two strings on a scale of 0 to 5.
    0: The strings are completely different.
    5: The strings are semantic identical.
    """
    llm.model_name = "gpt-4"
    evaluator = load_evaluator(EvaluatorType.SCORE_STRING, llm=llm, criteria=criterion)
    result = evaluator.evaluate_strings(
        prediction=string1,
        input=string2,
        criteria=criterion
    )
    return result


def evaluate_prompt_with_score(llm: BaseLanguageModel, criteria: list[dict], inputs: list[dict]):
    # bypass lc blocker static validation
    llm.model_name = "gpt-4"
    metadata = {"total_evaluations": len(inputs)}
    scores = {}
    for message in inputs:
        message_eval_result = {}
        for criterion in criteria:
            evaluator = load_evaluator(EvaluatorType.SCORE_STRING, llm=llm, criteria=criterion)
            criterion_name = list(criterion.keys())[0]
            eval_result = evaluator.evaluate_strings(
                prediction=message["prediction"],
                criteria=criterion,
                input=message["input"],
            )
            message_eval_result[criterion_name] = eval_result["score"]
            message_eval_result[criterion_name] = eval_result["reasoning"]
            if criterion_name not in scores:
                scores[criterion_name] = {"count": 0, "avg": 0, "reasoning": ""}
            sum = scores[criterion_name]["avg"] * scores[criterion_name]["count"]
            scores[criterion_name]["count"] += 1
            scores[criterion_name]["avg"] = (sum + eval_result["score"]) / scores[criterion_name]["count"]
            scores[criterion_name]["reasoning"] += f'{eval_result["reasoning"]}. '
    return scores, metadata


def print_scores(scores: dict, metadata: dict, logger: LogWrapper):
    logger.info("========================================")
    logger.info(f"scores=[0,3,5], 5 is perfect, 0 is worst")
    logger.info("total evaluations: ", metadata["total_evaluations"])
    logger.info("----------------------------------------")
    for criterion, score in scores.items():
        logger.info(f"{criterion} score: {score['avg']}/5.0")
    logger.info("========================================")
