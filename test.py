import mwapi

from revscoring.revscoring.extractors.api.extractor import Extractor
from revscoring.revscoring.features import wikitext

session = mwapi.Session("https://de.wikipedia.org",
                        user_agent="Kokolores Testing <kilian.kluge@wikipedia.de>")

e = Extractor(session)

for u in e.extract(179414094, [wikitext.revision.diff.words_added,
                               wikitext.revision.diff.words_removed,
                               wikitext.revision.diff.longest_repeated_char_added]):
    print(u)
