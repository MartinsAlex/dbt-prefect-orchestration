from prefect import flow, task, get_run_logger
import utils
import shutil
import json
from graphlib import TopologicalSorter
import os
import re
from prefect.task_runners import ConcurrentTaskRunner
import pandas as pd
from sqlalchemy import create_engine
from prefect.artifacts import create_table_artifact

class DBTCommandError(Exception):
    def __init__(self, message="DBT command execution failed"):
        super().__init__(message)

DBT_EXE = shutil.which("dbt") or "dbt"

db_username = 'username'
db_password = 'password'
db_name = 'yourdatabase'
db_host = 'localhost'  # Use 'localhost' if the database is on your local machine
db_port = '5432'

@task(task_run_name="{test_name}")
def dbt_task_run(test_name: str):
    logger = get_run_logger()
    dbt_command = f"{DBT_EXE} test --select {test_name} --store-failures"
    logger.info(f"RUNNING DBT COMMAND: {dbt_command}")

    stdout, stderr, returncode = utils.run_cmd(dbt_command)

    if returncode != 0:
        # Improved regex to capture the SQL query more accurately
        match = re.search(r"compiled Code at .+?\.sql\s+[\s\S]+?\s+-+\s+([\s\S]+?)\s+-+", stdout, re.DOTALL)
        sql_query = match.group(1).strip() if match else "SQL query not found"
        error_message = f"DBT COMMAND FAILED:\n{stdout}\n\nSQL Query:\n{sql_query}"
        engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')
        # Connecting to the database and executing the query
        df = pd.read_sql_query(sql_query, engine)


        # Convert Timestamp columns to string (adjust the column names as necessary)
        for col, dtype in df.dtypes.items():
            if dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Convert the DataFrame to a list of dictionaries
        data_as_dict = df.to_dict('records')

        # Creating a Prefect table artifact with a valid key
        create_table_artifact(
            key=test_name.lower().replace('_', '-'),  # Ensure the key is in lowercase and uses dashes
            table=data_as_dict,
            description="Results from SQL query execution"
        )


        raise DBTCommandError(error_message)
    else:
        logger.info(stdout)


@flow(log_prints=True, task_runner=ConcurrentTaskRunner())
def dbt_flow_run(run_scope: str = "project"):

    if run_scope != 'project':
        dbt_select_command = f"--select transformation/{run_scope}"
    else:
        dbt_select_command = ""

    dbt_ls_command = f"{DBT_EXE} ls {dbt_select_command} --resource-type=test --output json" #  --output-keys 'resource_type name alias depends_on'
    print(f"Executing command:\n{dbt_ls_command}")
    dbt_ls_result_raw, stderr, returncode = utils.run_cmd(dbt_ls_command)
    dbt_ls_result_raw = dbt_ls_result_raw.split("\n")

    dbt_ls_result = [json.loads(line.strip()) for line in dbt_ls_result_raw if line.strip().startswith('{') and line.strip().endswith('}')]
    print(f"Command result:\n{dbt_ls_result}")

    for test in dbt_ls_result:
        dbt_task_run.submit(test_name=test['name'])

if __name__ == "__main__":
    dbt_flow_run.serve(
        name="dbt-tests", 
    )
