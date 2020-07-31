# Git Changelog Generator
Easily generate a changelog for a git repository by filling in a template file.

```
usage: git-changelog-generator.py [-h] --file FILE --range RANGE [--additional_data ADDITIONAL_DATA]

Extract commits from a git repo and format according to template

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Template file to process
  --range RANGE, -r RANGE
                        git log range to extract commits for
  --additional_data ADDITIONAL_DATA, -c ADDITIONAL_DATA
                        Additional data values pass to template, must be in the form key=value
```

Note: The program assumes the current working directory is the in the git repository to generate the changelog for.

`-r` is a passed to the git log command directly. You use things such as:
- A commit range - `HEAD~4..HEAD` or `1.1.0..2.0.0`
- A number of commits `-n 4`


## Templating
The Python implementation, [Chevron](https://github.com/noahmorrison/chevron), of the [{{ Mustache }}](https://mustache.github.io/) template specification is used.

The input file is processed and according to the Mustache syntax. The values available in the template are a list of commits that are extracted from the git log as well as additional data that can be provided on the command line.

- `commit_list` - list, each item in the list contains:
    - `subject` - Subject line of commit
    - `commit` - Full commit hash
    - `author` - Author name
    - `body` - Full body of commit
    - `pr_num` - Extracted from commits where the subject contiains `(#XXXX)`

Additional data can be provided as command line arguments to do things like specify a release version in the template. The `-c` argument must be passed as a `key=value` pair. For values to have spaces then just surround the entire argument in quotes `-c "key=value"`.

If the data does not exist then the templating engine will simply ignore the value.

## Example

Given the following template file:
```
# Changelist
Version: {{version}}

{{#commit_list}}
- {{commit}} {{author}}
  - {{subject}}
{{/commit_list}}
```

Running the following command:
```sh
python git-changelog-generator.py -f example-changelog.template.md -r "HEAD~10..HEAD" -c version=2.0
```

May produce output similar to:
```
# Changelist
Version: 2.0

- 3fc607e5cbb2cfa613b67cabf60372e726575cd6 Jack Gerrits
  - Refactor input and basic window handling into a window object
- 8e0fbb36329985672cb5260320836b55b9a71310 Jack Gerrits
  - various small const and constexpr related things
- 2cc48e7f7e0d850d5dec9a3aa4756167b35268a5 Jack Gerrits
  - Add CLion things to gitignore
- 84042db1612dfbffe4fda7f9625ff60005d3511c Jack Gerrits
  - Add glm_ext header to deal with unknown pragma warning
- 0e3928524e8297b4f485fc48b484765d2d741b40 Jack Gerrits
  - Fix build on Ubuntu
- cf74b2fa96501d5d2aea9403fcff34030abb2876 Jack Gerrits
  - Applying clang-tidy fixes
- 785b85bf69ba72d72d88286fe632003c9904512c Jack Gerrits
  - Set CMake policy CMP0092 to new to avoid warnings with MSVC
- e7043c5bdac810ce906e7b13ee9d9b07eb68ed6b Jack Gerrits
  - Run format over code
- f125be755f1bbd9354a4292bc840f679d853c930 Jack Gerrits
  - Bring in fmt
- f2b740becfa982ef4e999f44842ba97996e12e38 Jack Gerrits
  - Remove shader from target sources
```