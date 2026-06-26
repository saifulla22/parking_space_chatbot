from openai import OpenAI
from langchain_openai import ChatOpenAI

HF_API_KEY = "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"
HF_BASE_URL = "https://router.huggingface.co/v1"
DEFAULT_MODEL = "Qwen/Qwen3-Next-80B-A3B-Instruct"


class LLM:
    """
    Standalone HuggingFace LLM client using the OpenAI-compatible API.
    Use this for direct calls outside of LangChain chains.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        self.client = OpenAI(
            base_url=HF_BASE_URL,
            api_key=HF_API_KEY,
        )
        self.model = model

    def ask(self, question: str) -> str:
        """
        Send a question to the model and return its text response.

        Args:
            question (str): The input question to ask the model.

        Returns:
            str: The model's text answer.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": question}],
        )
        return completion.choices[0].message.content.strip().replace("**", "")


def get_langchain_llm(model: str = DEFAULT_MODEL) -> ChatOpenAI:
    """
    Return a LangChain-compatible ChatOpenAI instance pointing to HuggingFace.
    Use this inside LangChain chains, RAG pipelines, and LangGraph nodes.
    """
    return ChatOpenAI(
        model=model,
        base_url=HF_BASE_URL,
        api_key=HF_API_KEY,
        temperature=0.7,
    )


if __name__ == "__main__":
    llm = LLM()
    print(llm.ask("What is the capital of France?"))
    print(llm.ask("Who painted the Mona Lisa?"))
