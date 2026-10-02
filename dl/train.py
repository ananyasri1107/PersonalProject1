import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models

# =========================
# SETTINGS
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")

MODEL_DIR = os.path.join(BASE_DIR, "dl", "saved_model")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "plant_disease_model.h5"
)

CLASS_PATH = os.path.join(
    MODEL_DIR,
    "class_names.json"
)

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10


# =========================
# CREATE MODEL DIRECTORY
# =========================

os.makedirs(MODEL_DIR, exist_ok=True)


# =========================
# LOAD DATASET
# =========================

print("Loading dataset...")

train_data = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

validation_data = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)


# =========================
# CLASS NAMES
# =========================

class_names = train_data.class_names

print("\nClasses:")
for i, name in enumerate(class_names):
    print(i, "->", name)


# Save class names

with open(CLASS_PATH, "w") as f:
    json.dump(class_names, f)


# =========================
# PERFORMANCE
# =========================

AUTOTUNE = tf.data.AUTOTUNE

train_data = train_data.prefetch(
    buffer_size=AUTOTUNE
)

validation_data = validation_data.prefetch(
    buffer_size=AUTOTUNE
)


# =========================
# CNN MODEL
# =========================

model = models.Sequential([

    layers.Input(shape=(224, 224, 3)),

    layers.Rescaling(1.0 / 255),

    # CNN Layer 1
    layers.Conv2D(
        32,
        (3, 3),
        activation="relu"
    ),

    layers.MaxPooling2D(),

    # CNN Layer 2
    layers.Conv2D(
        64,
        (3, 3),
        activation="relu"
    ),

    layers.MaxPooling2D(),

    # CNN Layer 3
    layers.Conv2D(
        128,
        (3, 3),
        activation="relu"
    ),

    layers.MaxPooling2D(),

    # Flatten
    layers.Flatten(),

    # Fully Connected Layer
    layers.Dense(
        128,
        activation="relu"
    ),

    layers.Dropout(0.5),

    # Output
    layers.Dense(
        len(class_names),
        activation="softmax"
    )
])


# =========================
# COMPILE
# =========================

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# =========================
# MODEL SUMMARY
# =========================

model.summary()


# =========================
# TRAIN
# =========================

print("\nStarting training...\n")

history = model.fit(
    train_data,
    validation_data=validation_data,
    epochs=EPOCHS
)


# =========================
# SAVE MODEL
# =========================

model.save(MODEL_PATH)

print("\nTraining completed!")

print(
    "Model saved at:",
    MODEL_PATH
)

print(
    "Classes saved at:",
    CLASS_PATH
)