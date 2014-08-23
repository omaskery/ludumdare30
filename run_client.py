__author__ = 'Oliver Maskery'

import client as c


def main():
    target = 'teamfrag.net'
    
    client = c.Client(target)
    client.run()


if __name__ == "__main__":
    main()
