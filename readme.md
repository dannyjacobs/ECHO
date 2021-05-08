# ECHO Web Page
The ECHO web page is built using jekyll and the miminal mistakes theme.


# Build
Build the site locally with
```
bundle install
```
and preview with
```
bundle exec jekyll serve
```

# Deploy
It is deployed to github pages by a github action, circumventing the default
GHP deploy because I want to use ruby gems which are not available in the
github build.

The build workflow happens automatically on pushing to the gh-pages-local-dev branch it builds the
site and pushes to gh-pages where it is deployed to dannycjacobs.github.io/ECHO.

The action setup is based on https://www.moncefbelyamani.com/making-github-pages-work-with-latest-jekyll/.
