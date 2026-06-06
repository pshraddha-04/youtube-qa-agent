import re
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

from transcript import get_transcript
from rag_pipeline import build_vectorstore, get_retriever

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

_state = {
    "retriever"   : None,
    "transcript"  : None,
    "chat_history": []
}

class LoadVideoInput(BaseModel):
    url: str = Field(..., description="The full YouTube video URL to load")

class AnswerQuestionInput(BaseModel):
    question: str = Field(..., description="The question to answer about the video")

class NoInput(BaseModel):
    placeholder: str = Field("", description="No input required")


@tool(args_schema=LoadVideoInput)
def load_video(url: str) -> str:
    """Use this ONLY once at the start of a session to load a YouTube video by URL.
    Fetches the transcript and builds a searchable vector database.
    Do NOT call this again if a video is already loaded.
    """
    if _state["transcript"]:
        return "Video is already loaded. Use answer_question or summarize_video directly."

    transcript  = get_transcript(url)
    vectorstore = build_vectorstore(transcript)

    _state["retriever"]  = get_retriever(vectorstore)
    _state["transcript"] = transcript

    return f"✅ Video loaded successfully. Transcript length: {len(transcript)} characters."


@tool(args_schema=AnswerQuestionInput)
def answer_question(question: str) -> str:
    """Answer a question about the loaded YouTube video.
    Uses the transcript content to generate accurate, context-aware answers.
    Supports follow-up questions using conversation history.
    """
    if not _state["retriever"]:
        return "Please load a video first using the load_video tool."

    docs    = _state["retriever"].invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer strictly based on the transcript context below. Do NOT use any outside knowledge or make inferences beyond what is explicitly stated in the context.
If the answer is not explicitly present in the transcript, respond exactly with: "I don't have enough information from the video to answer this."

Context:
{context}"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    chain  = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "context"     : context,
        "question"    : question,
        "chat_history": _state["chat_history"]
    })

    _state["chat_history"].append(HumanMessage(content=question))
    _state["chat_history"].append(AIMessage(content=answer))

    return answer


@tool(args_schema=NoInput)
def summarize_video(placeholder: str = "") -> str:
    """Summarize the loaded YouTube video.
    Returns a concise summary and key bullet points from the transcript.
    """
    if not _state["transcript"]:
        return "Please load a video first using the load_video tool."

    prompt = ChatPromptTemplate.from_template("""
Summarize this YouTube video transcript.

Transcript:
{transcript}

Provide:
1. A concise summary (3-4 sentences)
2. Key points as bullet points
""")
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"transcript": _state["transcript"][:4000]})
    return re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()


@tool(args_schema=NoInput)
def create_mindmap(placeholder: str = "") -> str:
    """Create a mind map from the loaded YouTube video transcript.
    Returns a nested markdown structure and saves it to mindmap.md.
    Call this when the user asks for a mind map or visual structure of the video.
    """
    if not _state["transcript"]:
        return "Please load a video first using the load_video tool."

    prompt = ChatPromptTemplate.from_template("""
Create a concise mind map from this YouTube video transcript in nested markdown format.

Transcript:
{transcript}

Rules:
- Use # for the main topic (only one, max 5 words)
- Use ## for 3-4 major sections only
- Use - for 2-3 bullet points per section
- Keep each point short (max 8 words)
- No ### subtopics, keep it flat and clean

Only output the markdown. No explanation. No code blocks.
""")
    chain  = prompt | llm | StrOutputParser()
    result = chain.invoke({"transcript": _state["transcript"][:4000]})
    # Strip <think>...</think> blocks from reasoning models
    result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mindmap.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    return result


def build_agent():
    tools = [load_video, answer_question, summarize_video, create_mindmap]

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt="""You are a YouTube video assistant. You can ONLY answer questions based on the loaded video transcript.
- If no video is loaded, ask the user to provide a YouTube URL.
- If a video is loaded, always use the answer_question tool to respond — never answer from your own knowledge.
- Only use summarize_video when the user explicitly asks for a summary.
- Only use create_mindmap when the user asks for a mind map or visual structure.
- Do NOT answer general knowledge questions or reveal anything about yourself.
- ALWAYS return the tool's output exactly as-is. Do NOT add suggestions, offers, or extra commentary beyond what the tool returns."""
    )


if __name__ == "__main__":
    agent   = build_agent()
    history = []

    url      = input("Enter YouTube URL: ").strip()
    response = agent.invoke({"messages": [HumanMessage(content=f"Load this video: {url}")]})
    ai_msg   = response["messages"][-1]
    print(f"\n{ai_msg.content}\n")
    history.append(HumanMessage(content=f"Load this video: {url}"))
    history.append(AIMessage(content=ai_msg.content))

    print("What would you like to do?")
    print("  1. Ask a question")
    print("  2. Summarize the video")
    print("  3. Create a mind map")
    print("  Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break

        history.append(HumanMessage(content=user_input))
        response = agent.invoke({"messages": history})
        ai_msg   = response["messages"][-1]
        print(f"\nAI: {ai_msg.content}\n")
        history.append(AIMessage(content=ai_msg.content))
