# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 indent-with-tabs: 0 -*-

from __future__ import unicode_literals, print_function, division

import argparse
import datetime
import idnits
import json
import lxml.etree
import os
import sys

import idnits.parser
import idnits.checks
import idnits.utils

try:
    import debug
    assert debug
except ImportError:
    pass

# ----------------------------------------------------------------------

def show_version(verbose=False):
    # Show version information, then exit
    print('%s %s' % (idnits.NAME, idnits.__version__))
    if verbose:
        try:
            import pkg_resources
            this = pkg_resources.working_set.by_key[idnits.NAME]
            for p in this.requires():
                try:
                    dist = pkg_resources.get_distribution(p.key)
                    print('  %s'%dist)
                except:
                    pass
        except:
            pass

def show_checks():
    def empty():
        ""
    show = dict(any='any', xml='XML', rfc='RFC', ids='IDs', txt='TXT')
    format = "%3s  %3s  %s"
    print(format % ('Fmt', 'Doc', 'Comment'))
    print(format % ('---', '---', '-------'))
    print('')
    for c in idnits.checks.Checker.checks:
        
        if c.func.__code__.co_code != empty.__code__.co_code:
            line = format % (show[c.fmt], show[c.type], c.func.__doc__ )
            print(idnits.utils.wrap(line, i=10))
            print('')

def die(*args):
    sys.stderr.write('Error: ' + ' '.join(args))
    sys.stderr.write('\n')
    sys.exit(1)

def main():
    # Populate options
    argparser = argparse.ArgumentParser(description=idnits.DESCRIPTION.split('\n')[0])
    argparser.add_argument('docs', metavar='DOC', nargs='*', help="document to check")

    argparser.add_argument('-d', '--debug', action='store_true', help="show debug information")
    argparser.add_argument('-l', '--list', action='store_true', help="list the idnits checks")
    argparser.add_argument('-m', '--mode', choices=['normal', 'lenient', 'submission',], default='normal',
        help="the mode to run in, default=%(default)s ")
    argparser.add_argument('-v', '--verbose', action='store_true', help="be more verbose")
    argparser.add_argument('-V', '--version', action='store_true', help="show version information, then exit")

    options = argparser.parse_args()
    for o in vars(options):
        assert hasattr(idnits.default_options, o), "Internal error: Missing a default option value for '%s'"%o

    if options.version:
        show_version(verbose=options.verbose)
        sys.exit(0)

    if options.list:
        show_checks()
        sys.exit()

    errors = 0
    for filename in options.docs:
        severities = ['err', 'warn', 'comm']
        items = dict( (s, []) for s in severities)
        longform = dict(err='error', warn='warning', comm='comment')
        #
        print("Inspecting file %s" % filename)
        try:
            doc = idnits.parser.parse(filename, options)
        except LookupError as e:
            die('Could not parse %s:'%filename, str(e))
        parse_errors = []
        for e in doc.err:
            if isinstance(e, lxml.etree.XMLSyntaxError):
                for ee in e.error_log:
                    parse_errors.append(idnits.checks.Nit(ee.line, ee.message))
            else:
                if hasattr(e, 'lineno'):
                    parse_errors.append(idnits.checks.Nit(e.lineno, e.msg))
                else:
                    parse_errors.append(idnits.checks.Nit(None, str(e)))
        count = len(parse_errors)
        if count:
            items['err'] = [(parse_errors, "Found %d parse error%s while processing file.  The idnits result may be incomplete." %(count, '' if count==1 else 's')), ]
        #
        checker = idnits.checks.Checker(doc, options=options)
        result = checker.check()
        for s in severities:
            items[s] += result[s]
        for s in severities:
            long = longform[s].capitalize()
            found = items[s]

            if found:
                count = len(found)
                print("\n%s%s%s\n" % (long, '' if count==1 else 's', ':' if count>0 else ''))
                for nits, msg in found:
                    sys.stdout.write(idnits.utils.wrap("   %s" % (msg, ), i=9))
                    assert msg.endswith('.') is False
                    if options.verbose:
                        print(':\n')
                        for item in nits:
                            if item.num:
                                print("%s(%s): %s" % (filename, item.num, item.msg))
                            else:
                                print("%s: %s" % (filename, item.msg))
                        print('')
                    else:
                        print('.')
        errors += len(result['err'])

        summary = []
        tot = 0
        for s in severities:
            found = items[s]
            count = len(found)
            tot += count
            summary.append("%s %s%s" % (count, longform[s], '' if count==1 else 's'))
        print('')
        if tot>0 and not options.verbose:
            print('Use --verbose mode to get a line-by-line listing of the issues found.\n')
        print("Found %s.\n"  % ', '.join(summary))

    sys.exit(1 if errors else 0)