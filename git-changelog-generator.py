import argparse
import re
import subprocess
import textwrap

import chevron


def try_decode(binary_object):
    return binary_object.decode("utf-8") if binary_object is not None else None


def get_list_of_commits(range):
    result = subprocess.run((
        f"git log --format=__START_LOG_ENTRY__START_SUBJECT%s__END_SUBJECT__START_COMMITHASH%H__END_COMMITHASH__START_COMMITAUTHOR%an__END_COMMITAUTHOR__START_COMMITBODY%b__END_COMMITBODY {range}"
    ).split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    if result.returncode != 0:
        error = try_decode(result.stdout)
        message = textwrap.indent(error, '\t')
        print(
            f"Error: git log failed with the following message: \n {message}")
        exit(1)

    info = try_decode(result.stdout)
    # skip the first empty string
    info = info.split("__START_LOG_ENTRY")[1:]

    commits = []
    for commit in info:
        m = re.search(
            r'__START_SUBJECT([\s\S]*)__END_SUBJECT__START_COMMITHASH([\s\S]+)__END_COMMITHASH__START_COMMITAUTHOR([\s\S]*)__END_COMMITAUTHOR__START_COMMITBODY([\s\S]*)__END_COMMITBODY',
            commit)

        if not m:
            raise RuntimeError(f'Could not parse commit: "{commit}""')

        item = dict()
        item['subject'] = m.group(1)
        item['commit'] = m.group(2)
        item['author'] = m.group(3)
        item['body'] = m.group(4)

        pr_num_match = re.search(r'\(#([1-9]+)\)', item['subject'])
        if pr_num_match:
            item['pr_num'] = pr_num_match.group(1)
        else:
            item['pr_num'] = "unknown"

        commits.append(item)

    return commits


def main():
    parser = argparse.ArgumentParser(
        description=
        'Extract commits from a git repo and format according to template')
    parser.add_argument('--file',
                        "-f",
                        type=str,
                        required=True,
                        help='Template file to process')
    parser.add_argument('--range',
                        "-r",
                        type=str,
                        required=True,
                        help='git log range to extract commits for')
    parser.add_argument(
        '--additional_data',
        "-c",
        type=str,
        default=[],
        action='append',
        help=
        'Additional data values pass to template, must be in the form key=value'
    )
    args = parser.parse_args()

    commits = get_list_of_commits(args.range)

    template_file = args.file
    with open(template_file, "r") as f:
        template_contents = f.read()

        data = {'commit_list': commits}
        for val in args.additional_data:
            if '=' in val and val.count('=') == 1:
                components = val.split("=")
                if components[0] in data:
                    raise RuntimeError(
                        f'{components[0]} already defined in template data')

                data[components[0]] = components[1]
            else:
                raise RuntimeError(
                    f'--additional_data must be of the form key=value, but found: {val}'
                )

        rendered = chevron.render(template=template_contents, data=data)
        print(rendered)


if __name__ == "__main__":
    main()
