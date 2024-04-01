# dbt-prefect-orchestration: Managing DBT Jobs with Prefect

## Description

This project serves as a showcase demonstrating the integration of DBT (Data Build Tool) jobs and tests within Prefect workflows. It is designed to provide a hands-on example for data engineers and developers looking to explore the synergy between DBT for data transformation and Prefect for workflow orchestration. Through Docker-compose for environment setup, and a Python script for database population, this showcase illustrates a comprehensive workflow from setting up your data environment to orchestrating complex data workflows with Prefect.

## Highlights

- **Integration Showcase**: Demonstrates how to seamlessly integrate DBT tasks within Prefect flows.

![](/assets/dbt_prefect_runs.png)

- **Artifacts from Failed DBT Tests**: Showcases how to configure Prefect to generate and handle artifacts from failed DBT tests, enhancing debugging capabilities.

```yaml
models:
  - name: VIZ_ORDERS
    description: ""
    columns:
        ...
      - name: order_amount
        description: ""
        data_type: numeric
        tests:
          - dbt_utils.expression_is_true:
              expression: "> 18"
```
![](/assets/dbt_test_prefect_artifact.png)

- **Educational Resource**: Serves as a valuable resource for learning about data workflow orchestration and transformation best practices.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.6 or later

### Setup Instructions

1. **Start Docker Services**:
   - Run `docker-compose up -d` in the project root to launch PostgreSQL and pgAdmin.
   - Access pgAdmin at `http://localhost:5050`.

2. **Populate the Database**:
   - Install Python dependencies: `pip install psycopg2-binary faker`.
   - Execute `python generate_fake_data.py` to generate and insert data.

### Exploring the Showcase

1. **Configure DBT and Prefect**: Review the DBT project configuration and Prefect flow definitions to understand the setup.
2. **Run DBT Jobs Manually**: Try running DBT jobs directly to familiarize yourself with DBT commands.
3. **Execute Prefect Flows**: Launch Prefect flows that encapsulate DBT tasks to see the orchestration in action.
4. **Inspect Artifacts**: Explore how artifacts are generated from failed DBT tests for debugging purposes.
