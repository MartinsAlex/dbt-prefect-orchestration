from prefect import flow, task, get_run_logger
import utils
import shutil
import json
from graphlib import TopologicalSorter
import os


class DBTCommandError(Exception):
    def __init__(self, message="DBT command execution failed"):
        super().__init__(message)

DBT_EXE = shutil.which("dbt") or "dbt"

@task(task_run_name="{model_name}")
def dbt_task_run(model_name: str):
    logger = get_run_logger()
    dbt_command = f"{DBT_EXE} run --select {model_name}"
    logger.info(f"RUNNING DBT COMMAND: {dbt_command}")

    stdout, stderr, returncode = utils.run_cmd(dbt_command)

    if returncode != 0:
        error_message = f"DBT COMMAND FAILED: {stderr}"
        logger.error(error_message)
        raise DBTCommandError(error_message)
    else:
        logger.info(stdout)

@flow(log_prints=True)
def dbt_flow_run(run_scope: str = "project"):

    print(os.getcwd())

    if run_scope != 'project':
        dbt_select_command = f"--select transformation/{run_scope}"
    else:
        dbt_select_command = ""

    dbt_ls_command = f"{DBT_EXE} ls {dbt_select_command} --resource-type=model --output json" #  --output-keys 'resource_type name alias depends_on'
    print(f"Executing command:\n{dbt_ls_command}")
    dbt_ls_result_raw, stderr, returncode = utils.run_cmd(dbt_ls_command)
    dbt_ls_result_raw = dbt_ls_result_raw.split("\n")

    dbt_ls_result = [json.loads(line.strip()) for line in dbt_ls_result_raw if line.strip().startswith('{') and line.strip().endswith('}')]
    #print(f"Command result:\n{dbt_ls_result}")

    # Preparing the graph for topological sorting
    graph = {}
    for model in dbt_ls_result:
        # Using model unique_id as the key, and its dependencies as the values
        dependencies = [dep.split('.')[-1] for dep in model['depends_on']['nodes'] if dep.startswith('model.')]
        graph[model['unique_id']] = set(dependencies)
    
    # Creating an instance of TopologicalSorter with the graph
    ts = TopologicalSorter(graph)

    reordered_models = []

    for model_id in ts.static_order():
        model = next((m for m in dbt_ls_result if m['unique_id'] == model_id), None)
        reordered_models.append(model)

    # Mapping of model unique_ids to their task submissions (futures)
    model_tasks_map = {}
    # Temporary mapping to hold dependencies for each model
    dependency_map = {}

    # Identify dependencies for each model
    for model in [model for model in reordered_models if model is not None]:
        # Initialize an empty list for dependencies
        dependency_map[model['unique_id']] = []
        for dep_unique_id in model['depends_on']['nodes']:
            if dep_unique_id.startswith('model.'):
                dependency_map[model['unique_id']].append(dep_unique_id)

    # Submit tasks with dependencies
    for model in [model for model in reordered_models if model is not None]:
        unique_id = model['unique_id']
        wait_for_tasks = [model_tasks_map[dep_id] for dep_id in dependency_map[unique_id] if dep_id in model_tasks_map]
        # Submit each task exactly once with the correct wait_for dependencies
        model_tasks_map[unique_id] = dbt_task_run.submit(model_name=model['name'], wait_for=wait_for_tasks)


if __name__ == "__main__":
    dbt_flow_run.serve(
        name="dbt-run", 
    )
