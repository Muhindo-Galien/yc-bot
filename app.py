
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Bot, Dispatcher, html
from src.helper import load_embeddings
from src.prompt import system_prompt
from langchain_openai import OpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os
import logging
import asyncio
import sys

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize RAG components
embeddings = load_embeddings()
vector_store = PineconeVectorStore.from_existing_index(
    index_name="yc-bot-db",
    embedding=embeddings
)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Initialize LLM and RAG chain
llm = OpenAI(temperature=0.4, max_tokens=500)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

class Reference:
    '''
    A class to store previously response from the chatGPT openAI API
    '''
    def __init__(self):
        self.response = ""

    def add_reference(self, text: str, url: str):
        self.response += f"{text}\n{url}\n"

    def get_reference(self):
        return self.reference

reference = Reference()

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()



@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

def clear_past_conversation():
    reference.reference = ""

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer("""
    Hey, I'm YC Bot, your personal assistant for the Y Combinator.
    I can answer questions about the Y Combinator.
    """)

@dp.message(Command("clear"))
async def clear_handler(message: Message) -> None:
    clear_past_conversation()
    await message.answer("Conversation cleared!")


@dp.message()
async def rag_message(message: Message):
    """
    This function will handle the message from the user and send it to the RAG system
    """
    # Get the message from the user
    user_message = message.text
    print(f">>> User message: {user_message}")

    try:
        # Use RAG chain to get response
        response = rag_chain.invoke({"input": user_message})
        result = response["answer"]
        
        print(f">>> RAG Response: {result}")
        reference.response = result
        await message.answer(result)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        await message.answer("Sorry, I encountered an error processing your question.")

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Ensure webhook is removed before starting polling to avoid conflicts
    await bot.delete_webhook(drop_pending_updates=True)

    # And the run events dispatching
    await dp.start_polling(bot, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())