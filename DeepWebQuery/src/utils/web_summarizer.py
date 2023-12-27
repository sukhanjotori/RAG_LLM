
from utils.utilities import count_num_tokens
from langchain.document_loaders import WebBaseLoader
from utils.load_config import LoadConfig
import openai
CFG = LoadConfig()


class WebSummarizer:
    """
    A class for summarizing PDF documents using OpenAI's ChatGPT engine.

    Attributes:
        None

    Methods:
        summarize_the_pdf:
            Summarizes the content of a PDF file using OpenAI's ChatGPT engine.

        get_llm_response:
            Retrieves the response from the ChatGPT engine for a given prompt.

    Note: Ensure that you have the required dependencies installed and configured, including the OpenAI API key.
    """
    @staticmethod
    def summarize_the_webpage(url: str):
        """
        Summarizes the content of a website using OpenAI's ChatGPT engine.

        Args:
            url (str): The URL of the webpage.

        Returns:
            str: The summary of the webpage.
        """

        loader = WebBaseLoader(url)
        docs = loader.load()
        print(f"Website length: {len(docs)}")
        max_summarizer_output_token = int(
            CFG.max_final_token/len(docs)) - CFG.token_threshold
        full_summary = ""
        counter = 1
        print("Generating the summary..")
        for i in range(len(docs)):
            # NOTE: This part can be optimized by considering a better technique for creating the prompt. (e.g: lanchain "chunksize" and "chunkoverlap" arguments.)
            if i == 0:  # For the first page
                prompt = docs[i].page_content + \
                    docs[i+1].page_content[:CFG.character_overlap]
            # For pages except the fist and the last one.
            elif i < len(docs)-1:
                prompt = docs[i-1].page_content[-CFG.character_overlap:] + \
                    docs[i].page_content + \
                    docs[i+1].page_content[:CFG.character_overlap]
            else:  # For the last page
                prompt = docs[i-1].page_content[-CFG.character_overlap:] + \
                    docs[i].page_content
            summarizer_llm_system_role = CFG.summarizer_llm_system_role.format(
                max_summarizer_output_token)
            full_summary += WebSummarizer.get_llm_response(
                CFG.summarizer_gpt_model,
                CFG.summarizer_temperature,
                summarizer_llm_system_role,
                prompt=prompt
            )
            print(f"Page {counter} was summarized. ", end="")
            counter += 1
        print("\nFull summary token length:", count_num_tokens(
            full_summary, model=CFG.summarizer_gpt_model))
        final_summary = WebSummarizer.get_llm_response(
            CFG.summarizer_gpt_model,
            CFG.summarizer_temperature,
            CFG.final_summarizer_llm_system_role,
            prompt=full_summary
        )
        return final_summary

    @staticmethod
    def get_llm_response(gpt_model: str, temperature: float, llm_system_role: str, prompt: str):
        """
        Retrieves the response from the ChatGPT engine for a given prompt.

        Args:
            gpt_model (str): The ChatGPT engine model name.
            temperature (float): The temperature parameter for ChatGPT response generation.
            summarizer_llm_system_role (str): The system role for the summarizer.
            max_summarizer_output_token (int): The maximum number of tokens for the summarizer output.
            prompt (str): The input prompt for the ChatGPT engine.

        Returns:
            str: The response content from the ChatGPT engine.
        """
        response = openai.ChatCompletion.create(
            engine=gpt_model,
            messages=[
                {"role": "system", "content": llm_system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
