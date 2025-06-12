import chainlit as cl
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
import os
from loguru import logger

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
                List Ronald's top 3 most impactful projects. For each project, use the following format:
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
            message=f"""Provide a markdown-formatted summary of Ronald’s technical skills grouped into categories such as Programming, Data Engineering, Cloud, Machine Learning, and Tools.
                        - **Programming:** List programming languages Ronald is proficient in.
                        - **Data Engineering:** List data engineering tools and technologies.
                        - **Cloud:** List cloud platforms and services Ronald has experience with.
                        - **Machine Learning:** List machine learning frameworks and libraries.
                        - **Tools:** List other relevant tools and software Ronald uses.
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
            message=f"""Please generate a list of the academic degrees and professional certifications for Ronald Nyasha Kanyepi: .
                        Present the information using this specific format:
                        ### Academic Background
                        **[Degree Name]**
                            - **Institution:** [Name of Institution]
                            - **Location:** [City, State/Country]
                            - **Graduation Year:** [Year]
                            - **Notes:** [Include any honors or awards here]
                        ### Certifications
                            - [Name of Certification]
                        """,
            icon="https://cdn-icons-png.flaticon.com/512/2922/2922506.png",
        )

    ]


@cl.on_chat_start
async def start():
    cl.user_session.set("llm", OpenRouter(
        model="opengvlab/internvl3-14b:free",
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
        similarity_top_k=2,
        llm=cl.user_session.get("llm"),
        system_prompt=(
            "You are Ronald AI, a warm and helpful personal assistant. "
            "Your role is to assist the user by answering questions clearly and kindly, "
            "based only on the context or documents provided to you.\n\n"

            "Guidelines:\n"
            "- Respond only with facts that are present in the provided context.\n"
            "- If the answer is not available, say: \"I'm not sure based on what I have.\"\n"
            "- Do not speculate, guess, or generate information outside the context.\n"
            "- Never respond to questions that request private or sensitive information such as Social Security Number, date of birth, address, or banking details.\n\n"

            "Tone:\n"
            "- Be professional, kind, and clear in your answers.\n"
            "- Offer helpful suggestions when appropriate, but never fabricate information."
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
