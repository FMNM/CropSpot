def custom_cnn_train(dataset_name, project_name):
    """
    Train the model using a custom CNN architecture with preprocessed dataset.

    Args:
        dataset_name (str): Name of the preprocessed dataset
        project_name (str): Name of the ClearML project
        queue_name (str): Name of the ClearML queue for remote execution

    Returns:
        ID of the trained model
    """
    from clearml import Task, Dataset, OutputModel

    task = Task.init(project_name=project_name, task_name="CNN Train Model")
    # task.execute_remotely(queue_name=queue_name, exit_process=True)

    import os
    import pickle
    import matplotlib.pyplot as plt
    from keras.models import Model
    from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
    from keras.optimizers import Adam
    from keras.callbacks import EarlyStopping, ReduceLROnPlateau, LambdaCallback
    from keras.preprocessing.image import ImageDataGenerator

    # Load preprocessed dataset
    prep_dataset_name = dataset_name + "_preprocessed"
    dataset = Dataset.get(dataset_name=prep_dataset_name)

    # Check if the dataset is already downloaded. If not, download it. Otherwise, use the existing dataset.
    dataset_path = f"Dataset/{prep_dataset_name}"
    if not os.path.exists(dataset_path):
        dataset.get_mutable_local_copy(dataset_path)

    # # Get image size from the first image from the healthy directory
    # first_image_file = os.listdir(f"{dataset_path}/{first_category}")[0]
    # img = plt.imread(f"{dataset_path}/{first_category}/{first_image_file}")
    # img_height, img_width, _ = img.shape
    # img_size = min(img_height, img_width)
    img_size = 224

    batch_size = 64

    # Data augmentation and preprocessing
    datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=0.2,
    )

    train_generator = datagen.flow_from_directory(dataset_path, target_size=(img_size, img_size), batch_size=batch_size, class_mode="categorical", shuffle=True, seed=42, subset="training")
    test_generator = datagen.flow_from_directory(dataset_path, target_size=(img_size, img_size), batch_size=batch_size, class_mode="categorical", shuffle=True, seed=42, subset="validation")

    epochs = 200
    num_classes = len(train_generator.class_indices)
    optimizer = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999)
    early_stopping = EarlyStopping(monitor="val_accuracy", patience=10, min_delta=0.001, restore_best_weights=True)
    learning_rate_reduction = ReduceLROnPlateau(monitor="val_accuracy", patience=3, verbose=1, factor=0.75, min_lr=0.00001)

    inputs = Input(shape=(img_size, img_size, 3))
    x = Conv2D(32, (3, 3), activation="relu")(inputs)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Conv2D(64, (3, 3), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Conv2D(128, (3, 3), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Conv2D(128, (3, 3), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Flatten()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation="softmax")(x)

    cnn_model = Model(inputs=inputs, outputs=predictions)
    cnn_model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])

    logger = task.get_logger()
    clearml_log_callbacks = [
        LambdaCallback(
            on_epoch_end=lambda epoch, logs: [
                logger.report_scalar("loss", "train", iteration=epoch, value=logs["loss"]),
                logger.report_scalar("accuracy", "train", iteration=epoch, value=logs["accuracy"]),
                logger.report_scalar("val_loss", "validation", iteration=epoch, value=logs["val_loss"]),
                logger.report_scalar("val_accuracy", "validation", iteration=epoch, value=logs["val_accuracy"]),
            ]
        )
    ]

    cnn_model.fit(train_generator, epochs=epochs, validation_data=test_generator, callbacks=[learning_rate_reduction, early_stopping, clearml_log_callbacks])

    trained_model_dir = "Trained Models"
    if not os.path.exists(trained_model_dir):
        os.makedirs(trained_model_dir)

    cnn_model.save(os.path.join(trained_model_dir, "cropspot_CNN_model.h5"))

    output_model = OutputModel(task=task, name="cropspot_CNN_model", framework="Tensorflow")
    output_model.update_weights(os.path.join(trained_model_dir, "cropspot_CNN_model.h5"), upload_uri="https://files.clear.ml", auto_delete_file=False)
    output_model.publish()

    task.upload_artifact("CNN Model", artifact_object="cropspot_CNN_model.h5")

    return output_model.id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset_name", type=str, required=False, default="TomatoDiseaseDatasetV2", help="Name of the preprocessed dataset")
    parser.add_argument("--project_name", type=str, required=False, default="CropSpot", help="Name of the ClearML project")
    parser.add_argument("--queue_name", type=str, required=False, default="helldiver", help="Name of the ClearML queue for remote execution")

    args = parser.parse_args()

    model_id = custom_cnn_train(args.dataset_name, args.project_name, args.queue_name)

    print(f"Model trained with ID: {model_id}")