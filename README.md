# AIMO: Emotional Companion Language Model Backends

AIMO is a lightweight, large-language model backend designed to provide emotional companionship through conversations. It is optimized for generating empathetic and engaging responses, making it an ideal solution for emotional companion toys and applications.

## Features

- **Emotional Engagement**: Provides empathetic and meaningful responses to user inputs, fostering an emotional connection.
- **Lightweight and Efficient**: Optimized for performance on devices with GPU or CPU, ensuring smooth interactions.
- **Customizable**: Easily adaptable for specific use cases or personalized prompts, enabling tailored interactions.

## Installation

Follow the steps below to set up AIMO on your system:

```bash
# Clone the repository
git clone https://github.com/AIMOverse/AIMO-Models.git
cd AIMO-Models

# Install dependencies
pip install -r requirements.txt
```

## Usage

Start the AIMO server using the following command:

```bash
python main.py
```

Once the server is running, you can integrate it with your applications or test it through API endpoints.

## API Overview

The AIMO backend provides a RESTful API for interaction. Below is an example of the main endpoint:

### Endpoint: `/chat/`

#### Method: `POST`

#### Request Body:
```json
{
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_new_tokens": 100
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
