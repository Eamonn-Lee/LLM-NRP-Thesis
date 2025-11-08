# LLM-NRP-Thesis

anal_utils/ -> bias analysis. Please update in future work.
api_llm/ -> LLM classes for apicalls. Used in main.py.

*_Dataset/ -> json and txt formatted INRC2 datasets files. Refer to INRC2_ruleset.pdf

mischeck_eval/ -> 1 week evaluator. See mischeck_eval/README.md and eval.sh

eval.sh -> mischeck evaluator for all 'solution'.json files in local dirr
    - Utilises mischeck_eval/ dirr

test_results -> all iterations from Thesis work.

constraints_*.txt -> problem and constraint set prompts via mathematical model(mm) and natural language(nl)

INRC2_validator.jar -> Competition validator, requires full solution details. See INRC2_ruleset.pdf(4.2). Kept for posterity.

main.py -> batch instance runner. Update Instance inside. Will only run 1st week regardless.
    - helper functions in util.py

prompt_nl.txt -> raw data insert template. Appended to end of constraints

hard_only.py -> computes and finds all hard constraint violations. Sloppy work, please update for future.

sol2his.py -> DEPRECATED. Given a solution json file and current history file, update the history file for next week to solve.

util.py -> see main.py
