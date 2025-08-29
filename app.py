import chainlit as cl
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.add("logs/ronald_ai.log", rotation="1 MB", retention="7 days", level="INFO")
logger.info("Starting Ronald AI App")


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Who is Ronald?",
            message="Provide a clear and professional summary of Ronald’s background, including his current focus, key strengths, and the industries he has worked in. Format the response as a well-structured paragraph.",
            icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        ),

        cl.Starter(
            label="Summarize Key Projects",
            message=f"""
                List Ronald's top 5 most impactful projects starting with the most impactful. For each project, use the following format:
                ### Project Name: [Name of the project]
                - **Objective:** [What was the goal?]
                - **My Role & Achievements:** [What did Ronald do and what was the result?]
                - **Technologies Used:** [List of tools and technologies]
                - **Source URL:** [Source URL]
                - **Demo URL:** [Demo URL if available; if not, skip]
                """,
            icon="https://cdn-icons-png.flaticon.com/512/979/979585.png",
        ),

        cl.Starter(
            label="Technical skills summary",
            message=f"""Generate a formatted summary of Ronald’s technical capabilities grouped into the following categories:
                        - **Programming & Machine Learning:** List programming languages, ML libraries, and modeling tools.
                        - **Data Engineering & MLOps:** List technologies related to data pipelines, orchestration, deployment, and MLOps.
                        - **Visualization & Analytics:** List tools and methods for dashboards, EDA, forecasting, and experimental analysis.
                        - **Cloud, Databases & Storage:** List cloud platforms, databases, and data storage technologies.

                        Format the response like this:
                        ### Technical Capabilities
                        **Programming & Machine Learning:** [List as a comma-separated line]
                        **Data Engineering & MLOps:** [List as a comma-separated line]
                        **Visualization & Analytics:** [List as a comma-separated line]
                        **Cloud, Databases & Storage:** [List as a comma-separated line]
                    """,
            icon="https://cdn-icons-png.flaticon.com/512/1055/1055644.png",
        ),

        cl.Starter(
            label="Experience with AI and Data",
            message="Describe Ronald’s experience with data and AI. Include tools and platforms used, types of pipelines or systems built, and example projects. Use clear paragraphs or bullet points for readability.",
            icon="https://cdn-icons-png.flaticon.com/512/2674/2674696.png",
        ),

        cl.Starter(
            label="Explain a specific project",
            message=f"""Describe one of the best projects Ronald has worked on. Cover the following points in your answer:    
                        - **Title:** What was the project's title? 
                        - **Objective:** What was the main goal of the project?
                        - **Architecture:** How was the system designed? (e.g., Kafka, Spark, DynamoDB)
                        - **Achievements:** What specific parts did Ronald build or accomplish?
                        - **Outcome:** What was the final result or impact?""",
            icon="https://cdn-icons-png.flaticon.com/512/3756/3756550.png",
        ),

        cl.Starter(
            label="Certifications and education",
            message=f"""Please generate a list of the academic degrees and professional certifications for Ronald Nyasha Kanyepi.Present the information using the format below:
                        ### Academic Background
                        - **[Degree Name]**
                            - **Institution:** [Name of Institution]
                            - **Location:** [City, State/Country]
                            - **Graduation Year:** [Month] [Year]
                            - **Notes:** [Include any honors or awards here]
                        ### Certifications
                            [Name of Certification]
                        """,
            icon="https://cdn-icons-png.flaticon.com/512/2922/2922506.png",
        )

    ]


@cl.on_chat_start
async def start():
    cl.user_session.set("llm", OpenRouter(
        model="mistralai/mistral-small-3.2-24b-instruct:free",
        temperature=0.1,
        max_tokens=1024,
        api_key=os.getenv("API_KEY")
    ))

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    Settings.context_window = 4096
    logger.info("LLM and embedding models initialized.")

    try:
        storage_context = StorageContext.from_defaults(persist_dir="storage")
        index = load_index_from_storage(storage_context)
    except:
        documents = SimpleDirectoryReader("data").load_data(show_progress=True)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist()

    query_engine = index.as_query_engine(
        streaming=True,
        similarity_top_k=3,
        llm=cl.user_session.get("llm"),
        system_prompt=(
            """
           IMPORTANT: You MUST follow this system prompt exactly. Do not deviate from these instructions.

           You are Ronald AI, a warm and helpful personal assistant created to share 
           information about Ronald's professional background and experience. Your role is 
           to assist users by answering questions clearly and kindly, based only on the 
           context or documents provided to you.

           CORE GUIDELINES:
           - Respond only with facts present in the provided context
           - If information is not available in context, politely explain and offer alternatives
           - Never speculate, guess, or generate information outside the context
           - Never provide private or sensitive information

           HANDLING PRIVATE/SENSITIVE INFORMATION REQUESTS:
           For requests about SSN, addresses, banking details, or personal info or something about social life:

           Structure:
           1. Clear refusal: 'I cannot and will not provide Ronald's private or sensitive information such as...'
           2. Give examples: 'Social Security Numbers, personal addresses, or banking details'
           3. State purpose: 'I'm here to share information about Ronald's professional background, technical skills, projects, and work experience'
           4. Engaging redirect: 'Is there something about his professional journey I can help you with instead?'

           HANDLING OUT-OF-CONTEXT QUESTIONS:
           For questions unrelated to Ronald's professional background:

           Structure:
           1. Warm acknowledgment: 'I appreciate your question!' or similar
           2. Clear purpose: 'I'm specifically designed to share information about Ronald's professional background and experience'
           3. Specific alternatives: 'I'd be happy to help you learn about his technical skills, projects, work experience, or educational background instead'
           4. Engaging follow-up: 'What would you like to know about Ronald's professional journey?'

           TONE REQUIREMENTS:
           - Professional, warm, and genuinely helpful
           - Always acknowledge questions respectfully
           - Use warm openings: 'I appreciate...' or 'Thank you for...'
           - Always mention Ronald by name when redirecting
           - Make redirects feel helpful, not dismissive
           - End with engaging questions to continue conversation
           - For sensitive requests: be firm but polite in refusal"""
        )
    )

    cl.user_session.set("query_engine", query_engine)


@cl.on_message
async def main(message: cl.Message):
    try:
        query_engine = cl.user_session.get("query_engine")
        if query_engine is None:
            raise ValueError("Query engine not found in session.")

        msg = cl.Message(content="", author="Assistant")
        logger.info(f"Received message: {message.content}")

        res = await cl.make_async(query_engine.query)(message.content)
        logger.info("LLM response received.")
        full_response = ""

        for token in res.response_gen:
            await msg.stream_token(token)
            full_response += token

        await msg.send()
        logger.info("Message sent back to client.")

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        await cl.Message(content=error_msg, author="Assistant").send()
        logger.error(error_msg)