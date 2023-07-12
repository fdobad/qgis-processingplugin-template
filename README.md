# setting up autoversioning

1. define versions to update in `.gitattributes`

2. commit & tag

    # ok
    git commit
    git push
    git tag -a v0.0.2 -m 'message'
    git push origin v0.0.2

    # undo tag
    git push --delete origin v0.0.2
    git tag --delete v0.0.2

3. archive

    git archive --format=zip --prefix=archived/ --output archive.zip HEAD

# TRASH 

    git config filter.export-subst.clean "sed 's/\$Format:%d\$//g'"
    git config filter.export-subst.smudge cat
    git config filter.export-subst.required true


