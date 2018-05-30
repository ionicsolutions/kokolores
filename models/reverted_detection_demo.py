# This is based on
# https://github.com/wiki-ai/editquality/blob/master/ipython/reverted_detection_demo.ipynb
# and only looks at single diffs
import json
import sys
import mwapi

import enchant
enchant.set_param("enchant.myspell.dictionary.path", r"/data/project/kokolores/dicts/usr/share/myspell/dicts/")
d = enchant.Dict("de-DE")

print("Load dataset...")
with open("../datasets/datasets/temp.js", "r") as datafile:
    dataset = json.load(datafile)

length = len(dataset)
print("Loaded dataset of length %d" % length)
training_set = dataset[:int(length/1.33)]
testing_set = dataset[int(length/1.33):]

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
    # Is the user a bot or a sysop
    revision_oriented.revision.user.in_group({'bot', 'sysop'}),
    # How long ago did the user register?
    temporal.revision.user.seconds_since_registration
]

session = mwapi.Session("https://de.wikipedia.org",
                        user_agent="kokolores training <kokolores.training@tools.wmflabs.org>")

from revscoring.extractors import api
api_extractor = api.Extractor(session)

print("Extracting training features")
training_features = []
for rev_id, approved, _ in training_set:
    try:
        feature_values = list(api_extractor.extract(rev_id, features))
        observation = {"rev_id": rev_id, "cache": feature_values, "approved": approved}
    except RuntimeError as e:
        sys.stderr.write(str(e))
    else:
        print(observation)
        training_features.append(observation)

print("Dump observations to file")
from revscoring.utilities.util import dump_observation, read_observations
import bz2

with open("observations.json.bz2", "wt") as dumpfile:
    for observation in training_features:
        dump_observation(observation, dumpfile)
