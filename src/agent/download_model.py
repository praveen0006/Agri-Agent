import os
from huggingface_hub import hf_hub_download


def download_model():
    model_id = "bartowski/Llama-3.2-1B-Instruct-GGUF"
    filename = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"

    # Target directory
    model_dir = "models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    print(f"Downloading {filename} from {model_id}...")

    try:
        model_path = hf_hub_download(
            repo_id=model_id, filename=filename, local_dir=model_dir, local_dir_use_symlinks=False
        )
        print(f"✅ Success! Model downloaded to: {model_path}")
        return model_path
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return None


if __name__ == "__main__":
    download_model()
