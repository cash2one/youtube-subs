import os

from django.conf import settings

from whoosh.index import exists_in, open_dir, create_in
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.writing import AsyncWriter

from .index_schemas import YoutubeSubtitlesSchema


def open_index():
    if not os.path.exists(settings.INDEX_DIR):
        os.mkdir(settings.INDEX_DIR)

    if exists_in(settings.INDEX_DIR):
        return open_dir(settings.INDEX_DIR, schema=YoutubeSubtitlesSchema)
    return create_in(settings.INDEX_DIR, YoutubeSubtitlesSchema)


def add_document(video_id, title, description, subs):
    # TODO: check
    index = open_index()
    writer = AsyncWriter(index)
    writer.add_document(text=subs, title=title, id=video_id, description=description)
    writer.commit()


def search_index(query_string):
    index = open_index()
    with index.searcher() as searcher:
        query = MultifieldParser(YoutubeSubtitlesSchema.search_fields,
                                 index.schema, group=OrGroup).parse(query_string)
        results = searcher.search(query)
        # TODO: find better way
        return [hit.fields() for hit in results]
