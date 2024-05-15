def create_CropSpot_pipeline(
    pipeline_name,
    project_name,
    dataset_name,
    queue_name,
    model_path_1,
    model_path_2,
    model_path_3,
    test_data_dir,
    repo_path,
    branch,
    commit_message,
    model_name,
):
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

    from clearml import PipelineController, Task
    from upload_data import upload_dataset, download_dataset
    from preprocess_data import preprocess_dataset
    from resnet_train import resnet_train
    from densenet_train import densenet_train
    from cnn_train import custom_cnn_train
    from model_evaluation import evaluate_model
    from compare_models import compare_models
    from update_model import update_repository

    # Initialize a new pipeline controller task
    pipeline = PipelineController(
        name=pipeline_name,
        project=project_name,
        version="1.0",
        add_pipeline_tags=True,
        target_project=project_name,
        auto_version_bump=True,
    )

    # Add pipeline-level parameters with defaults from function arguments
    pipeline.add_parameter(name="project_name", default=project_name)
    pipeline.add_parameter(name="dataset_name", default=dataset_name)
    pipeline.add_parameter(name="queue_name", default=queue_name)
    pipeline.add_parameter(name="model_path_1", default=model_path_1)
    pipeline.add_parameter(name="model_path_2", default=model_path_2)
    pipeline.add_parameter(name="model_path_3", default=model_path_3)
    pipeline.add_parameter(name="test_data_dir", default=test_data_dir)
    pipeline.add_parameter(name="repo_path", default=repo_path)
    pipeline.add_parameter(name="branch", default=branch)
    pipeline.add_parameter(name="commit_message", default=commit_message)
    pipeline.add_parameter(name="model_name", default=model_name)

    # Set the default execution queue
    pipeline.set_default_execution_queue("helldiver")

    # Step 1: Upload Data
    pipeline.add_function_step(
        name="Data_Upload",
        task_name="Upload Raw Data",
        function=upload_dataset,
        function_kwargs=dict(
            project_name="${pipeline.project_name}",
            dataset_name="${pipeline.dataset_name}",
            queue_name="${pipeline.queue_name}",
        ),
        task_type=Task.TaskTypes.data_processing,
        function_return=["raw_dataset_id", "raw_dataset_name"],
        helper_functions=[download_dataset],
        parents=None,
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 2: Preprocess Data
    pipeline.add_function_step(
        name="Data_Preprocessing",
        task_name="Preprocess Uploaded Data",
        function=preprocess_dataset,
        function_kwargs=dict(
            dataset_name="${pipeline.dataset_name}",
            project_name="${pipeline.project_name}",
            queue_name="${pipeline.queue_name}",
        ),
        task_type=Task.TaskTypes.data_processing,
        function_return=["processed_dataset_id", "processed_dataset_name"],
        parents=["Data_Upload"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 3(a): Train Model(s)
    pipeline.add_function_step(
        name="ResNet_Model_Training",
        task_name="ResNet Train Model",
        function=resnet_train,
        function_kwargs=dict(
            dataset_name="${pipeline.dataset_name}",
            project_name="${pipeline.project_name}",
            queue_name="${pipeline.queue_name}",
        ),
        task_type=Task.TaskTypes.training,
        function_return=["resnet_model_id"],
        parents=["Data_Preprocessing"],
        project_name=project_name,
        cache_executed_step=False,
    )

    # Step 3(b): Train Model(s)
    pipeline.add_function_step(
        name="DenseNet_Model_Training",
        task_name="DenseNet Train Model",
        function=densenet_train,
        function_kwargs=dict(
            dataset_name="${pipeline.dataset_name}",
            project_name="${pipeline.project_name}",
            queue_name="${pipeline.queue_name}",
        ),
        task_type=Task.TaskTypes.training,
        function_return=["densenet_model_id"],
        parents=["Data_Preprocessing"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 3(c): Train Model(s)
    pipeline.add_function_step(
        name="CNN_Model_Training",
        task_name="CNN Train Model",
        function=custom_cnn_train,
        function_kwargs=dict(
            dataset_name="${pipeline.dataset_name}",
            project_name="${pipeline.project_name}",
            queue_name="${pipeline.queue_name}",
        ),
        task_type=Task.TaskTypes.training,
        function_return=["cnn_model_id"],
        parents=["Data_Preprocessing"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 4(a): Evaluate Model(s)
    pipeline.add_function_step(
        name="ResNet_Model_Evaluation",
        task_name="ResNet Evaluate Model",
        function=evaluate_model,
        function_kwargs={
            "model_path": "${pipeline.model_path_1}",
            "test_data_dir": "${pipeline.test_data_dir}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.testing,
        function_return=["f1_score"],
        parents=["ResNet_Model_Training"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 4(b): Evaluate Model(s)
    pipeline.add_function_step(
        name="DenseNet_Model_Evaluation",
        task_name="DenseNet Evaluate Model",
        function=evaluate_model,
        function_kwargs={
            "model_path": "${pipeline.model_path_2}",
            "test_data_dir": "${pipeline.test_data_dir}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.testing,
        function_return=["f1_score"],
        parents=["DenseNet_Model_Training"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 4(c): Evaluate Model(s)
    pipeline.add_function_step(
        name="CNN_Model_Evaluation",
        task_name="CNN Evaluate Model",
        function=evaluate_model,
        function_kwargs={
            "model_path": "${pipeline.model_path_3}",
            "test_data_dir": "${pipeline.test_data_dir}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.testing,
        function_return=["f1_score"],
        parents=["CNN_Model_Training"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # Step 5: Compare Model(s)
    pipeline.add_function_step(
        name="Model_Comparison",
        task_name="Compare Models",
        function=compare_models,
        function_kwargs={
            "model_path_1": "${pipeline.model_path_1}",
            "model_path_2": "${pipeline.model_path_2}",
            "model_path_3": "${pipeline.model_path_3}",
            "queue_name": "${pipeline.queue_name}",
        },
        task_type=Task.TaskTypes.service,
        parents=["ResNet_Model_Evaluation", "DenseNet_Model_Evaluation", "CNN_Model_Evaluation"],
        project_name=project_name,
        cache_executed_step=False,
        execution_queue=queue_name,
    )

    # # Step 5: Update Model in GitHub Repository
    # pipeline.add_function_step(
    #     name="GitHub_Update",
    #     task_name="Update Model Weights in GitHub Repository",
    #     function=update_repository,
    #     function_kwargs={
    #         "repo_path": "${pipeline.repo_path}",
    #         "branch_name": "${pipeline.branch}",
    #         "commit_message": "${pipeline.commit_message}",
    #         "project_name": "${pipeline.project_name}",
    #         "model_name": "${pipeline.model_name}",
    #         "queue_name": "${pipeline.queue_name}",
    #     },
    #     task_type=Task.TaskTypes.service,
    #     parents=["Model_Training", "Model_Evaluation"],
    #     project_name=project_name,
    #     cache_executed_step=False,
    #     execution_queue=queue_name,
    # )

    # Start the pipeline
    print("CropSpot Data Pipeline initiated. Check ClearML for progress.")
    pipeline.start(queue="helldiver")
    # pipeline.start_locally(run_pipeline_steps_locally=False)


if __name__ == "__main__":
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(description="Run CropSpot Pipeline")

    # Add arguments
    parser.add_argument(
        "--pipeline_name",
        type=str,
        required=False,
        default="CropSpot Pipeline",
        help="Name of the pipeline",
    )
    parser.add_argument(
        "--project_name",
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
    parser.add_argument(
        "--model_path_1",
        type=str,
        required=False,
        default="Trained Models/cropspot_resnet_model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--model_path_2",
        type=str,
        required=False,
        default="Trained Models/cropspot_densenet_model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--model_path_3",
        type=str,
        required=False,
        default="Trained Models/cropspot_CNN_model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--test_data_dir",
        type=str,
        required=False,
        default="Dataset/Preprocessed",
        help="Directory containing test data",
    )
    parser.add_argument(
        "--repo_path",
        type=str,
        required=False,
        default=".",
        help="Path to the local Git repository",
    )
    parser.add_argument(
        "--branch",
        type=str,
        required=False,
        default="Crop-33-Deploy-MLOPs-pipeline",
        help="The branch to commit and push changes to",
    )
    parser.add_argument(
        "--commit_message",
        type=str,
        required=False,
        default="Automated commit of model changes",
        help="Commit message",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        required=False,
        default="CropSpot_Model",
        help="ClearML trained model",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the parsed arguments
    create_CropSpot_pipeline(
        pipeline_name=args.pipeline_name,
        project_name=args.project_name,
        dataset_name=args.dataset_name,
        queue_name=args.queue_name,
        model_path=args.model_path,
        test_data_dir=args.test_data_dir,
        repo_path=args.repo_path,
        branch=args.branch,
        commit_message=args.commit_message,
        model_name=args.model_name,
    )
