from fastapi import APIRouter, Header


router = APIRouter()


@router.get("/locale")
async def get_locale(accept_language: str | None = Header(None)):
    # Very simple locale detection: prefer fa if present, else en
    if accept_language and "fa" in accept_language.lower():
        return {"locale": "fa", "rtl": True, "calendar": "jalali", "currency": "IRR"}
    return {"locale": "en", "rtl": False, "calendar": "gregorian", "currency": "USD"}








