# Auto versioning at release

With github actions

1. Setup `.gitattributes` to:

1.1. Auto update files with commit_id if contains `__version__ = "$Format:%H$"` line

    file_name export-subst

  1.2. Ignore file (or glob *) when git archiving

    file_name export-ignore

2. Commit, push & tag

        # do
        git commit
        git push
        git tag -a v0.0.2 -m 'message'
        git push origin v0.0.2
    
        # undo tag
        git push --delete origin v0.0.2
        git tag --delete v0.0.2

3. Archive adding the modified versioning file

        VERSION=${GITHUB_REF_NAME#v}
        sed -i -e "s/version=0.0.1/version=${VERSION}/" metadata.txt
        git archive --format=zip --prefix=archived/ --add-file=metadata.txt --output archive.zip HEAD

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
