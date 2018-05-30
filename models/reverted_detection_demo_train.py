# This is based on
# https://github.com/wiki-ai/editquality/blob/master/ipython/reverted_detection_demo.ipynb
# and only looks at single diffs

print("Load observations from file")
from revscoring.utilities.util import read_observations

with open("observations.json.bz2", "wt") as dumpfile:
    training_features = list(read_observations(dumpfile))

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



from revscoring.scoring.models import GradientBoosting
is_approved = GradientBoosting(features, labels=[True, False],
                               version="Demo",
                               learning_rate=0.01,
                               max_features="log2",
                               n_estimators=700, max_depth=5,
                               population_rates={False: 0.5, True: 0.5},
                               scale=True, center=True)

training_unpacked = [(o["cache"], o["approved"]) for o in training_features]
is_approved.train(training_unpacked)



