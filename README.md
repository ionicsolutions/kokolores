# kokolORES

Exploring the use of data from [Flagged Revisions](https://www.mediawiki.org/wiki/Extension:FlaggedRevs) to create [ORES](https://www.mediawiki.org/wiki/ORES) models for the automatic review of edits on Wikipedia.

## What are Flagged Revisions?

[Flagged Revisions](https://www.mediawiki.org/wiki/Extension:FlaggedRevs) is a [MediaWiki](https://www.mediawiki.org) extension used by some language versions of [Wikipedia](https://www.wikipedia.org) and other Wikimedia projects to review edits.

There are several different ways in which Flagged Revisions are used on Wikipedia language versions. Some — most notably the [German-language Wikipedia](https://de.wikipedia.org) — require review of all edits by editors with no or a newly registered user account before they are shown to the general public, whereas many others only flag certain pages for review (e.g. the [English-language Wikipedia's](https://en.wikipedia.org) [pending changes](https://en.wikipedia.org/wiki/Wikipedia:Pending_changes) configuration). An overview of configurations can be seen [here on meta.wikimedia.org](https://meta.wikimedia.org/wiki/Requests_for_comment/Flagged_revisions_deployment#Statistics_from_Wikipedias_with_different_configurations) (2016), the latest configuration can be found in [flaggedrevs.php](https://github.com/wikimedia/operations-mediawiki-config/blob/master/wmf-config/flaggedrevs.php).

## What is ORES?

The [Objective Revision Evaluation Service](https://www.mediawiki.org/wiki/ORES) is a web service run by the Wikimedia Foundation's [Scoring Platform team](https://www.mediawiki.org/wiki/Wikimedia_Scoring_Platform_team). ORES provides different machine learning models to score edits made to Wikipedia. A comprehensive description of ORES, the motivation of its creators, and a description of some use cases can be found in [this 2018 paper](https://github.com/halfak/ores-paper).

## Why this project?

Data recorded through the use of Flagged Revisions constitutes a large, human-labeled dataset of accepted and rejected edits. Especially for Wikipedia language versions where a large number of edits have been reviewed, this is a potentially valuable resource for training machine learning models to judge edit quality. In a first step, `kokolores` will focus on the compilation and documentation of data sets from Flagged Revisions.

The use of Flagged Revisions — especially in the 'German' configuration where only reviewed edits are shown to the general public — has long been controversial for a variety of reasons which are summarized in the Wikimedia Foundation's [request for comment regarding new deployments of Flagged Revisions](https://meta.wikimedia.org/wiki/Requests_for_comment/Flagged_revisions_deployment). One of the problems faced by Wikipedias using Flagged Revisions is that the queue of yet-unreviewed edits grows very large and the need to review a large number of edits is a burden on the volunteer communities, most of which are shrinking.

For these Wikipedias, it has been proposed to use ORES to auto-review at least some of the edits to reduce the backlog ([T165848](https://phabricator.wikimedia.org/T165848)). In a second step, `kokolores` will investigate whether models trained on Flagged Revisions data can help to substantially reduce the backlog of edits awaiting review while maintaining a high level of accuracy. It will be especially interesting to compare their performance to models trained the general ORES edit quality data sets compiled through [Wiki labels](https://meta.wikimedia.org/wiki/Wiki_labels). (A first investigation of a model trained on a subset of Flagged Revisions data from the [Finnish-language Wikipedia](https://fi.wikipedia.org) is documented in [T166235](https://phabricator.wikimedia.org/T166235).)

If successful, in a potential third step, `kokolores` will facilitate the development of an interface between ORES and Flagged Revisions. This could be a [bot](https://meta.wikimedia.org/wiki/Bot) which is granted the right to review pages, or a more direct means.

This third step would open up the possibility to employ ORES on Wikipedias using the 'English' approach where only edits to specially marked pages require review. For this group of Wikipedias, the use of ORES to mark edits for review has been proposed in 2016 ([T150593](https://phabricator.wikimedia.org/T150593)), but the corresponding [patch](https://gerrit.wikimedia.org/r/#/c/326156/) was not deployed as the underlying [Deferred Changes](https://en.wikipedia.org/wiki/Wikipedia:Deferred_changes) process ([T118696](https://phabricator.wikimedia.org/T118696)) was never adopted by the English-language Wikipedia's community. A similar proposal which asks to flag edits for review based on ORES scores can be found in [T132901](https://phabricator.wikimedia.org/T132901). Note that in these cases, rather than using models trained on Flagged Revisions data, the full edit quality models already present in ORES are expected to be more suitable.



