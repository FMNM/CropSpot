import os
import argparse
from clearml import PipelineController, Task
from upload_data import upload_dataset, download_dataset
from preprocess_data import preprocess_dataset, preprocess_images
from model_training import train_model


def create_CropSpot_pipeline(
    pipeline_name: str = "CropSpot Pipeline",
    project_name: str = "CropSpot",
    dataset_name: str = "TomatoDiseaseDataset",
    queue_name: str = "helldiver",
):
    from clearml import PipelineController, Task
    from upload_data import upload_dataset, download_dataset
    from preprocess_data import preprocess_dataset, preprocess_images

    """
    Create a ClearML pipeline for the CropSpot project.
    
    Parameters:
        pipeline_name (str): Name of the pipeline.
        project_name (str): Name of the ClearML project.
        dataset_name (str): Name of the dataset.
        queue_name (str): Name of the queue to execute the pipeline.
        
    Returns:
        None
    """

    # Initialize a new pipeline controller task
    pipeline = PipelineController(
        name=pipeline_name,
        project=project_name,
        version="1.0",
        add_pipeline_tags=True,
        auto_version_bump=True,
        target_project=project_name,
    )

    # Add pipeline-level parameters with defaults from function arguments
    pipeline.add_parameter(name="project_name", default=project_name)
    pipeline.add_parameter(name="dataset_name", default=dataset_name)
    pipeline.add_parameter(name="queue_name", default=queue_name)

    # Step 1: Upload Data
    pipeline.add_function_step(
        name="Data Upload",
        function=upload_dataset,
        function_kwargs={
            "project_name": "${pipeline.project_name}",
            "dataset_name": "${pipeline.dataset_name}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.data_processing,
        task_name="Upload Raw Data",
        function_return=["raw_dataset_id", "dataset_name"],
        helper_functions=[download_dataset],
        execution_queue=queue_name,
        cache_executed_step=False,
    )

    # Step 2: Preprocess Data
    pipeline.add_function_step(
        name="Data Preprocessing",
        function=preprocess_dataset,
        function_kwargs={
            "dataset_name": "${pipeline.dataset_name}",
            "project_name": "${pipeline.project_name}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.data_processing,
        task_name="Preprocess Uploaded Data",
        function_return=["processed_dataset_id"],
        helper_functions=[preprocess_images],
        execution_queue=queue_name,
        cache_executed_step=False,
    )

    # Step 3: Train Model
    pipeline.add_function_step(
        name="train_model",
        function=train_model,
        function_kwargs={
            "dataset_name": "${pipeline.dataset_name}",
            "project_name": "${pipeline.project_name}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.training,
        task_name="Train Model",
        function_return=["model_file_name"],
        execution_queue=queue_name,
        cache_executed_step=False,
    )

    # # Step 4: Evaluate Model
    # pipeline.add_function_step(
    #     name="evaluate_model",
    #     function=evaluate_model,
    #     function_kwargs={
    #         "dataset_name": "${pipeline.dataset_name}",
    #         "project_name": "${pipeline.project_name}",
    #         "queue_name": "${pipeline.queue_name}",
    #     },
    #     task_type=Task.TaskTypes.testing,
    #     task_name="Evaluate Model",
    #     execution_queue=queue_name,
    #     cache_executed_step=False,
    # )

    # # Step 5: Update Model in GitHub Repository
    # pipeline.add_function_step(
    #     name="update_model",
    #     function=update_model,
    #     function_kwargs={
    #         "dataset_name": "${pipeline.dataset_name}",
    #         "project_name": "${pipeline.project_name}",
    #         "queue_name": "${pipeline.queue_name}",
    #     },
    #     task_type=Task.TaskTypes.system,
    #     task_name="Update Model",
    #     execution_queue=queue_name,
    #     cache_executed_step=False,
    # )

    # Start the pipeline
    pipeline.start(queue=queue_name)
    print("CropSpot Data Pipeline initiated. Check ClearML for progress.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CropSpot Data Pipeline")
    parser.add_argument(
        "--pipeline_name",
        type=str,
        required=False,
        default="CropSpot Data Pipeline",
        help="Name of the pipeline",
    )
    parser.add_argument(
        "--dataset_project",
        type=str,
        required=False,
        default="CropSpot",
        help="Project name for datasets",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        required=False,
        default="TomatoDiseaseDataset",
        help="Name for the raw dataset",
    )
    parser.add_argument(
        "--queue_name",
        type=str,
        required=False,
        default="helldiver",
        help="ClearML queue name",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the parsed arguments
    create_CropSpot_pipeline(
        pipeline_name=args.pipeline_name,
        project_name=args.dataset_project,
        dataset_name=args.dataset_name,
        queue_name=args.queue_name,
    )
