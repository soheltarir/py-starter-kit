import structlog
from kink import di
from taskiq_dependencies import Depends

from src.application.dto.user_dto import WelcomeEmailTaskPayload
from src.application.services.user_service import UserService

logger = structlog.get_logger()

async def send_welcome_email_task(
        payload: WelcomeEmailTaskPayload,
        svc: UserService = Depends(lambda: di[UserService])
):
    user = await svc.get_user_by_email(payload.recipients[0])
    logger.info(f"Sending welcome email to {user.id}")
