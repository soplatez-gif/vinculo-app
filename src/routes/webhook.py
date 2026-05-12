import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Form, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.session import get_db
from src.db.models import Patient, Conversation, Message, MessageRole, ConversationStatus
from src.services.llm import get_ai_response
from src.agents.prompt import build_system_prompt, DEMO_THERAPIST

router = APIRouter()

DEMO_THERAPIST_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

ROLE_MAP = {
    MessageRole.user: "user",
    MessageRole.assistant: "model",
}


def build_conversation_history(messages: list) -> list[dict]:
    return [
        {"role": ROLE_MAP[msg.role], "parts": [{"text": msg.content}]}
        for msg in messages
    ]


@router.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    patient_phone = From.replace("whatsapp:", "")
    incoming_text = Body.strip()

    print(f"📨 Mensaje de {patient_phone}: {incoming_text}")

    result = await db.execute(
        select(Patient).where(Patient.phone == patient_phone)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        patient = Patient(phone=patient_phone, therapist_id=DEMO_THERAPIST_ID)
        db.add(patient)
        await db.flush()

    result = await db.execute(
        select(Conversation).where(
            Conversation.patient_id == patient.id,
            Conversation.status == ConversationStatus.active,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            patient_id=patient.id,
            therapist_id=DEMO_THERAPIST_ID,
        )
        db.add(conversation)
        await db.flush()

    db.add(Message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=incoming_text,
    ))
    await db.flush()

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    recent_messages = list(reversed(result.scalars().all()))

    system_prompt = build_system_prompt(DEMO_THERAPIST)
    history = build_conversation_history(recent_messages)
    ai_response = await get_ai_response(system_prompt, history)

    db.add(Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=ai_response,
    ))
    conversation.last_message_at = datetime.now(timezone.utc).replace(tzinfo=None)

    print(f"🤖 Respuesta: {ai_response}")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{ai_response}</Message>
</Response>"""
