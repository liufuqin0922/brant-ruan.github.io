# decode/encode a file (base64)
# Usage:
# python file2b64.py e filename
# python file2b64.py d filename
import base64
import sys

def handle_b64():
    if(sys.argv[1] == 'e'): # file to base64
        fp = open(sys.argv[2], "rb")
        data = fp.read()
        fp.close()
        fp = open(sys.argv[2] + ".en.b64", "wb")
        fp.write(base64.b64encode(data))
        fp.close()

    if(sys.argv[1] == 'd'): # file to base64
        fp = open(sys.argv[2], "rb")
        data = fp.read()
        fp.close()
        fp = open(sys.argv[2] + ".de.b64", "wb")
        fp.write(base64.b64decode(data))
        fp.close()
        
def main():
    handle_b64()

if __name__ == "__main__":
    main()