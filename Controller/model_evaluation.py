import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import f1_score, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize
from itertools import cycle
from math import ceil
import pickle as pkl
import tensorflow as tf


def evaluate_model(model_path, history_path, test_data_dir, batch_size, img_size):
    # import numpy as np
    # import matplotlib.pyplot as plt
    # import seaborn as sns
    # from keras.preprocessing.image import ImageDataGenerator
    # from sklearn.metrics import f1_score, confusion_matrix, roc_curve, auc
    # from itertools import cycle
    # from math import ceil
    # import pickle as pkl
    # import tensorflow as tf
    # from sklearn.preprocessing import label_binarize

    # Load the model
    model = tf.keras.models.load_model(model_path)

    # Load history
    with open(history_path, "rb") as file:
        history = pkl.load(file)

    # Data generator for evaluation
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)
    test_generator = test_datagen.flow_from_directory(test_data_dir, target_size=(img_size, img_size), batch_size=batch_size, class_mode="categorical", shuffle=False, seed=42)

    # Calculate the correct number of steps per epoch
    steps = ceil(test_generator.samples / test_generator.batch_size)

    # Generate predictions
    predictions = model.predict(test_generator, steps=steps)
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_generator.classes[: len(y_pred)]

    # Evaluate the model
    score = model.evaluate(test_generator)
    print(f"Test loss: {score[0]:.3f}")
    print(f"Test accuracy: {score[1]:.3f}")

    # Printing the f1 score
    f1 = f1_score(y_true, y_pred, average="macro")
    print(f"F1 Score: {f1}")

    # Plotting the confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt="d")
    plt.xlabel("Predicted labels")
    plt.ylabel("True labels")
    plt.title("Confusion Matrix")
    plt.show()

    y_test_binarized = label_binarize(y_true, classes=np.arange(test_generator.num_classes))

    # Compute ROC curve and ROC area for each class
    n_classes = y_test_binarized.shape[1]
    fpr, tpr, roc_auc = dict(), dict(), dict()
    colors = cycle(["blue", "red", "green"])
    plt.figure()
    for i, color in zip(range(n_classes), colors):
        fpr[i], tpr[i], _ = roc_curve(y_test_binarized[:, i], predictions[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], color=color, lw=2, label="ROC curve of class {0} (area = {1:0.2f})".format(i, roc_auc[i]))

    plt.plot([0, 1], [0, 1], "k--", lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Multi-class ROC")
    plt.legend(loc="lower right")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ResNet Model")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained model file")
    parser.add_argument("--history_path", type=str, required=True, help="Path to the training history file")
    parser.add_argument("--test_data_dir", type=str, required=True, help="Directory containing test data")
    parser.add_argument("--batch_size", type=int, required=True, help="Batch size for evaluation")
    parser.add_argument("--img_size", type=int, required=True, help="Image size (height and width should be the same)")

    args = parser.parse_args()

    evaluate_model(args.model_path, args.history_path, args.test_data_dir, args.batch_size, args.img_size)
