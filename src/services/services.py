from collections.abc import Coroutine, Callable, Awaitable
from typing import Protocol, TypeAlias, Any, NewType
from uuid import UUID

from aiogram.types import Message, Update, User as FromUser

from exceptions import InvalidSecretMediaDeeplinkError
from models import SecretMediaType

__all__ = (
    'is_anonymous_messaging_enabled',
    'HasVideoPhotoAnimationVoiceAudioDocument',
    'HasFileID',
    'HasSendVideoPhotoAnimationVoiceAudioDocumentMethod',
    'determine_media_file_id_and_answer_method',
    'ReturnsMessage',
    'extract_secret_media_id',
    'determine_media_file',
    'get_message_method_by_media_type',
    'extract_user_from_update',
)

Url = NewType('Url', str)

ReturnsMessage: TypeAlias = Callable[..., Awaitable[Message]]


class HasSendVideoPhotoAnimationVoiceAudioDocumentMethod(Protocol):

    async def send_photo(
            self,
            chat_id: int | str,
            file_id: str,
            caption: str | None,
    ) -> Message: ...

    async def send_video(
            self,
            chat_id: int | str,
            file_id: str,
            caption: str | None,
    ) -> Message: ...

    async def send_animation(
            self,
            chat_id: int | str,
            file_id: str,
            caption: str | None,
    ) -> Message: ...

    async def send_voice(
            self,
            chat_id: int | str,
            file_id: str,
            caption: str | None,
    ) -> Message: ...

    async def send_audio(
            self,
            chat_id: int | str,
            file_id: str,
            caption: str | None,
    ) -> Message: ...

    async def send_document(
            self,
            chat_id: int | str,
            file_id: str,
            caption: str | None,
    ) -> Message: ...


class HasFileID(Protocol):
    file_id: str


class HasVideoPhotoAnimationVoiceAudioDocument(Protocol):
    photo: list[HasFileID]
    video: HasFileID | None
    animation: HasFileID | None
    voice: HasFileID | None
    audio: HasFileID | None
    document: HasFileID | None


def is_anonymous_messaging_enabled(state_name: str) -> bool:
    # rename it if state declaration will be changed
    # in anonymous_messaging.states.py file
    return state_name == 'AnonymousMessagingStates:enabled'


def determine_media_file_id_and_answer_method(
        bot: HasSendVideoPhotoAnimationVoiceAudioDocumentMethod,
        message: HasVideoPhotoAnimationVoiceAudioDocument,
) -> tuple[HasFileID, ReturnsMessage]:
    """Determine media type and answer method."""

    methods_and_medias = [
        (bot.send_video, message.video),
        (bot.send_animation, message.animation),
        (bot.send_voice, message.voice),
        (bot.send_audio, message.audio),
        (bot.send_document, message.document),
    ]
    if message.photo:
        methods_and_medias.append((bot.send_photo, message.photo[-1]))

    for method, media in methods_and_medias:
        if media is not None:
            return media.file_id, method
    raise ValueError('Unsupported media type')


def extract_secret_media_id(deep_link: str) -> UUID:
    try:
        return UUID(deep_link.split('-')[-1])
    except (ValueError, IndexError):
        raise InvalidSecretMediaDeeplinkError


def determine_media_file(message: Message) -> tuple[str, SecretMediaType]:
    medias_and_media_types: list[tuple[HasFileID, SecretMediaType]] = [
        (message.voice, SecretMediaType.VOICE),
        (message.video, SecretMediaType.VIDEO),
        (message.audio, SecretMediaType.AUDIO),
        (message.animation, SecretMediaType.ANIMATION),
        (message.document, SecretMediaType.DOCUMENT),
        (message.video_note, SecretMediaType.VIDEO_NOTE),
        (message.sticker, SecretMediaType.STICKER),
    ]
    if message.photo:
        medias_and_media_types.append(
            (message.photo[-1], SecretMediaType.PHOTO)
        )
    for media, media_type in medias_and_media_types:
        if media is not None:
            return media.file_id, media_type
    raise ValueError('Unsupported media type')


def get_message_method_by_media_type(
        *,
        message: Message,
        media_type: SecretMediaType,
) -> Callable[..., Coroutine[Any, Any, Message]]:
    media_type_to_method = {
        SecretMediaType.PHOTO: message.answer_photo,
        SecretMediaType.VOICE: message.answer_voice,
        SecretMediaType.ANIMATION: message.answer_animation,
        SecretMediaType.VIDEO: message.answer_video,
        SecretMediaType.VIDEO_NOTE: message.answer_video_note,
        SecretMediaType.STICKER: message.answer_sticker,
        SecretMediaType.DOCUMENT: message.answer_document,
        SecretMediaType.AUDIO: message.answer_audio,
    }
    try:
        return media_type_to_method[media_type]
    except KeyError:
        raise ValueError('Unsupported media type')


def extract_user_from_update(update: Update) -> FromUser:
    """Extract user from update.

    Args:
        update: Update object.

    Returns:
        User object.

    Raises:
        ValueError: If update type is unknown.
    """
    if update.message is not None:
        return update.message.from_user
    elif update.callback_query is not None:
        return update.callback_query.from_user
    elif update.inline_query is not None:
        return update.inline_query.from_user
    elif update.chosen_inline_result is not None:
        return update.chosen_inline_result.from_user
    else:
        raise ValueError('Unknown event type')
