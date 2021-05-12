import enum
import os
import shutil
import subprocess
import sys
import time

import pytest

from assets.scripts.build_gallery import execute_shell_command
from great_expectations.data_context.util import file_relative_path


class BackendDependencies(enum.Enum):
    MYSQL = "MYSQL"
    MSSQL = "MSSQL"
    PANDAS = "PANDAS"
    POSTGRESQL = "POSTGRESQL"
    SPARK = "SPARK"
    SQLALCHEMY = "SQLALCHEMY"


integration_test_matrix = [
    # {
    #     "user_flow_script": "integration/code/connecting_to_your_data/filesystem/pandas.py",
    #     "base_dir": file_relative_path(__file__, "../../"),
    #     "data_context_dir": "integration/fixtures/runtime_data_taxi_monthly/great_expectations",
    #     "data_dir": "integration/fixtures/data",
    # },
    # {
    #     "name": "postgres_runtime_golden_path",
    #     "data_dir": "integration/fixtures/data",
    #     "base_dir": file_relative_path(__file__, "../../"),
    #     "data_context_dir": "integration/fixtures/runtime_data_taxi_monthly/great_expectations",
    #     "user_flow_script": "integration/code/connecting_to_your_data/database/postgres.py",
    #     "extra_backend_dependencies": BackendDependencies.POSTGRESQL,
    # },
    {
        "name": "snowflake_runtime_golden_path",
        "data_dir": "integration/fixtures/data",
        "base_dir": file_relative_path(__file__, "../../"),
        "data_context_dir": "integration/fixtures/runtime_data_taxi_monthly/great_expectations",
        "user_flow_script": "integration/code/connecting_to_your_data/database/snowflake_db.py",
    },
    # {
    #     "name": "pandas_two_batch_requests_two_validators",
    #     "base_dir": file_relative_path(__file__, "../../"),
    #     "data_context_dir": "tests/integration/fixtures/yellow_trip_data_pandas_fixture/great_expectations",
    #     "data_dir": "tests/test_sets/taxi_yellow_trip_data_samples",
    #     "user_flow_script": "tests/integration/fixtures/yellow_trip_data_pandas_fixture/two_batch_requests_two_validators.py",
    #     "expected_stderrs": "",
    #     "expected_stdouts": "",
    # },
]


def idfn(test_configuration):
    return test_configuration.get("user_flow_script")


@pytest.fixture
def pytest_parsed_arguments(request):
    return request.config.option


@pytest.mark.docs
@pytest.mark.integration
@pytest.mark.parametrize("test_configuration", integration_test_matrix, ids=idfn)
@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python3.7")
def test_docs(test_configuration, tmp_path, pytest_parsed_arguments):
    _check_for_skipped_tests(pytest_parsed_arguments, test_configuration)

    workdir = os.getcwd()
    try:

        startTime = time.time()
        os.chdir(tmp_path)
        base_dir = test_configuration.get("base_dir", ".")

        # Ensure GE is installed in our environment
        #ge_requirement = test_configuration.get("ge_requirement", "great_expectations")
        #execute_shell_command(f"pip install {ge_requirement}")
        #executionTime = (time.time() - startTime)
        #print("Installation Time:" + str(executionTime))
        #
        # Build test state
        #

        startTime = time.time()

        # DataContext
        context_source_dir = os.path.join(
            base_dir, test_configuration.get("data_context_dir")
        )
        test_context_dir = os.path.join(tmp_path, "great_expectations")
        shutil.copytree(
            context_source_dir,
            test_context_dir,
        )
        executionTime = (time.time() - startTime)
        print("DataContext Time:" + str(executionTime))


        startTime = time.time()

        if test_configuration.get("data_dir") is not None:
            # Test Data
            source_data_dir = os.path.join(base_dir, test_configuration.get("data_dir"))
            test_data_dir = os.path.join(tmp_path, "data")
            shutil.copytree(
                source_data_dir,
                test_data_dir,
            )

        # UAT Script
        script_source = os.path.join(
            test_configuration.get("base_dir"),
            test_configuration.get("user_flow_script"),
        )
        script_path = os.path.join(tmp_path, "test_script.py")
        shutil.copyfile(script_source, script_path)
        # Check initial state
        executionTime = (time.time() - startTime)

        print("CopyingData Time:" + str(executionTime))


        startTime = time.time()

        # Execute test
        res = subprocess.run(["python", script_path], capture_output=True)
        #res = "Hello"
        # Check final state
        expected_stderrs = test_configuration.get("expected_stderrs")
        expected_stdouts = test_configuration.get("expected_stdouts")
        expected_failure = test_configuration.get("expected_failure")
        outs = res.stdout.decode("utf-8")
        errs = res.stderr.decode("utf-8")
        print(outs)
        print(errs)
        executionTime = (time.time() - startTime)

        print("RunningTime Time:" + str(executionTime))

        if expected_stderrs:
            assert expected_stderrs == errs

        if expected_stdouts:
            assert expected_stdouts == outs

        if expected_failure:
            assert res.returncode != 0
        else:
            assert res.returncode == 0
    except:
        raise
    finally:
        os.chdir(workdir)



def _check_for_skipped_tests(pytest_args, test_configuration) -> None:
    """Enable scripts to be skipped based on pytest invocation flags."""
    dependencies = test_configuration.get("extra_backend_dependencies", None)
    if not dependencies:
        return
    elif dependencies == BackendDependencies.POSTGRESQL and (
        pytest_args.no_postgresql or pytest_args.no_sqlalchemy
    ):
        pytest.skip("Skipping postgres tests")
    elif dependencies == BackendDependencies.MYSQL and (
        pytest_args.no_mysql or pytest_args.no_sqlalchemy
    ):
        pytest.skip("Skipping mysql tests")
    elif dependencies == BackendDependencies.MSSQL and (
        pytest_args.no_mssql or pytest_args.no_sqlalchemy
    ):
        pytest.skip("Skipping mssql tests")
    elif dependencies == BackendDependencies.SPARK and pytest_args.no_spark:
        pytest.skip("Skipping spark tests")
