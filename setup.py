from setuptools import setup

setup(
    name="git-changelog-generator",
    version="0.1.0",
    py_modules=["git_changelog_generator"],
    entry_points={
        "console_scripts": [
            "git-changelog-generator=git_changelog_generator:main",
        ],
    },
    python_requires=">=3.6, <4",
    install_requires=["chevron>=0.13", "GitPython>=3.1"],
)
