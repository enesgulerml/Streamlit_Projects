import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import io


# --- Image Processing Functions ---
# All advanced logic is contained within a single file.

def apply_grayscale(img):
    """Converts the image to grayscale."""
    return img.convert("L")


def apply_blur(img, radius):
    """Applies a Gaussian blur filter to the image."""
    if radius > 0:
        return img.filter(ImageFilter.GaussianBlur(radius))
    return img


def adjust_brightness(img, factor):
    """Adjusts the brightness of the image."""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)


def adjust_contrast(img, factor):
    """Adjusts the contrast of the image."""
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)


def apply_edge_detection(img):
    """Applies an edge detection filter (FIND_EDGES)."""
    return img.filter(ImageFilter.FIND_EDGES)


def apply_color_inversion(img):
    """Inverts the colors of the image (Negative effect)."""
    # Convert the image to a NumPy array
    img_array = np.array(img.convert("RGB"))
    # Invert each pixel value (255 - current value)
    inverted_array = 255 - img_array
    # Convert back to a PIL image
    return Image.fromarray(inverted_array.astype('uint8'), 'RGB')


# --- Streamlit App Interface ---

def main():
    st.set_page_config(
        page_title="Advanced Image Processing Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📸 Advanced Image Processing Dashboard")
    st.markdown("""
    This single-file application applies various filters and transformations to your uploaded image using the **Pillow (PIL)** library.
    """)
    st.markdown("---")

    # Sidebar: Inputs and Controls
    st.sidebar.header("⚙️ Controls and Filters")

    # Image Uploader
    uploaded_file = st.sidebar.file_uploader(
        "Upload an image (JPEG, PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is None:
        st.info("Please upload an image from the sidebar to get started.")
        return

    # Process the image if uploaded
    original_img = Image.open(uploaded_file)
    processed_img = original_img.copy()

    st.sidebar.markdown("### Basic Adjustments")

    # Brightness and Contrast Controls
    brightness_factor = st.sidebar.slider("Brightness", 0.0, 3.0, 1.0, 0.1)
    contrast_factor = st.sidebar.slider("Contrast", 0.0, 3.0, 1.0, 0.1)

    # Blur Control
    blur_radius = st.sidebar.slider("Blur (Gaussian)", 0, 10, 0, 1)

    st.sidebar.markdown("### Special Filters")

    # Checkboxes
    grayscale = st.sidebar.checkbox("Apply Grayscale", value=False)
    edge_detect = st.sidebar.checkbox("Detect Edges", value=False)
    invert_colors = st.sidebar.checkbox("Invert Colors (Negative)", value=False)

    # --- Image Processing Pipeline ---

    # 1. Apply brightness and contrast
    if brightness_factor != 1.0:
        processed_img = adjust_brightness(processed_img, brightness_factor)

    if contrast_factor != 1.0:
        processed_img = adjust_contrast(processed_img, contrast_factor)

    # 2. Apply special filters
    if invert_colors:
        processed_img = apply_color_inversion(processed_img)

    if grayscale:
        processed_img = apply_grayscale(processed_img)

    if edge_detect:
        # Edge detection is typically applied last
        processed_img = apply_edge_detection(processed_img)

    # 3. Apply blur (usually the final step or based on desired order)
    if blur_radius > 0:
        processed_img = apply_blur(processed_img, blur_radius)

    # --- Display Results ---

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(original_img, use_column_width=True)

    with col2:
        st.subheader("Processed Image")
        st.image(processed_img, use_column_width=True)

        # --- Download Button (Advanced Feature) ---

        # Save the image to an in-memory buffer
        buf = io.BytesIO()
        # Get the original file format to maintain it on download
        original_format = original_img.format if original_img.format else 'PNG'

        try:
            processed_img.save(buf, format=original_format)
            byte_im = buf.getvalue()

            st.download_button(
                label="Download Processed Image",
                data=byte_im,
                file_name=f"processed_image.{original_format.lower()}",
                mime=f"image/{original_format.lower()}",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"An error occurred during download: {e}")


if __name__ == "__main__":
    main()