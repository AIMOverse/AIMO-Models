import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class AIMO:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_path = "OEvortex/HelpingAI2.5-2B"
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        # Load Model
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)

    def get_response(self, chat:list):
        # tokenize the input
        inputs = self.tokenizer.apply_chat_template(
            chat,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate text
        outputs = self.model.generate(
            inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        # decode the output
        response = outputs[0][inputs.shape[-1]:]
        return self.tokenizer.decode(response, skip_special_tokens=True)