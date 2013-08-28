#!/usr/bin/env python
# link me into your git hooks like so:
# ln -s `pwd`/scripts/pre-commit.py `pwd`/.git/hooks/pre-commit

import os
import re
import subprocess
import sys

modified = re.compile('^(?:M|A)(\s+)(?P<name>.*)')

CHECKS = [
    {
        'output': 'Checking for pdbs...',
        'command': 'grep -n "import pdb" %s',
        'ignore_files': ['.*pre-commit', '.*/ve/.*',
                         '.*djangosherd/media/js/sherdjs'],
        'print_filename': True,
    },
    {
        'output': 'Checking for print statements...',
        'command': 'grep -n print %s',
        'match_files': ['.*\.py$'],
        'ignore_files': ['.*migrations.*', '.*management/commands.*',
                         '.*manage.py', '.*/scripts/.*', '.*/ve/.*',
                         '.*settings_test.py',
                         '.*scripts/pre-commit\.py$',
                         '.*scripts/minify-js\.py$',
                         '.*scripts/minify-mustache\.py$',
                         '.*virtualenv\.py$'],
        'print_filename': True,
    },
    {
        'output': 'Checking for console.log()...',
        'command': 'grep -n console.log %s',
        'match_files': ['.*\.js$'],
        'ignore_files': ['.*backbone-min\.js$', '.*jquery-.*\.js$',
                         '.*underscore.*\.js$', '.*/media/CACHE/.*',
                         '.*/ve/.*'],
        'print_filename': True,
    },
    {
        'output': 'Checking for debugger...',
        'command': 'grep -n debugger %s',
        'match_files': ['.*\.js$', '.*/media/CACHE/.*'],
        'print_filename': True,
    }
]


def matches_file(file_name, match_files):
    return any(re.compile(match_file).match(file_name)
               for match_file in match_files)


def check_files(files, check):
    result = 0
    for file_name in files:
        if (not 'match_files' in check or
                matches_file(file_name, check['match_files'])):
            if (not 'ignore_files' in check or
                    not matches_file(file_name, check['ignore_files'])):
                process = subprocess.Popen(check['command'] % file_name,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, shell=True)
                out, err = process.communicate()
                if out or err:
                    if check['print_filename']:
                        prefix = '\t%s:' % file_name
                    else:
                        prefix = '\t'
                    output_lines = ['%s%s' % (prefix, line)
                                    for line in out.splitlines()]
                    print '\n'.join(output_lines)
                    if err:
                        print err
                    result = 1
    return result


def main(all_files):
    # Stash any changes to the working tree that are not going to be committed
    subprocess.call(['git', 'stash', '--keep-index'], stdout=subprocess.PIPE)

    files = []
    if all_files:
        for root, dirs, file_names in os.walk('.'):
            for file_name in file_names:
                files.append(os.path.join(root, file_name))
    else:
        p = subprocess.Popen(['git', 'status', '--porcelain'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        for line in out.splitlines():
            match = modified.match(line)
            if match:
                files.append(match.group('name'))

    result = 0
    print 'Running Django Code Validator...'
    return_code = subprocess.call('./manage.py validate', shell=True)
    result = return_code or result

    for check in CHECKS:
        print check['output']
        result = check_files(files, check) or result

    if result == 0:
        print 'Running Flake8...'
        return_code = subprocess.call(
            'flake8 --exclude=ve,media --ignore=F403 .',
            shell=True)
        result = return_code or result

    if result == 0:
        print 'Running Unit Tests...'
        return_code = subprocess.call(
            './manage.py jenkins',
            shell=True)
        result = return_code or result

    # Unstash changes to the working tree that we had stashed
    subprocess.call(['git', 'stash', 'pop', '--quiet', '--index'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Update the release id if things looks good
    if result == 0:
        print 'Updating Release Id...'
        return_code = subprocess.call('scripts/update-release-id.sh',
                                      shell=True)
        result = return_code or result

    sys.exit(result)


if __name__ == '__main__':
    all_files = False
    if len(sys.argv) > 1 and sys.argv[1] == '--all-files':
        all_files = True
    main(all_files)
