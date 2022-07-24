from .tags import TITLE_TAG, TEXT_TAG, EOS_TAG
from typing import Tuple


def get_title_and_text(generated_text) -> Tuple[str, str]:
    # так как при генерации тэг заголовка подставляется, он гарантированно присутствует
    _, content = generated_text.split(TITLE_TAG, maxsplit=1)
    if TEXT_TAG in content:
        title, content_without_title = content.split(TEXT_TAG, maxsplit=1)
    else:
        title = ""
        # Если по каким-то причинам не сгенерировался разделитель заголовка и текста,
        # будем считать, что весь результат генерации - текст без заголовка
        content_without_title = content
    text = content_without_title.split(EOS_TAG)[0]
    return title, text
