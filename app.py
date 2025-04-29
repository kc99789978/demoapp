import streamlit as st
from openai import OpenAI


import requests
from io import BytesIO
from PIL import Image
import os

def save_image(url, path):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image.save(path)
    return path

# Streamlit app
st.set_page_config(page_title="Photorealistic Image Generator", layout="centered")
import base64
from openai import OpenAI

def is_valid_api_key(api_key: str) -> bool:
    return isinstance(api_key, str) and api_key.startswith('sk-') and len(api_key) >= 20

def reset_api_key():
    st.session_state['authenticated'] = False
    st.session_state['api_key'] = ''
    st.rerun()

def generate_image(api_key: str, prompt: str, size: str = "1024x1024"):
    try:
        client = OpenAI(api_key=api_key)
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            n=1,
            size=size
        )
        image_bytes = base64.b64decode(img.data[0].b64_json)
        save_path = os.path.join("generated_image.png")
        with open(save_path, "wb") as f:
            f.write(image_bytes)
        return save_path, None
    except Exception as e:
        return None, str(e)

def main():
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ''
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'image_path' not in st.session_state:
        st.session_state['image_path'] = ''

    if not st.session_state['authenticated']:
        st.title("Enter your OpenAI API Key")
        api_key = st.text_input("OpenAI API Key", type="password")
        if st.button("Submit"):
            if api_key:
                st.session_state['api_key'] = api_key
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Please enter a valid API key.")
    else:
        st.title("Photorealistic Image Generator")
        user_text = st.text_input("Enter image description", key="user_text")
        if st.button("Generate"):
            if not user_text.strip():
                st.warning("Please enter a description.")
            else:
                api_key = st.session_state['api_key']
                if not is_valid_api_key(api_key):
                    st.error("Invalid or missing OpenAI API key. Please re-enter your key.")
                    reset_api_key()
                else:
                    prompt = f"generate a photorealistic image {user_text}"
                    save_path, error = generate_image(api_key, prompt)
                    if error:
                        st.error(f"Failed to generate image: {error}")
                    else:
                        st.session_state['image_path'] = save_path
        # Show image if already generated
        if st.session_state['image_path']:
            st.image(st.session_state['image_path'], caption="Generated Image", use_column_width=True)

if __name__ == "__main__":
    main()
