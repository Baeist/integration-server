import os
import shutil
from IntegrationServer import utility
from IntegrationServer.JobList import job_assigner
import json


class JobDriver:

    def __init__(self):
        self.util = utility.Utility()
        self.jobby = job_assigner.JobAssigner()

    def process_new_directories(self):

        input_dir = "./Files/NewFiles"
        in_process_dir = "./Files/InProcess"
        error_path = "./Files/Error"

        # Iterate over subdirectories in the input directory
        for subdirectory in os.listdir(input_dir):
            subdirectory_path = os.path.join(input_dir, subdirectory)

            # Check if a directory with the same name exists in the error path
            error_directory_path = os.path.join(error_path, subdirectory)
            if os.path.exists(error_directory_path) and os.path.isdir(error_directory_path):
                print(f"Directory {error_directory_path} already exists in the error path. Skipping processing.")
                continue

            # Check if it's a directory
            if os.path.isdir(subdirectory_path):
                # Look for a JSON job file in the subdirectory
                json_job_files = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}_jobs.json"]
                # check if _jobs file already exist, it shouldnt
                if json_job_files:
                    # check other folders for similar names, then maybe move files to error folder, depend on job status?
                    print("error joblist already exist")
                else:
                    # Look for a JSON file in the subdirectory
                    json_files = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}.json"]
                    error_dir = os.path.join(error_path, subdirectory)

                    # if no json files are present move files to error dir
                    if len(json_files) == 0:
                        shutil.move(subdirectory_path, error_dir)
                        continue

                    if json_files:
                        json_file_name = json_files[0]
                        json_file_path = os.path.join(subdirectory_path, json_file_name)

                        # Read the JSON file to get the 'pipeline_name' value
                        pipeline_name = self.util.get_value(json_file_path, "pipeline_name")

                        # Create jobs dictionary
                        jobs_json = self.jobby.create_jobs(pipeline_name)

                        if jobs_json is None:
                            shutil.move(subdirectory_path, error_dir)
                            continue

                        # Create a new JSON file with '_jobs' suffix
                        jobs_file_name = json_file_name.replace('.json', '_jobs.json')
                        jobs_file_path = os.path.join(subdirectory_path, jobs_file_name)

                        with open(jobs_file_path, 'w') as jobs_file:
                            json.dump(jobs_json, jobs_file, indent=2)

                        # Move the directory to the 'InProcess' directory or error if it already exists
                        new_directory_path = os.path.join(in_process_dir, f"{pipeline_name}/{subdirectory}")

                        if os.path.exists(new_directory_path):
                            shutil.move(subdirectory_path, error_dir)
                        else:
                            shutil.move(subdirectory_path, new_directory_path)

    def process_updated_directories(self):

        input_dir = "./Files/UpdatedFiles"
        in_process_dir = "./Files/InProcess"
        error_path = "./Files/Error"

        # Iterate over subdirectories in the input directory
        for subdirectory in os.listdir(input_dir):
            subdirectory_path = os.path.join(input_dir, subdirectory)

            # Check if a directory with the same name exists in the error path
            error_directory_path = os.path.join(error_path, subdirectory)
            if os.path.exists(error_directory_path) and os.path.isdir(error_directory_path):
            # TODO handle files if in error folder
                print(f"Directory {error_directory_path} already exists in the error path.")
                continue

            jobs_json = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}_jobs.json"]
            metadata_json = [f for f in os.listdir(subdirectory_path) if f == f"{subdirectory}.json"]

            if len(jobs_json) != 1 and len(metadata_json) != 1:
                #TODO move to error folder
                continue

            metadata_path = os.path.join(subdirectory_path, metadata_json[0])
            jobs_path = os.path.join(subdirectory_path, f"{subdirectory}_jobs.json")

            pipeline_name = self.util.get_value(metadata_path, "pipeline_name")

            process_pipeline_path = os.path.join(in_process_dir, pipeline_name)

            process_directory_path = os.path.join(process_pipeline_path, subdirectory)

            process_jobs_path = os.path.join(process_directory_path, f"{subdirectory}_jobs.json")

            process_jobs = self.util.read_json(process_jobs_path)
            updated_jobs = self.util.read_json(jobs_path)

            job_key_to_update = self.util.find_keys_with_value(process_jobs, "INPIPELINE")
            updated_job_keys = self.util.find_keys_with_value(updated_jobs, "INPIPELINE")

            if job_key_to_update == updated_job_keys:
                self.util.update_json(process_jobs_path, updated_job_keys, "DONE")
            else:
                # TODO move to error folder
                continue

            new_data = self.util.read_json(metadata_path)

            process_data_path = os.path.join(process_directory_path, f"{subdirectory}.json")

            self.util.write_full_json(process_data_path, new_data)

            shutil.rmtree(subdirectory_path)