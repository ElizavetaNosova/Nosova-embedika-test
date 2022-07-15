import requests
import random


class RequestsWrapper:

    def __init__(self, fake_success=True):
        self.fake_success = fake_success
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]

    def get(self, link):
        user_agent = random.choice(self.user_agents)
        headers = {'User-Agent': user_agent}
        resp = requests.get(link, headers=headers)
        return resp

    def get_html(self, link):
        resp = self.get(link)
        if not self.fake_success:
            resp.raise_for_status()
        return resp.text if resp.status_code == 200 else ''
