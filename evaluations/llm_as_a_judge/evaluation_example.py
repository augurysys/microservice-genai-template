import json
from core.evaluators.cot_evaluator import evaluate_prompt_with_score, evaluate_semantic_distance
from core.llms.llm import LLMFactory
from utils.log_wrapper import LogWrapper

redundancy_criteria = {
    "redundancy": """
    Score 0: The recommendedSteps list has duplicate elements.
    Score 2: The recommendedSteps list has redundancy.
    Score 5: The recommendedSteps list has no redundancy and contains all the necessary steps.
    Rate the redundancy of the output on a scale of 0 to 5.
    """,
}

coherency_criteria = {
    "coherency": """
    the output should be coherent, concise, short, actionable and without low details of physics jargon
    Score 0: Less coherent, concise, short, actionable.
    Score 2: Medium coherent, concise, short, actionable.
    Score 5: Good coherent, concise, short, actionable.
    Rate the coherence of the output on a scale of 0 to 5.
    """,
}


class Item:
    def __init__(self, suggestion: str, output: str):
        self.suggestion = suggestion
        self.output = output


def evaluate_overview(input: str, output: str, suggestion: str, logger: LogWrapper) -> dict:
    # words evaluation
    # distance is the no. of different words between the suggestion and the output
    try:
        output_json = json.loads(output)
        recommended_steps = " ".join(output_json.get("recommendedSteps", []))
        symptoms = output_json.get("symptoms", "")
        timeframe = output_json.get("timeFrame", "")

        output_text = f"Symptoms:\n{symptoms}\n\nRecommended steps:\n{recommended_steps}\n\nTimeFrame:{timeframe}".strip()
    except json.JSONDecodeError:
        output_text = output

    it = Item(suggestion=suggestion, output=output_text)
    llm = LLMFactory().create_llm()

    # distance semantics evaluation
    distance = evaluate_semantic_distance(llm=llm, string1=it.output, string2=it.suggestion)
    logger.info(f"distance semantics evaluation distance score={distance['score']} reasoning={distance['reasoning']}")
    # CoT evaluation (LLM-as-a-judge)
    scores, meta = evaluate_prompt_with_score(llm=llm,
                                              criteria=[redundancy_criteria, coherency_criteria],
                                              inputs=[{"input": input, "prediction": output}])
    logger.info(f"CoT evaluation scores={scores} metadata={meta}")

    total = 0
    count = 0
    reasoning = ""
    for criterion, score in scores.items():
        total += score["avg"]
        count += 1
        reasoning += score["reasoning"]
    avg = total/count
    return {"distance": distance["score"], "judge": {
        "score": avg,
        "details": reasoning
    }}
