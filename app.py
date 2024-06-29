import streamlit as st
from PIL import Image
import numpy as np
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import img_to_array

# Load the EfficientNetB0 model pre-trained on ImageNet
base_model = EfficientNetB0(weights='imagenet', include_top=False)

# Add custom top layers for binary classification
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(1, activation='sigmoid')(x)

# Create the full model
model = Model(inputs=base_model.input, outputs=predictions)

# Function to preprocess the image
def preprocess_image(img):
    img = img.resize((224, 224))  # Resize image to match model expected sizing
    img = img_to_array(img)  # Convert image to numpy array
    img = np.expand_dims(img, axis=0)  # Add a batch dimension
    img = preprocess_input(img)  # Preprocess image according to EfficientNetB0 requirements
    return img

# Streamlit UI
st.title("Image Forgery Detection")

# File upload and classification
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    # Preprocess the image
    img = preprocess_image(image)

    # Classify the image
    prediction = model.predict(img)
    if prediction > 0.5:
        st.write("Prediction: This image is forged.")
    else:
        st.write("Prediction: This image is real.")
