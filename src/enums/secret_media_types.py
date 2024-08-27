from enum import IntEnum

__all__ = ('SecretMediaType',)


class SecretMediaType(IntEnum):
    PHOTO = 1
    VOICE = 2
    VIDEO = 3
    AUDIO = 4
    ANIMATION = 5
    DOCUMENT = 6
    VIDEO_NOTE = 7
    STICKER = 8
