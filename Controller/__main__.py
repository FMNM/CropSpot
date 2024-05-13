import argparse
from pipeline import create_CropSpot_pipeline
from clearml import Task

if __name__ == "__main__":
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
        "--model_path",
        type=str,
        required=False,
        default="Trained Models/CropSpot_Model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--model_history_path",
        type=str,
        required=False,
        default="Trained Models/CropSpot_Model_History.pkl",
        help="Local model history path",
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

    # task = Task.init(project_name=args.project_name, task_name=args.pipeline_name)
    # task.connect(args)
    # task.execute_remotely(queue_name=args.queue_name)

    # Call the function with the parsed arguments
    create_CropSpot_pipeline(
        pipeline_name=args.pipeline_name,
        project_name=args.project_name,
        dataset_name=args.dataset_name,
        queue_name=args.queue_name,
        model_path=args.model_path,
        model_history_path=args.model_history_path,
        test_data_dir=args.test_data_dir,
        repo_path=args.repo_path,
        branch=args.branch,
        commit_message=args.commit_message,
        model_name=args.model_name,
    )
