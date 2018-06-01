# kokolORES data sets

Description of all `kokolores` benchmark data sets.

## dewiki_10000

### Summary

- 10 000 revisions
  - approved: 7 236 (72.36%)
  - rejected: 2 764 (27.64%)

### Creation

The data set was created by randomly drawing `page_id`s from the `page`
table. For each page, all manually approved revisions were recorded as
*approved* revisions. All revisions which were never reviewed were
considered as candidates for *rejected* revisions. Of those, only those
were added to the data set which were indeed reverted within the next
five revisions, were not reverted by the revision editors themselves, and
were never recorded as the target of a reversion. This process was continued
until the desired data set size was reached.

### Notes
- No care was taken to obtain a balanced data set.
- Only revisions made after the start of FlaggedRevs on `dewiki` in
  May 2008 were considered.
- Note that there are many pages which only contain revisions by editors
  with the `autoreview` right and are thus not part of the data set.

### Comments & Use
Since all revisions of a page were inspected, the data set includes
revisions across 10 years of use of FlaggedRevs on `dewiki`. Due to
the random selection pages, a fair distribution from heavily edited
to seldomly visited pages can be assumed.
