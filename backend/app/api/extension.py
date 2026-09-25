from fastapi import APIRouter, HTTPException, status

from ..schemas.extension import QuickVerifyRequest, QuickVerifyResponse
from ..services import ai_service
from ..services.trust_score_service import calculate_trust_score
from ..services.verification_service import verify_claims

router = APIRouter(prefix="/api/ext", tags=["extension"])


@router.post("/quick-verify", response_model=QuickVerifyResponse)
async def quick_verify(request: QuickVerifyRequest):
    if not request.text and not request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either text or url",
        )

    text = request.text
    if not text and request.url:
        text = await ai_service.extract_text_from_url(request.url)

    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text for verification",
        )

    # Run AI inference directly
    ai_result = ai_service.analyze_text(text)

    # Mocking claims extraction for quick verification, normally would be NLP
    claims = [text[:100] + "..."] if len(text) > 100 else [text]

    # Run source verification directly
    verification = await verify_claims(claims)

    # Calculate score
    score_result = calculate_trust_score(ai_result, verification)

    return QuickVerifyResponse(
        score=score_result.get("score"),
        classification=score_result.get("classification", "Unverified"),
        confidence=ai_result.get("confidence", 0.0),
        evidence_count=verification.get("evidence_count", 0) if verification else 0,
        summary=ai_result.get("summary", ""),
    )
