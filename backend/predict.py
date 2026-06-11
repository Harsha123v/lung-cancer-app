import sys
import json
import numpy as np
import pickle
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg19 import VGG19, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D

# Class names
CLASS_NAMES = [
    'Adenocarcinoma',
    'Large Cell Carcinoma',
    'Normal',
    'Squamous Cell Carcinoma'
]

def load_feature_extractor():
    base_model = VGG19(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )
    feature_extractor = Model(
        inputs=base_model.input,
        outputs=GlobalAveragePooling2D()(base_model.output)
    )
    return feature_extractor

def predict(image_path):
    # Load VGG19 feature extractor
    feature_extractor = load_feature_extractor()

    # Load SVM model
    with open('vgg19_svm_model.pkl', 'rb') as f:
        svm_model = pickle.load(f)

    # Load and preprocess image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    # Extract features
    features = feature_extractor.predict(img_array, verbose=0)

    # Predict
    prediction = svm_model.predict(features)[0]
    diagnosis = CLASS_NAMES[prediction]

    # Return result
    result = {
        'diagnosis': diagnosis,
        'is_cancer': diagnosis != 'Normal',
        'message': 'No cancer detected' if diagnosis == 'Normal' else f'Cancer detected: {diagnosis}'
    }

    print(json.dumps(result))

if __name__ == '__main__':
    image_path = sys.argv[1]
    predict(image_path)