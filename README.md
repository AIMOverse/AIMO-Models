# AIMO: Emotional Companion Language Model for Trendy Toys

AIMO is a lightweight, large-language model designed to provide emotional companionship through conversations. It leverages a causal language model to generate empathetic and engaging responses, making it an ideal fit for trendy emotional companion toys.

## Features
- **Emotional Engagement**: AIMO offers empathetic responses to user inputs.
- **Lightweight and Efficient**: Designed to run efficiently on devices with GPU or CPU.
- **Customizable**: Easily extendable for specific use cases or personalized prompts.

## Installation
To get started, clone this repository and install the required dependencies.

```bash
# Clone the repository
git clone https://github.com/AIMOverse/AIMO-Models.git
cd AIMO-Models

# Install dependencies
pip install -r requirements.txt
```

## Usage
The following example demonstrates how to use AIMO:

```python
from aimo import AIMO

if __name__ == "__main__":
    ai = AIMO()
    reply = ai.get_response([{ "role": "user", "content": "I'm a bit sad today. The weather in London is really bad. It's always cloudy."}])
    print(reply)
```

### Example Output
```
I'm sorry to hear that. London's weather can indeed be gloomy sometimes, but perhaps a cozy day indoors with a good book or movie could lift your spirits?
```

## How It Works
1. **Model Initialization**: The model and tokenizer are loaded from the `OEvortex/HelpingAI2.5-2B` pre-trained checkpoint.
2. **Conversation Input**: Users provide a chat history as a list of dictionaries containing roles (e.g., "user") and messages.
3. **Text Generation**: The model generates responses using advanced sampling techniques.
4. **Response Decoding**: The generated tokens are decoded into human-readable text.

## Requirements
- Python 3.8+
- PyTorch
- Transformers library
- GPU (recommended but not required)

## Model Details
- **Base Model**: `OEvortex/HelpingAI2.5-2B`
- **Architecture**: Transformer-based causal language model
- **Fine-Tuning**: Adapted for empathetic conversations

## Customization
You can modify the model's behavior by adjusting generation parameters such as:
- `max_new_tokens`: Controls the maximum length of the generated response.
- `temperature`: Adjusts randomness in the output.
- `top_p`: Implements nucleus sampling for better response quality.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- [Hugging Face Transformers](https://github.com/huggingface/transformers) for providing tools to work with large language models.
- `OEvortex` for the pre-trained model checkpoint.

## Contact
For questions or feedback, please contact jack.pan.23@ucl.ac.uk.
