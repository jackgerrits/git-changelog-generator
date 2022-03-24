import argparse
import re

import chevron
import git


def extract_info_from_commits(commits):
    extracted_commits = []
    for commit in commits:
        message_lines = commit.message.splitlines()
        subject = message_lines[0]
        body = "\n".join(message_lines[1:])

        item = dict()
        item["subject"] = subject
        item["commit"] = commit.hexsha
        item["author_name"] = commit.author.name
        item["author_email"] = commit.author.email
        item["body"] = body

        match_type_and_pr_num = re.search(
            r"^([a-zA-Z]+)(\!?):.+\(#([0-9]+)\)$", subject
        )
        if match_type_and_pr_num:
            item["type"] = match_type_and_pr_num.group(1)
            item["breaking"] = match_type_and_pr_num.group(2) == "!"
            item["pr_num"] = match_type_and_pr_num.group(3)
        else:
            # If type isn't found try just extracting the PR number.
            match_pr_num = re.search(r"^.+\(#([0-9]+)\)$", subject)
            if match_pr_num:
                item["pr_num"] = match_pr_num.group(1)
                item["breaking"] = False
                item["type"] = "unknown"
            else:
                item["type"] = "unknown"
                item["breaking"] = False
                item["pr_num"] = "unknown"
        extracted_commits.append(item)
    return extracted_commits


def extract_authors_from_commits(commits):
    authors_seen = set()
    authors = []
    for commit in commits:
        if commit.author.name not in authors_seen:
            authors.append({"name": commit.author.name, "email": commit.author.email})
            authors_seen.add(commit.author.name)

    return authors


def main():
    parser = argparse.ArgumentParser(
        description="Extract commits from a git repo and format according to template"
    )
    parser.add_argument(
        "--file", "-f", type=str, required=True, help="Template file to process"
    )
    parser.add_argument(
        "--range",
        "-r",
        type=str,
        required=True,
        help="git log range to extract commits for",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        required=True,
        help="directory of repo to read commits from",
    )
    parser.add_argument(
        "--additional_data",
        "-c",
        type=str,
        default=[],
        action="append",
        help="Additional data values pass to template, must be in the form key=value",
    )
    args = parser.parse_args()

    repo = git.Repo(args.dir)
    commit_list = list(repo.iter_commits(args.range, max_count=None))
    commits_with_extracted_info = extract_info_from_commits(commit_list)
    authors = extract_authors_from_commits(commit_list)

    def commits_by_type(commit_type):
        return [
            commit
            for commit in commits_with_extracted_info
            if commit["type"] == commit_type
        ]

    data = {
        "commits": commits_with_extracted_info,
        "authors": authors,
        "unknown_type_commits": commits_by_type("unknown"),
        "feat_type_commits": commits_by_type("feat"),
        "fix_type_commits": commits_by_type("fix"),
        "docs_type_commits": commits_by_type("docs"),
        "style_type_commits": commits_by_type("style"),
        "refactor_type_commits": commits_by_type("refactor"),
        "perf_type_commits": commits_by_type("perf"),
        "test_type_commits": commits_by_type("test"),
        "build_type_commits": commits_by_type("build"),
        "ci_type_commits": commits_by_type("ci"),
        "chore_type_commits": commits_by_type("chore"),
        "revert_type_commits": commits_by_type("revert"),
    }

    template_file = args.file
    with open(template_file, "r") as f:
        template_contents = f.read()

        for val in args.additional_data:
            if "=" in val and val.count("=") == 1:
                components = val.split("=")
                if components[0] in data:
                    raise RuntimeError(
                        f"{components[0]} already defined in template data"
                    )

                data[components[0]] = components[1]
            else:
                raise RuntimeError(
                    f"--additional_data must be of the form key=value, but found: {val}"
                )

        rendered = chevron.render(template=template_contents, data=data)
        print(rendered)


if __name__ == "__main__":
    main()
