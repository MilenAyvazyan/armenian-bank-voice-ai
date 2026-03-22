import os
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, AgentSession
from livekit.agents.voice.agent import Agent
from livekit.plugins import openai, elevenlabs, silero
from query_engine import get_query_engine

load_dotenv()

query_engine = get_query_engine()

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    system_prompt = """You are a voice assistant for Armenian banks. You speak Armenian.
Only answer questions about credits, deposits, and branch locations.
Base all answers strictly on the provided bank data below. Do not use outside knowledge.
If the question is outside these topics, politely decline in Armenian.
Keep answers short and clear. Always respond in Armenian.
Always say numbers and dates in Armenian words, not digits.

Bank name mappings - treat these as the same:
- "Ameriabank", "ամերիաբանկ", "ամերյաբանք", "ամերիա" = Ameriabank
- "ACBA", "ակբա", "ակբաբանկ", "ագբա", "ակպա" = ACBA
- "InecoBank", "ինեկո", "ինեքո", "ինեկոբանկ" = InecoBank"""

    credits = str(query_engine.query("վարկեր տոկոսադրույք պայմաններ գումար"))
    deposits = str(query_engine.query("ավանդներ տոկոսադրույք ժամկետ"))
    branches = str(query_engine.query("մասնաճյուղեր հասցե Երևան աշխատանքային ժամեր"))

    full_prompt = f"""{system_prompt}

Below is the bank data you must base your answers on.

CREDITS:
{credits}

DEPOSITS:
{deposits}

BRANCHES:
{branches}"""

    agent = Agent(instructions=full_prompt)

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model="whisper-1", language="hy"),
        llm=openai.LLM(model="gpt-4o"),
        tts=elevenlabs.TTS(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model="eleven_multilingual_v2",
        ),
    )

    await session.start(agent=agent, room=ctx.room)
    await session.say("Բարև ձեզ։ Ինչո՞վ կարող եմ օգնել։")

    print("agent is running")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
        )
    )
