from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.qwen import load_qwen
from app.core.oauth2 import get_current_user

from app.schema.image import (
    ImageDescriptionResponse,
    ImageOCRResponse,
    ImageAnalysisResponse,
)

from app.services.image_description_service import (
    describe_uploaded_image_service,
)

from app.services.ocr_service import (
    perform_uploaded_image_ocr_service,
)

from app.services.image_combine_service import (
    analyze_both_service,
)


router = APIRouter(
    prefix="/api/v1/images",
    tags=["Images"],
)




@router.post(
    "/describe/{file_id}",
    response_model=ImageDescriptionResponse,
)
def describe_image(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    model, processor = load_qwen()

    return describe_uploaded_image_service(
        db=db,
        file_id=file_id,
        user_id=current_user.id,
        model=model,
        processor=processor,
    )




@router.post(
    "/ocr/{file_id}",
    response_model=ImageOCRResponse,
)
def ocr_image(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return perform_uploaded_image_ocr_service(
        db=db,
        file_id=file_id,
        user_id=current_user.id,
    )




@router.post(
    "/analyze/{file_id}",
    response_model=ImageAnalysisResponse,
)
def analyze_image(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    model, processor = load_qwen()

    return analyze_both_service(
        db=db,
        file_id=file_id,
        user_id=current_user.id,
        model=model,
        processor=processor,
    )