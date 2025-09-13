import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
import cv2

# --- PAGE CONFIG ---
# This must be the first Streamlit command in your script
st.set_page_config(
    page_title="AI Image Quality Analyzer",
    page_icon="📸",
    layout="centered" # or "wide"
)


# --- MODEL LOADING (Cached) ---
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model('image_quality_analyzer.h5')
    return model

model = load_model()


# --- HELPER FUNCTIONS ---
def preprocess_image(image):
    """Prepares the image for the AI model."""
    image = image.convert('RGB')
    image = image.resize((224, 224))
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = image_array / 255.0
    return image_array

def analyze_image_issues(image):
    """Analyzes a PIL image for specific quality issues using OpenCV."""
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    
    # Blur Detection (Laplacian Variance)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = laplacian_var < 100 

    # Brightness Detection (Average Pixel Intensity)
    brightness = np.mean(gray)
    is_dark = brightness < 70

    issues = []
    if is_blurry:
        issues.append(f"⚠️ Potential Blur Detected (Variance: {laplacian_var:.2f})")
    if is_dark:
        issues.append(f"⚠️ Potential Darkness Detected (Brightness: {brightness:.2f})")
    
    return issues


# --- SIDEBAR ---
with st.sidebar:
    st.header("About This Project")
    st.write("""
    This application leverages a Convolutional Neural Network (CNN) to classify image quality. 
    It was trained on a dataset of sharp and blurry images to distinguish between 'Good' and 'Bad' quality photos.
    
    When an image is classified as 'Bad', additional checks using OpenCV are performed to detect specific issues like blurriness and darkness.
    """)
    st.header("Technology Stack")
    st.write("- TensorFlow/Keras (MobileNetV2)")
    st.write("- OpenCV")
    st.write("- Streamlit")


# --- MAIN PAGE ---
st.title("📸 AI-Powered Image Quality Analyzer")
st.write("Upload an image and let the AI determine its quality. Clear, sharp images are 'Good', while blurry or dark ones are 'Bad'.")

uploaded_file = st.file_uploader("Choose an image to analyze...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(image, caption='Your Uploaded Image', use_container_width=True)

    with col2:
        with st.spinner('AI is analyzing the image...'):
            # AI Model Prediction
            processed_image = preprocess_image(image)
            prediction = model.predict(processed_image)
            score = prediction[0][0]

            st.subheader("Analysis Results:")

            if score > 0.5:
                st.success(f"**Result: Good Quality**")
            else:
                st.error(f"**Result: Bad Quality**")

            # OpenCV Heuristic Analysis
            issues = analyze_image_issues(image)
            
            with st.expander("Show Technical Details"):
                if score > 0.5:
                    st.write(f"The model is {score:.0%} confident this image is of good quality.")
                else:
                    st.write(f"The model is {1-score:.0%} confident this image is of bad quality.")
                
                if issues:
                    st.write("Further analysis found these potential issues:")
                    for issue in issues:
                        st.write(issue)
                elif score > 0.5:
                    st.write("No specific technical issues (blur, darkness) were flagged.")
                else:
                    st.write("AI predicts low quality, but specific issues (blur/darkness) were not strongly detected by our checks.")
else:
    st.info("Please upload an image to begin the analysis.")