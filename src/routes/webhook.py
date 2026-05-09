from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    # Por ahora solo echo. El sábado conectamos IA.
    print(f"Mensaje de {From}: {Body}")

    twiml = f"""<Response>
        <Message>Recibido: {Body}</Message>
    </Response>"""
    return twiml.strip()