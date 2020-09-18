"""
simple script that tests accessing executable info, writing to stdout, 
and reading/writing files in container and on host when mounted
"""
import socket
import sys

def create_message():
    version_info = sys.version_info
    major = version_info.major
    minor = version_info.minor
    hostname = socket.gethostname()
    msg = "Hello, world! I'm {} and I run Python {}.{}".format(hostname, major, minor)
    return msg


def write_to_file(filepath, message):
    with open(filepath, 'w') as f:
        f.write(message)


def read_from_file(filepath):
    with open(filepath, 'r') as f:
        message = f.read()

    return message


def main():
    filepath = sys.argv[1]
    orig_message = create_message()
    print(orig_message)
    write_to_file(filepath, orig_message)
    file_message = read_from_file(filepath)
    print(file_message)


if __name__ == '__main__':
    sys.exit(main())

