import argparse

# from pipeline_v2 import create_CropSpot_pipeline

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
        default="TomatoDiseaseDatasetV2",
        help="Name for the original dataset",
    )
    parser.add_argument(
        "--queue_name",
        type=str,
        required=False,
        default="helldiver_2",
        help="ClearML queue name",
    )
    parser.add_argument(
        "--model_path_1",
        type=str,
        required=False,
        default="cropspot_resnet_model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--model_path_2",
        type=str,
        required=False,
        default="cropspot_densenet_model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--model_path_3",
        type=str,
        required=False,
        default="cropspot_CNN_model.h5",
        help="Local model path",
    )
    parser.add_argument(
        "--test_dataset",
        type=str,
        required=False,
        default="TomatoDiseaseDatasetV2_test",
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
        model_name_1=args.model_path_1,
        model_name_2=args.model_path_2,
        model_name_3=args.model_path_3,
        test_dataset=args.test_dataset,
        repo_path=args.repo_path,
        branch=args.branch,
        commit_message=args.commit_message,
        model_name=args.model_name,
    )
