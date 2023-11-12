import asyncio
import logging as lg
import time
import uuid

import httpx
from fastapi import FastAPI

from src.initialize import initialize_app, initialize_logging
from src.utils import timeit

initialize_logging()

APP = FastAPI()

INIT_OBJECTS = initialize_app()

DEFAULT_INPUT_QUERY = (
    "¿Es de aplicación la ley de garantía integral de la libertad sexual a niños (varones) menores de edad "
    "víctimas de violencias sexuales o solo a niñas y mujeres?"
)


@APP.get("/healthcheck")
@timeit
async def healthcheck():
    """Asynchronous Health Check"""
    # TODO: healthcheck with embeddings db api and llm api
    return {"status": "OK"}


@APP.get("/semantic_search")
@timeit
async def semantic_search(input_query: str = DEFAULT_INPUT_QUERY):
    logger = lg.getLogger(semantic_search.__name__)
    logger.info(input_query)
    docs = await INIT_OBJECTS.vector_store.asimilarity_search_with_score(
        query=input_query, k=INIT_OBJECTS.config_loader["top_k_results"]
    )
    logger.info(docs)
    return docs


async def a_request_get(url):
    """Requests for sync/async load tests"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        return response.text


@APP.get("/qa")
@timeit
async def qa(input_query: str = DEFAULT_INPUT_QUERY):
    logger = lg.getLogger(qa.__name__)
    logger.info(input_query)

    # Getting context from embedding database (Qdrant)
    docs = await INIT_OBJECTS.vector_store.asimilarity_search_with_score(
        query=input_query, k=INIT_OBJECTS.config_loader["top_k_results"]
    )

    # Generate response using a LLM (OpenAI)
    context_preprocessed = [
        {"context": doc[0].page_content, "score": doc[1]} for doc in docs
    ]
    response = await INIT_OBJECTS.openai_client.chat.completions.create(
        model=INIT_OBJECTS.config_loader["llm_model_name"],
        messages=[
            {"role": "system", "content": INIT_OBJECTS.config_loader["prompt_system"]},
            {
                "role": "system",
                "content": INIT_OBJECTS.config_loader["prompt_system_context"],
            },
            {"role": "system", "content": "A continuación se proporciona el contexto:"},
            {"role": "system", "content": str(context_preprocessed)},
            {
                "role": "system",
                "content": "A continuación se proporciona la pregunta del usuario:",
            },
            {"role": "user", "content": input_query},
        ],
        temperature=INIT_OBJECTS.config_loader["temperature"],
        seed=INIT_OBJECTS.config_loader["seed"],
        max_tokens=INIT_OBJECTS.config_loader["max_tokens"],
    )
    answer = response.choices[0].message.content
    logger.info(answer)
    logger.info(response.usage)

    response_payload = dict(
        scoring_id=str(uuid.uuid4()),
        context=docs,
        answer=answer,
    )
    return response_payload


@APP.get("/sleep")
@timeit
async def sleep():
    time.sleep(5)
    return {"status": "OK"}


@APP.get("/asleep")
@timeit
async def asleep():
    await asyncio.sleep(5)
    return {"status": "OK"}
