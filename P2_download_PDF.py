import pandas as pd
import requests
from dspipe import Pipe
import requests_random_user_agent
import time

f_xml = "data/processed_xml.csv"
sleep_time = 0

name = "archive_key"
df = pd.read_csv(f_xml, usecols=[name])
targets = df[name].values.tolist()


# If a proxy server is needed, use it here.
# def proxy(url):
#    port = 8000
#    hostname = ""
#    proxy_url = f"http://{hostname}:{port}"
#    return requests.get(proxy_url, params={"url": url})


def compute(f0, f1):
    url = "https://philarchive.org/archive/" + f0

    try:
        # Use a regular request, or ...
        r = requests.get(url)

        # Use the proxy server here
        # r = proxy(url)
    except Exception as EX:
        print(f"Failed to get {url}, {EX}")
        return False

    if not r.ok:

        # If we have a known error (missing document, write an empty file)
        if r.status_code in [
            404,
        ]:
            with open(f1, "w") as FOUT:
                print(f"Marked missing document {url}")
                return False

        print(f"Error {url}, status code {r.status_code}")

    with open(f1, "wb") as FOUT:
        FOUT.write(r.content)

    time.sleep(sleep_time)
    print(f1)


Pipe(targets, "data/download", output_suffix=".pdf", shuffle=True)(compute, 1)
