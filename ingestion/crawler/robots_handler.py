from urllib.parse import urlparse
import urllib.robotparser as robotparser


class RobotsHandler:
    def __init__(self):
        self.parsers = {}

    def allowed(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}"

            if base not in self.parsers:
                rp = robotparser.RobotFileParser()
                rp.set_url(f"{base}/robots.txt")
                rp.read()
                self.parsers[base] = rp

            return self.parsers[base].can_fetch("*", url)

        except Exception:
            # FAIL OPEN: allow crawl if robots fails
            return True
