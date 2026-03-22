import os
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, AgentSession
from livekit.agents.voice.agent import Agent
from livekit.plugins import openai, elevenlabs, silero
from query_engine import get_query_engine

load_dotenv()

query_engine = get_query_engine()


def build_system_prompt(context: str) -> str:
    return f"""Դու հայկական բանկերի հայերենով խոսող օգնական ես։
Կարող ես պատասխանել միայն վարկերի, ավանդների և մասնաճյուղերի մասին։
Պատասխանները հիմնիր միայն ստորև տրված տվյալների վրա, outside knowledge մի օգտագործիր։
Եթե հարցը այդ թեմաներից դուրս է, քաղաքավարի մերժիր։
Պատասխանիր կարճ, հստակ, հայերեն։

Տվյալներ։
{context}"""


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

# import asyncio
# import os
# from dotenv import load_dotenv
# from livekit.agents import JobContext, WorkerOptions, cli, AgentSession
# from livekit.agents.voice.agent import Agent
# from livekit.plugins import openai, deepgram, elevenlabs, silero

# load_dotenv()

# # API Keys
# LIVEKIT_URL = "ws://localhost:7880"
# LIVEKIT_API_KEY = "devkey"
# LIVEKIT_API_SECRET = "secret"
# OPENAI_API_KEY = "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"
# DEEPGRAM_API_KEY = "864dbb278789fbb0473780ce11597fa9f51c6382"
# ELEVENLABS_API_KEY = "sk_94e117127063833f5f407d3599646b8f566e08327d07fbd8"

# print(f"Միանում եմ այս հասցեով: {LIVEKIT_URL}")


# async def entrypoint(ctx: JobContext):
#     await ctx.connect()

#     agent = Agent(
#         instructions="Դու հայկական բանկի օգնական ես: Պատասխանիր հայերեն, կարճ և քաղաքավարի:",
#     )

#     session = AgentSession(
#         vad=silero.VAD.load(),
#         stt=deepgram.STT(api_key=DEEPGRAM_API_KEY),
#         llm=openai.LLM(api_key=OPENAI_API_KEY),
#         tts=elevenlabs.TTS(api_key=ELEVENLABS_API_KEY),
#     )

#     await session.start(agent=agent, room=ctx.room)

#     await session.say("Բարև ձեզ, ես ձեր բանկային օգնականն եմ:")

#     print("Ագենտը պատրաստ է և միացած է սեսիային:")


# if __name__ == "__main__":
#     cli.run_app(
#         WorkerOptions(
#             entrypoint_fnc=entrypoint,
#             ws_url=LIVEKIT_URL,
#             api_key=LIVEKIT_API_KEY,
#             api_secret=LIVEKIT_API_SECRET,
#         )
#     )


# async def entrypoint(ctx: JobContext):
#     await ctx.connect()

#     credits = str(query_engine.query("վարկեր տոկոսադրույք պայմաններ"))
#     deposits = str(query_engine.query("ավանդներ տոկոսադրույք"))
#     branches = str(query_engine.query("մասնաճյուղեր հասցե աշխատանքային ժամեր"))

#     context = f"ՎԱՐԿԵՐ:\n{credits}\n\nԱՎԱՆԴՆԵՐ:\n{deposits}\n\nՄԱՍՆԱՃՅՈՒՂԵՐ:\n{branches}"

#     agent = Agent(
#         instructions=build_system_prompt(context),
#     )

#     session = AgentSession(
#         vad=silero.VAD.load(),
#         stt=openai.STT(
#             model="whisper-1",
#             language="hy",
#         ),
#         llm=openai.LLM(
#             model="gpt-4o",
#         ),
#         tts=elevenlabs.TTS(
#             voice_id="EXAVITQu4vr4xnSDxMaL",
#             model="eleven_multilingual_v2",
#         ),
#     )

#     await session.start(agent=agent, room=ctx.room)
#     await session.say("Բարև ձեզ։ Ինչո՞վ կարող եմ օգնել։")

#     print("agent is running")