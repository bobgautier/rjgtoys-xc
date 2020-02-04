
import sys

import argparse

import requests

from rjgtoys.xc import Error

from apierrors import *


class ApiClient:

    DEFAULT_SERVICE="http://localhost:8000/"

    def build_parser(self):
        p = argparse.ArgumentParser('example API client')

        p.add_argument('verb', help="What to do", choices=('sum', 'div'))

        p.add_argument('--a', type=int, help="First parameter")
        p.add_argument("--b", type=int, help="Second parameter")

        p.add_argument("--service", type=str, help="URL of service", default=self.DEFAULT_SERVICE)

        return p


    def main(self, argv=None):

        p = self.build_parser()

        args = p.parse_args(argv)

        self.service = args.service

        try:
            print(self.get(args.verb, a=args.a, b=args.b))
        except OpError as e:
            print(e)

    def get(self, op, **params):

        url = "%s%s" % (self.service, op)
        r = requests.get(url, params=params)

        if r.status_code == 400:
            raise Error.from_obj(r.json())

        r.raise_for_status()

        return r.json()['result']


if __name__ == "__main__":
    cmd = ApiClient()

    sys.exit(cmd.main())

