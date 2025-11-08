# LLM-NRP-Thesis

## Usage
### Setup
1) Create `config.env` file from `config_template.txt`(`mv config_template.txt config.env`)
2) Paste api keys

### Experiments
1) `main.py` instance(l11) is updated to experiment. Note only the 1st week is ever completed.
2) `main.py` constraint setup(l12 & 13) are correct. See `constraints_nl.txt` and `constraints_ml.txt`.
3) Run `main.py`. Final files as well as intermediate files will be generated for each LLM

### Roster construction and Analysis
1) Starting from the bottom of output, reconstruct the final roster. Be sure to start from bottom as the LLM may change future assignments. Alternatively, outsource to external llm to construct if lazy.

Output must be in format: 
```
{
  "scenario" : "n005w4",
  "week" : 0,
  "assignments" : [
  { "nurse": "Andrea", "day": "Mon", "shiftType": "Early", "skill": "Nurse" },
  { "nurse": "Stefaan", "day": "Mon", "shiftType": "Late", "skill": "HeadNurse" },
  { "nurse": "Nguyen", "day": "Mon", "shiftType": "Night", "skill": "Nurse" }
  .....
  ]
}
```

```
Output the resulting assignments in a .json file, in the format:
"assignments" : [ {
    "nurse" : "nurse_name",
    "day" : "three letter abbreviation of day",
    "shiftType" : [ time of shift ],
    "skill" : [ skill of the nurse used ]
  }]
```

2) After .json roster has been generated and put inside main directory, running `hard_only.py` requires the json file as argument, and will output all hard constraints.
3) Running `eval.sh` will automatically seek out any .json files and analyse soft constraints.

4) Move rosters into `anal_util/files/`. Running `anal_util/run.sh --dir files` outputs into 3 txt files, covering first fit, recency and role anchoring bias. I recommend running bias analysis in batches.

## Contents
anal_utils/ -> bias analysis. Please update in future work.
api_llm/ -> LLM classes for apicalls. Used in main.py.

*_Dataset/ -> json and txt formatted INRC2 datasets files. Refer to INRC2_ruleset.pdf

mischeck_eval/ -> 1 week SOFT CONSTRAINT ONLY evaluator. See mischeck_eval/README.md and eval.sh

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
