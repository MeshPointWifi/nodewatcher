from .celery import app as celery_app

NAME = 'nodewatcher'
VERSION = (3, 0, 0, 'beta', 0)


def get_version(version=None):
    """
    Derives a PEP386-compliant version number from VERSION.
    """

    if version is None:
        version = VERSION

    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


__version__ = get_version()
__author__ = 'wlan slovenija'
__contact__ = 'nodewatcher@wlan-si.net'
__homepage__ = 'https://dev.wlan-si.net/wiki/Nodewatcher'
__docformat__ = 'restructuredtext'
__copyright__ = '2009-2014'
