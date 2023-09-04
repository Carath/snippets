# Git repository backup

*Small utility to backup git repositories.*

Supported sites:
- [Github](https://github.com)
- [Gitlab](https://about.gitlab.com)
- [BitBucket](https://bitbucket.org)

Limitations:
- Only public data is fetched, therefore no token is needed.
- Gitlab doesn't allow to get starred projects without a token, and BitBucket seems to not support that feature.

Possible improvements:
- [Github] sort starred by category (if available). Note: this is doable but needs doing more requests and html parsing.


## Installation

This requires [python 3.6+](https://www.python.org/downloads/) and [pip3](https://pypi.org/project/pip/) installed. Run the following command:

```sh
pip3 install -r requirements.txt
```

## Usage examples

All fetched repositories will be saved in the ``` backups/ ``` directory.

To backup a given repository (here [this one](https://github.com/Carath)), run the following command:

```sh
python3 fetch.py https://github.com/Carath
```

Additionally some options may be given as args to the previous command, following the model below:

```sh
python3 fetch.py url saveStarred onlyLastCommit ignoreCache
```

The optional args should be either 0 or 1, and are described below:

- **saveStarred**: enables to backup the starred project by the user if available.
- **onlyLastCommit**: used to only get the last commit instead of the whole git history. Note that when this has been used, ignoring the cache will be needed if one wants to get back the whole history.
- **ignoreCache**: enables to ignore all temporary files and clone the repositories from scratch.

Note also that running again the previous commands will update the projects, and the fetching time should be shorter.
