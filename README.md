# setting up autoversioning

1. define versions to update in `.gitattributes`

2. commit & tag

    git tag -a v0.0.1 -m 'message'

3. archive

    git archive --format=zip --prefix=archived/ --output archive.zip HEAD

# TRASH 

    git config filter.export-subst.clean "sed 's/\$Format:%d\$//g'"
    git config filter.export-subst.smudge cat
    git config filter.export-subst.required true
