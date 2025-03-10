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

# Build Docker image with required API keys
docker build \
  --build-arg NEBULA_API_KEY=your_nebula_api_key \
  --build-arg HF_TOKEN=your_huggingface_token \
  -t aimoverse/aimo-emotion-model .

# Run the Docker container
docker run -p 80:80 -d aimoverse/aimo-emotion-model
```

## Deployment on Phala Network

To deploy AIMO on Phala Network, follow these steps:

1. Ensure you have the necessary API keys:
   - `NEBULA_API_KEY`: For accessing LLM API
   - `HF_TOKEN`: For downloading Hugging Face models

2. Build the Docker image with the required environment variables:

```bash
# Export your API keys as environment variables
export NEBULA_API_KEY="your_nebula_api_key_here"
export HF_TOKEN="your_huggingface_token_here"

# Build the Docker image
docker build \
  --build-arg NEBULA_API_KEY=$NEBULA_API_KEY \
  --build-arg HF_TOKEN=$HF_TOKEN \
  -t aimoverse/aimo-emotion-model .
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

| Variable | Description | Required |
|----------|-------------|----------|
| `NEBULA_API_KEY` | API key for LLM service | Yes |
| `HF_TOKEN` | Hugging Face access token for downloading models | Yes |

## Usage

Start the AIMO server using the following command:

```bash
# If installed directly
fastapi run app/main.py

# If using Docker
docker run -p 80:80 \
  -e NEBULA_API_KEY=your_key \
  -e HF_TOKEN=your_token \
  -d aimoverse/aimo-emotion-model
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
    "role": "assistant",
    "content": "Hi there! How can I help you today?"
}
```

## Contributing

We welcome contributions to improve AIMO! Please fork the repository, make changes, and submit a pull request. Ensure your code adheres to the project's coding standards.

## License

This project is licensed under the [MIT License](LICENSE).
