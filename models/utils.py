import enchant
import mwapi
from revscoring.extractors import api

USER_AGENT = "kokolores training <kokolores.training@tools.wmflabs.org>"


def prepare_environment():
    # Use locally installed dictionaries
    enchant.set_param("enchant.myspell.dictionary.path",
                      r"/data/project/kokolores/dicts/usr/share/myspell/dicts/")


def get_extractor(lang="de"):
    session = mwapi.Session("https://%s.wikipedia.org" % lang,
                            user_agent=USER_AGENT)
    return api.Extractor(session)