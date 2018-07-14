#!/usr/bin/env python3
from pathlib import Path
from pprint import pprint
import argparse
import subprocess
import re
import nginx

NGINX_SITES_ENABLED = Path('/etc/nginx/sites-enabled')

def single(seq):
    it = iter(seq)
    x = next(it)
    try:
        next(it)
        raise RuntimeError("Sequence contains more than one item")
    except StopIteration:
        pass
    return x


class NginxSite:
    def __init__(self, cfg):
        self.cfg = cfg

    @classmethod
    def from_config(cls, cfg):
        return cls(cfg)

    def __get_keys(self, key):
        return [i.value for i in self.cfg.filter('Key', key)]

    @property
    def server_names(self):
        result = []
        for x in self.__get_keys('server_name'):
            result += x.split()
        return result

    @property
    def listen_directives(self):
        return self.__get_keys('listen')

    @property
    def root(self):
        return single(self.__get_keys('root'))

    @property
    def is_ssl(self):
        for listen in self.listen_directives:
            if 'ssl' in listen.split():
                return True
        return False


def get_nginx_sites():
    for path in NGINX_SITES_ENABLED.iterdir():
        if path.suffix == '.conf':
            cfg = nginx.loadf(str(path))
            for srv in cfg.servers:
                yield NginxSite.from_config(srv)

def get_domains_for_ssl():
    for s in get_nginx_sites():
        if not s.is_ssl:
            continue
        for name in s.server_names:
            yield name, s.root


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--cert-name')
    return ap.parse_args()


def main():
    args = parse_args()

    sites = list(get_domains_for_ssl())

    print("Nginx sites:")
    for domain, webroot in sites:
        print('{} -> {}'.format(domain, webroot))


    # Run certbot
    cb_args = ['certbot', 'certonly']
    if args.dry_run:
        cb_args.append('--dry-run')
    if args.cert_name:
        cb_args += ['--cert-name', args.cert_name]
    cb_args.append('--webroot')
    for domain, webroot in sites:
        cb_args += [
            '-w', webroot,
            '-d', domain,
        ]
    #print(cb_args)

    subprocess.check_call(cb_args)

if __name__ == '__main__':
    main()
