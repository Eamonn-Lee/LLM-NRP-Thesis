import openai
import json

openai.api_key = "your-api-key-here"

class ScenarioProcessingAgent:
    """scenario LLM reads, processes scenario and produces ruleset, Handles all constraints inside sce file"""
    
    def __init__(self, model="gpt-4"):
        self.model = model

    def process_scenario(self, data):
        prompt = f"""
        You are an expert in the International Nurse Rostering Competition (INRC2).
        Analyze the following JSON data representing a nurse rostering problem.
        Extract key constraints, shift types, and staffing requirements.

        -> blach blah blah, here is some info about how to actually read the sce file

        Data:
        {json.dumps(data, indent=4)}

        Summary:
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()


class ScheduleGenerationAgent:
    """
    handles assignment, but also constraint parsing of:
        weekly/daily min/opt role requirements -> 3 variables!
        preference user off?
        history issues
        global assignment numbers -> assignemnt per nurses
    
    """

    def __init__(self, model="gpt-4"):
        self.model = model

    def generate_schedule(self, sce_constraints, week_history, assign_stats, week_req):
        prompt = f"""
        Based on the following nurse rostering problem constraint ruleset, generate an initial weeks schedule.
        Ensure you follow the constraints within the provided constraint rulset.

        ->blah blah, here's some instructions about how to process/read a week file

        Ruleset:
        {sce_constraints}

        Previous weeks assignments:
        {week_history}

        Current assignements:
        {assign_stats}

        Data:
        {week_req}

        Initial Schedule:
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()


class OptimizationAgent:
    """
    Optimize schedule
        additional avenue to explore?
    """

    def __init__(self, model="gpt-4"):
        self.model = model

    def optimize_schedule(self, sce_constraints,init_schedule):
        prompt = f"""
        You are an optimization expert. Improve the following nurse schedule 
        by minimizing constraint violations and maximizing fairness.

        Scenario:
        {sce_constraints}

        Current Schedule:
        {init_schedule}

        Optimized Schedule:
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()
    

class OutputAgent:
    """
    Parse output into JSON
        or better to force it to use json from the getgo?
    """

    def __init__(self, model="gpt-4"):
        self.model = model

    def optimize_schedule(self, init_schedule):
        #double quote to escape f-string {}
        #need to insert shift types and skill types based on sce file
        prompt = f"""
        Given this assignment of nurses to shifts, Output the resulting assignments in a .json file, in the format:
        "assignments" : [ {{
            "nurse" : "nurse_name",
            "day" : "three letter abbreviation of day",
            "shiftType" : {["Early", "Late", "Night"]},
            "skill" : {["Nurse", "HeadNurse"]}
        }}]

        Current Schedule:
        {init_schedule}

        Parsed Output:
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    # best way to parse inrc data?
    inrc2_data = {}

    # Instantiate agents
    reader_agent = ScenarioProcessingAgent()
    scheduler_agent = ScheduleGenerationAgent()
    optimizer_agent = OptimizationAgent()
    output_agent = OutputAgent()

    scenario_summary = reader_agent.process_scenario(inrc2_data)
    print("\n--- Scenario ruleset ---\n", scenario_summary)

    for week in weeks:  #replace with weekly data
        feasible_schedule = scheduler_agent.generate_schedule(scenario_summary, week_history, history_file, week_data)
        print("\n--- init sched ---\n", feasible_schedule)

        optimized_schedule = optimizer_agent.optimize_schedule(scenario_summary, feasible_schedule)
        print("\n--- opt sched ---\n", optimized_schedule)

        parsed_schedule = output_agent.optimize_schedule(scenario_summary, optimized_schedule)
        print("\n--- fin out ---\n", optimized_schedule)
        # -> write out to sol file
