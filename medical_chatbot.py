from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl


@cl.on_chat_start
async def on_chat_start():
    
    # Sending an image with the local file path
    elements = [
    cl.Image(name="image1", display="inline", path="gemma.jpeg")
    ]
    await cl.Message(content="Hello there, I am ur Virtual Doctor . How can I help you ?", elements=elements).send()
    model = Ollama(model="biomistral:latest")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()



def word_matching_feedback_system(user_text, reference_text):
    preprocess = lambda text: [token.strip('.,!?') for token in text.lower().split()]
    user_tokens, reference_tokens = preprocess(user_text), preprocess(reference_text)
    
    feedback = [f"Good job! You used the word '{word}'." if word in user_tokens else f"Try to include the word '{word}'." for word in reference_tokens]
    
    feedback.append(f"Overall similarity score: {calculate_similarity(user_text, reference_text):.2f}")
    return feedback

def calculate_similarity(text1, text2):
    return 0.85  # Placeholder similarity score

# Example Usage
user_text = "The cat chased the mouse."
reference_text = "The cat was chasing a mouse."
feedback = word_matching_feedback_system(user_text, reference_text)
for message in feedback:
    print(message)



