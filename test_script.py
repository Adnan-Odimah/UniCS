import subprocess
import time

def main():
    while True:
        command = ["python3", "webscraper/url_gen.py"]
        print(subprocess.run(command, capture_output=True))

        time.sleep(5)

if __name__ == "__main__":
    main()