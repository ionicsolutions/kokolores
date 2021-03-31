import utils
utils.prepare_environment()

from revscoring.features import wikitext, revision_oriented, temporal
from revscoring.languages import german

features = [
    # Catches long key mashes like kkkkkkkkkkkk
    wikitext.revision.diff.longest_repeated_char_added,
    # Measures the size of the change in added words
    wikitext.revision.diff.words_added,
    # Measures the size of the change in removed words
    wikitext.revision.diff.words_removed,
    # Measures the proportional change in "badwords"
    german.badwords.revision.diff.match_prop_delta_sum,
    # Measures the proportional change in "informals"
    german.informals.revision.diff.match_prop_delta_sum,
    # Measures the proportional change meaningful words
    german.stopwords.revision.diff.non_stopword_prop_delta_sum,
    # Is the user anonymous
    revision_oriented.revision.user.is_anon,
    # How long ago did the user register?
    temporal.revision.user.seconds_since_registration
]

extractor = utils.get_extractor("de")