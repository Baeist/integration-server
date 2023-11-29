from IntegrationServer.utility import Utility


class JobAssigner:
    def __init__(self):
        self.util = Utility

    def create_jobs(self, pipeline_name):
        try:
            config = self.util.get_value(self.util, "../IntegrationServer/pipeline_job_config.json", pipeline_name)

            jobs_dict = {}

            for key in config:
                job_name = config.get(key)
                jobs_dict[job_name] = "WAITING"

                order = key[4:]
                jobs_dict[order] = job_name

            return jobs_dict

        except Exception as e:
            print(f"Pipeline name does not match job in config file: {e}")
