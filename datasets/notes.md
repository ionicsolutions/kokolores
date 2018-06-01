# Notes

## Links FlaggedRevs

- [Extension:Flagged Revisions](https://www.mediawiki.org/wiki/Extension:FlaggedRevs) 
- latest configuration: [flaggedrevs.php](https://github.com/wikimedia/operations-mediawiki-config/blob/master/wmf-config/flaggedrevs.php)
- [FlaggedRevs Report December 2008](https://meta.wikimedia.org/wiki/FlaggedRevs_Report_December_2008)
- [How to query the API for flagged status and latest stable revision](https://en.wikipedia.org/w/api.php?action=help&modules=query%2Bflagged)

## Links revscoring
- [Graph of features and data sources](https://upload.wikimedia.org/wikipedia/commons/a/a6/Revision_scoring.metric_dependencies.svg)

## Quarry queries
- [FlaggedRevs table layout](https://quarry.wmflabs.org/query/27154)
- [Potentially rejected revisions](https://quarry.wmflabs.org/query/27161)
- [Manually approved revisions](https://quarry.wmflabs.org/query/27156)
- [All revisions since FlaggedRevs was activated](https://quarry.wmflabs.org/query/27173)

## Types of approvals and rejections

### Approvals
Most revisions are autoreviewed (`fr_flag LIKE '%auto%`) because the editor is a member of
the group *autoreview* (called "Passiver Sichter" on dewiki).
These are of no interest here, as they are A) covered by ORES `editquality` models and B) do not
contribute to the backlog which we are trying to decrease (and C) are much more diverse than
the typical revisions we are looking at here).

There are single revisions which are approved individually (`fr_flag NOT LIKE '%auto%'`), but there are also
chains of revisions
by the same editor of which only the final revision is approved (which contains the whole set of changes).
Here, we need to look at all the changes since the last approved revision, rather than at the difference between
the marked revision and the one immediately preceding it. Note that this hides partial and complete reverts made
within the set of revisions, which is beneficial for our purpose. 

There is also the case where an editor's revision is modified by an experienced editor prior to being approved.
This is hard to find, as it can include partial reverts as well as substantial modification, e.g. perhaps only
the reference introduced is kept. Some *autoconfirmed* editors also have the habit to not approve a revision if
they plan on adding to the article anyway, e.g. they will approve only their own revision, even though the
previous revision was fine as well. In our problem context, these revisions could be seen as not particularly
relevant since a scoring model cannot make changes on its own anyway and should perhaps mark these revisions as
"edit with potential to become a useful contribution". **INVESTIGATE**

### Rejections
Quite often single revisions are reset to their approved parent.
There is also the case where a set of revisions by one or multiple editors is rejected.
This is straightforward to detect with `mwreverts`.

However, similar to the case where a set of revisions is approved, it might also be that
individual revisions are actually fine (e.g. there is a back-and-forth before the whole set is rejected,
and only later parts are restored). This is more difficult to detect, and it is currently unknown how
often this happens and whether these controversial cases should be reviewed based on `kokolores` scores at all.
**INVESTIGATE**

### Unapprovals
There are also revisions which are approved and later this decision is reversed.
These revisions are not present in the `flaggedrevs` table. This can be verified
by removing the approval from an old revision, query the database, approving
the revision again and looking at the database once again.

## Features specific to FlaggedRevisions

Potential new features to add to `revscoring`:
- number of revisions since the last approved revision
- number of reverts within the unapproved revision set
- is the editor of the last approved revision also the editor of the new revision
