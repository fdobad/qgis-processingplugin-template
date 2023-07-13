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
## github action to ammend a commit ?

    - name: Checkout
      uses: actions/checkout@master
      git config user.name github-actions
      git config user.email github-actions@github.com
      sed -i -e "s/version=0.0.1/version=${VERSION}/" metadata.txt
      git add metadata.txt
      git commit --amend --no-edit

## clean smudge filter ?

    git config filter.export-subst.clean "sed 's/\$Format:%d\$//g'"
    git config filter.export-subst.smudge cat
    git config filter.export-subst.required true
