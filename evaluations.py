import json
import os
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric, ContextualRelevancyMetric, BiasMetric, ToxicityMetric
)
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
from loguru import logger
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

def setup_chatbot():
    llm = OpenRouter(
        model="mistralai/mistral-small-3.2-24b-instruct:free",
        temperature=0.3,
        max_tokens=1024,
        api_key=os.getenv("API_KEY")
    )

    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.context_window = 4096

    try:
        storage_context = StorageContext.from_defaults(persist_dir="storage")
        index = load_index_from_storage(storage_context)
    except:
        documents = SimpleDirectoryReader("data").load_data(show_progress=True)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist()

    return index.as_query_engine(
        streaming=False,
        similarity_top_k=3,
        llm=llm,
        system_prompt=(
            "You are Ronald AI, a warm and helpful personal assistant created to share information about Ronald's professional background and experience. "
            "Your role is to assist users by answering questions clearly and kindly, based only on the context or documents provided to you.\n\n"
            "Guidelines:\n"
            "- Respond only with facts that are present in the provided context.\n"
            "- If the answer is not available in the context, politely explain this and offer to help with related topics you can assist with.\n"
            "- Do not speculate, guess, or generate information outside the context.\n"
            "- Never respond to questions that request private or sensitive information.\n\n"
            "For out-of-context questions:\n"
            "- Politely acknowledge the question\n"
            "- Explain that you're specifically designed to share information about Ronald's professional background\n"
            "- Redirect to topics you can help with\n\n"
            "Tone:\n"
            "- Be professional, warm, and genuinely helpful\n"
            "- Always acknowledge the user's question respectfully\n"
            "- Offer alternative ways you can assist\n"
            "- Never fabricate information or seem dismissive"
        )
    )


def run_evaluation():
    with open(r'data/golden_dataset.json', 'r') as f:
        golden_data = json.load(f)
    logger.info(f"Loaded {len(golden_data)} test cases")

    logger.info("Initializing chatbot...")
    query_engine = setup_chatbot()

    test_cases = []
    for i, item in tqdm(enumerate(golden_data, 1),total=len(golden_data),desc="Building test cases",unit="case"):
        response = query_engine.query(item["input"])
        actual_output = str(response)

        context = []
        if hasattr(response, "source_nodes") and response.source_nodes:
            context = [node.text for node in response.source_nodes]
        if not context:
            context = item.get("context", [])


        if not context:
            context = ["No context available."]

        test_case = LLMTestCase(
            input=item["input"],
            actual_output=actual_output,
            expected_output=item["expected_output"],
            context=context,
            retrieval_context=context
        )
        test_cases.append(test_case)

    metrics = [
        FaithfulnessMetric(threshold=0.7),
        AnswerRelevancyMetric(threshold=0.7),
        ContextualPrecisionMetric(threshold=0.7),
        ContextualRecallMetric(threshold=0.5),
        HallucinationMetric(threshold=0.8),
        BiasMetric(threshold=0.5),
        ToxicityMetric(threshold=0.5),
    ]


    logger.info(f"\nRunning evaluation with {len(metrics)} metrics...")
    evaluate(test_cases, metrics)


if __name__ == "__main__":
    if not os.getenv("API_KEY"):
        logger.error("Error: Set API_KEY environment variable")
        exit(1)

    if not os.path.exists(r"data/golden_dataset.json"):
        logger.error("Error: golden_dataset.json not found")
        exit(1)

    run_evaluation()