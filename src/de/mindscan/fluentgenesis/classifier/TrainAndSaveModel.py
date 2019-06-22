'''
Created on 22.06.2019

@author: JohnDoe
'''

import sys

def main(argv = None):
    try:
        print("Helo World!")
        pass
    except:
        return 1
    finally:
        return 0

if __name__ == '__main__':
    sys.exit(main())