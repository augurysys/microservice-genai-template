import os

SENTRY_MAX_TAGS_CHARACTERS = 200


class LogWrapper:
    def __init__(self, logger, raven_client=None, add_pod_name: bool = True):
        self.logger = logger
        self.raven_client = raven_client
        self.pod_name = ""
        self.request_id = ""
        if 'HOSTNAME' in os.environ and add_pod_name:
            self.pod_name = os.environ['HOSTNAME']

    def debug(self, message, tags=None, *args, **kwargs):
        self.logger.debug(f"{message} {self.format_tags(tags)}", *args, **kwargs)

    def info(self, message, tags=None, *args, **kwargs):
        self.logger.info(f"{message} {self.format_tags(tags)}", *args, **kwargs)

    def warning(self, message, tags=None, *args, **kwargs):
        self.logger.warning(f"{message} {self.format_tags(tags)}", *args, **kwargs)

    def error(self, message, tags=None, sentry=True, *args, **kwargs):
        self.logger.error(f"{message} {self.format_tags(tags)}", *args, **kwargs)
        if sentry:
            self.raven_client.captureMessage(message, tags=_clean_sentry_tags(tags))

    def critical(self, message, tags=None, sentry=True, *args, **kwargs):
        self.logger.critical(f"{message} {self.format_tags(tags)}", *args, **kwargs)
        if sentry:
            self.raven_client.captureMessage(message, tags=_clean_sentry_tags(tags))

    def exception(self, message, tags=None, sentry=True, *args, **kwargs):
        self.logger.exception(f"{message} {self.format_tags(tags)}", *args, **kwargs)
        if sentry:
            self.raven_client.captureMessage(message, tags=_clean_sentry_tags(tags))

    def enrich_tags(self, tags: dict):
        if tags is None:
            tags = {}
        if self.pod_name:
            tags.update({"pod_id": self.pod_name})
        if self.request_id:
            tags.update({"req_id": self.request_id})
        return tags

    def format_tags(self, tags):
        _tags = self.enrich_tags(tags)
        if not _tags:   # This will trigger if no tags were enriched
            return ""
        return ' '.join([f'[{key}={value}]' for key, value in _tags.items()])


# clean tags to avoid "invalid data" errors in sentry
def _clean_sentry_tags(tags):
    clean_tags = {}
    if tags is None:
        return clean_tags
    for tag, val in tags.items():
        val = str(val)
        clean_val = _limit_tag_characters(val)
        clean_tag = _remove_tag_invisible_characters(clean_val)
        clean_tags[tag] = clean_tag
    return clean_tags


# sentry tags can't contain invisible characters (Eg. \n)
def _remove_tag_invisible_characters(tag_text):
    tag_text_clean = list(s for s in tag_text if s.isprintable())
    return ''.join(tag_text_clean)


# sentry tags can't be longer than 200 characters
def _limit_tag_characters(tag_text):
    return tag_text[0:SENTRY_MAX_TAGS_CHARACTERS]
