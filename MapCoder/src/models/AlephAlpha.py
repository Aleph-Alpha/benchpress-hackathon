import os
import time

from .Base import BaseModel
from aleph_alpha_client import Client, CompletionRequest, Prompt
import json



class AlephAlpha(BaseModel):
    def __init__(self, temperature=0):
        rel_path = os.path.join(os.path.dirname(__file__), "keys.json")

        with open(rel_path, 'r') as f:
            keys = json.load(f)

        self.client = Client(keys['AA_TOKEN'])
        self.model = "llama-3.1-70b-instruct-long-context"

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def prompt(self, processed_input):
        for i in range(10):
            try:
                request = CompletionRequest(
                    prompt=Prompt.from_text(processed_input[0]['content']),
                    maximum_tokens=5000,
                )

                # API reference for the client:
                # https://aleph-alpha-client.readthedocs.io/en/latest/
                response = self.client.complete(request, model=self.model)
                return response.completions[0].completion, 0, 0
            except Exception as e:
                time.sleep(2)
                print(e)
        return response.text, 0, 0
