# AIMO: Emotional Companion Language Model Backends

AIMO is a lightweight, large-language model backend designed to provide emotional companionship through conversations. It is optimized for generating empathetic and engaging responses, making it an ideal solution for emotional companion toys and applications.

## Features

- **Emotional Engagement**: Provides empathetic and meaningful responses to user inputs, fostering an emotional connection.
- **Lightweight and Efficient**: Optimized for performance on devices with GPU or CPU, ensuring smooth interactions.
- **Customizable**: Easily adaptable for specific use cases or personalized prompts, enabling tailored interactions.

## Installation

### Requirements

- Python 3.6 or higher
- CUDA 12.4 (for GPU support)

### Method 1: Standard Setup

Follow the steps below to set up AIMO on your system:

```bash
# Clone the repository
git clone https://github.com/AIMOverse/AIMO-Models.git
cd AIMO-Models

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Docker Setup

AIMO can also be deployed using Docker for easier dependency management and deployment:

```bash
# Clone the repository
git clone https://github.com/AIMOverse/AIMO-Models.git
cd AIMO-Models

# Build Docker Image and pass HF_ACCESS_TOKEN
docker build --build-arg HF_ACCESS_TOKEN=<your_hf_access_token> -t aimo-models-app .

# Run the Docker container
docker run -p 8000:8000 -e NEBULA_API_KEY=<your_key> -e SECRET_KEY=<your_secret_key> -e ADMIN_API_KEY=<your_admin_api_key>  aimo-models-app
```

## Deployment on Phala Network

To deploy AIMO on Phala Network, follow these steps:

1. Ensure you have the necessary API keys:
   - `HF_ACCESS_TOKEN`: For downloading Hugging Face models

2. Build the Docker image with the required environment variables:

```bash
# Export your API keys as environment variables
export HF_ACCESS_TOKEN="your_huggingface_token_here"

# Build the Docker image
docker build --build-arg HF_ACCESS_TOKEN=$HF_ACCESS_TOKEN -t aimoverse/aimo-emotion-model .
```

3. Push the image to a container registry accessible by the Phala Network:

```bash
# Tag the image for your registry
docker tag aimoverse/aimo-emotion-model your-registry/aimoverse/aimo-emotion-model:latest

# Push to registry
docker push your-registry/aimoverse/aimo-emotion-model:latest
```

4. Deploy on Phala using their container deployment interface.

## Environment Variables

The following environment variables are used by AIMO:

| Variable          | Description                                      | Required | Time of Requirement         |
|-------------------|--------------------------------------------------|----------|-----------------------------|
| `HF_ACCESS_TOKEN` | Hugging Face access token for downloading models | Yes      | During building Images      |
| `NEBULA_API_KEY`  | API key for LLM service                          | Yes      | During running applications |
| `SECRET_KEY`      | Secret Key for JWT Tokens                        | Yes      | During running applications |
| `ADMIN_API_KEY`   | Admin Key for manage invitation codes            | Yes      | During running applications |

## Usage

Start the AIMO server using the following command:

```bash
# If installed directly
fastapi run app/main.py
```

```bash
# If using Docker
docker run -p 8000:8000 -e NEBULA_API_KEY=your_key -e SECRET_KEY=your_secret_key -e ADMIN_API_KEY=your_admin_api_key -d aimoverse/aimo-emotion-model
```

Once the server is running, you can integrate it with your applications or test it through API endpoints.

## Test

Please Test the server before push!!!

Test the server using the command below:

```bash
coverage run --source=app -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"
```

## API Overview

### Version: `1.0.0`

The AIMO backend provides a RESTful API for interaction. The version 1.0.0 of the server has a base url of /api/v1.0.0.
Below is an example of the main endpoint:

### Endpoint: `/api/v1.0.0/chat/`

#### Method: `POST`

#### Request Body:
```json
{
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_new_tokens": 100,
    "stream": false
}
```

#### Response:
```json
{
   "id": "chatcmpl-8ca23289-da13-4374-87a4-9020f5bbbebe",
   "object": "chat.completion",
   "created": 1741649537,
   "model": "aimo-chat",
   "choices": [
      {
         "index": 0,
         "message": {
            "role": "assistant",
            "content": "Hello! It's nice to meet you. How's your day going so far?"
         },
         "delta": null,
         "finish_reason": "stop"
      }
   ],
   "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "total_tokens": 0
   }
}
```

## Contributing

We welcome contributions to improve AIMO! Please fork the repository, make changes, and submit a pull request. Ensure your code adheres to the project's coding standards.

## License

This project is licensed under the [MIT License](LICENSE).
