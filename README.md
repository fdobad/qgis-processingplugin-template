# Processing Plugin Template

Calling order

    1.  __init__.py
    2.  ProcessingPluginModule.py          
    3.  ProcessingPluginModule_provider.py 
    4.1  ProcessingPluginModule_algorithm.py
    4.2  ProcessingPluginModule_knapsack.py 

# Auto versioning at release

1. Setup `.gitattributes` so `git archive`:
1.1. Auto update files with commit_id if contains `__version__ = "$Format:%H$"` line

    file_name export-subst

1.2. Ignore files (or glob \*) when archiving

    file_name export-ignore

2. Commit, push & tag

    # do
    git commit
    git push
    git tag -a v0.0.3 -m 'message'
    git push origin v0.0.3

    # undo tag
    git push --delete origin v0.0.2
    git tag --delete v0.0.2

3. Archive adding the modified versioning file

    VERSION=${GITHUB_REF_NAME#v}
    sed -i -e "s/version=0.0.1/version=${VERSION}/" metadata.txt
    git archive --format=zip --prefix=archived/ --add-file=metadata.txt --output archive.zip HEAD

# Github Actions
Action1: Documentation build and deploy based on [this](https://github.com/actions/starter-workflows/blob/main/pages/jekyll-gh-pages.yml)  

Action2: Auto-release on pushing tags

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

# References

/usr/share/qgis/python/plugins/processing/algs/gdal
https://qgis.org/pyqgis/
https://docs.qgis.org/3.28/en/docs/user_manual/processing/scripts.html#input-and-output-types-for-processing-algorithms
https://www.faunalia.eu/en/blog/2019-07-02-custom-processing-widget
https://gis.stackexchange.com/questions/462616/qgis-processing-parameter-using-values-from-layer-feature-in-processing-plugin

