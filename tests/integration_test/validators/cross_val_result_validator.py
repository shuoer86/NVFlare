# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from nvflare.app_common.app_constant import AppConstants

from .app_result_validator import AppResultValidator


def check_cross_validation_result(server_data, client_data, run_data, n_clients=-1):
    if n_clients != -1:
        client_names = [client_data["client_names"][i] for i in range(n_clients)]
    else:
        client_names = list(client_data["client_names"])

    server_run_dir = os.path.join(server_data["server_path"], run_data["job_id"])

    if not os.path.exists(server_run_dir):
        print(f"check_cross_validation_result: server run dir {server_run_dir} doesn't exist.")
        return False

    cross_val_dir = os.path.join(server_run_dir, AppConstants.CROSS_VAL_DIR)
    if not os.path.exists(cross_val_dir):
        print(f"check_cross_validation_result: models dir {cross_val_dir} doesn't exist.")
        return False

    model_shareable_dir = os.path.join(cross_val_dir, AppConstants.CROSS_VAL_MODEL_DIR_NAME)
    if not os.path.exists(model_shareable_dir):
        print(f"check_cross_validation_result: model shareable directory {model_shareable_dir} doesn't exist.")
        return False

    result_shareable_dir = os.path.join(cross_val_dir, AppConstants.CROSS_VAL_RESULTS_DIR_NAME)
    if not os.path.exists(result_shareable_dir):
        print(f"check_cross_validation_result: result shareable directory {result_shareable_dir} doesn't exist.")
        return False

    # There should be three files in model_shareable
    server_model_names = ["SRV_" + server_data["server_name"]]
    model_file_names = server_model_names.copy()
    model_file_names = model_file_names + client_names
    print(f"Model files to look for: {model_file_names}")

    for model_file_name in model_file_names:
        model_file = os.path.join(model_shareable_dir, model_file_name)
        if not os.path.exists(model_file):
            print(f"check_cross_validation_result: model {model_file} doesn't exist in model shareable directory.")
            return False

    # Check all the results
    # results_file_names = ["client_1_server", "client_0_server", "client_1_client_0", "client_1_client_1",
    #                       "client_0_client_1", "client_0_client_0"]
    results_file_names = [f"{x}_{y}" for x in client_names for y in server_model_names]
    for client_name in client_names:
        results_file_names += [f"{client_name}_{x}" for x in client_names]
    print(f"Result files to look for: {results_file_names}")

    for results_file_name in results_file_names:
        result_file = os.path.join(result_shareable_dir, results_file_name)
        if not os.path.exists(result_file):
            print(f"check_cross_validation_result: result {result_file} doesn't exist in result shareable directory.")
            return False

    return True


class CrossValResultValidator(AppResultValidator):
    def validate_results(self, server_data, client_data, run_data) -> bool:
        cross_val_result = check_cross_validation_result(server_data, client_data, run_data)

        print(f"CrossVal Result: {cross_val_result}")

        if not cross_val_result:
            raise ValueError("Cross val failed.")

        return cross_val_result


class CrossValSingleClientResultValidator(AppResultValidator):
    def validate_results(self, server_data, client_data, run_data) -> bool:
        cross_val_result = check_cross_validation_result(server_data, client_data, run_data, n_clients=1)

        print(f"CrossVal Result: {cross_val_result}")

        if not cross_val_result:
            raise ValueError("Cross val failed.")

        return cross_val_result