import json
import sys
import time
import urllib.parse

import dateutil.parser
import splinter

from output import output_print


def eprint(*args, **kwargs):
    return print(*args, **kwargs, file=sys.stderr)


class YahooBackupScraper:
    """Scrape Yahoo! Group messages with Selenium. Login information is required for
    private groups."""

    def __init__(self, group_name, driver, login_email=None, password=None, delay=1):
        self.group_name = group_name
        self.login_email = login_email
        self.password = password
        self.delay = delay

        # self.br = splinter.Browser(driver)
        self.br = splinter.Browser(driver)

    def __del__(self):
        self.br.quit()

    def _is_login_page(self):
        html = self.br.html
        output_print("Detecting the log-in page...")
        return "login-username" in html

    def _is_oath_page(self):
        html = self.br.html
        output_print("Detecting oath...")
        return "consent" in html

    def _process_login_page(self):
        """Process the login page."""
        if not self.login_email or not self.password:
            raise ValueError("Detected private group! Login information is required")

        output_print("Processing the log-in page...")

        # email ...
        self.br.fill("username", self.login_email)
        time.sleep(1)
        self.br.find_by_name("signin").click()
        # Wait ...
        time.sleep(2)

        # password ...
        self.br.fill("password", self.password)
        time.sleep(1)
        self.br.find_by_name("verifyPassword").click()
        # Wait ...
        time.sleep(2)

    def _process_oath_page(self):
        output_print("Processing the oath page...")
        self.br.find_by_name("agree").click()

    def _visit_with_login(self, url):
        """Visit the given URL. Logs in if necessary."""
        self.br.visit(url)
        time.sleep(1)
        time.sleep(1)

        if self._is_oath_page():
            self._process_oath_page()

        if self._is_login_page():
            self._process_login_page()
            # get the page again
            self.br.visit(url)

        if self._is_login_page():
            raise RuntimeError("Unable to login")

        return

    def yield_walk_files(self, path="."):
        """Starting from `path`, yield a dict describing each file, and recurse into subdirectories."""
        url = "https://groups.yahoo.com/neo/groups/%s/files/%s/" % (self.group_name, path)

        self._visit_with_login(url)

        # get all data-file attributes - these are the file entries
        data_files = []
        data_dirs = []
        elements = self.br.find_by_xpath("//*[@data-file]")

        for el in elements:
            data = json.loads('{' + el['data-file'].encode('utf8').decode('unicode_escape') + '}')
            if data['fileType'] == 'd':
                data_dirs.append(data)
            elif data['fileType'] == 'f':
                data['url'] = el.find_by_tag('a')[0]._element.get_attribute('href')
                data['profile'] = el._element.find_element_by_class_name('yg-list-auth').text
                data['the_date'] = dateutil.parser.parse(el._element.find_element_by_class_name('yg-list-date').text)
                data_files.append(data)
            else:
                raise NotImplementedError("Unknown fileType %s, data was %s" % (
                    data['fileType'], json.dumps(data),
                ))



        for data in data_files:
            yield {
                'filePath': urllib.parse.unquote(data['filePath']),
                'url': data['url'],
                'mime': data['mime'],
                'size': float(data['size']),
                'profile': data['profile'],
                'date': data['the_date'],
                'fileType': 'f'
            }

        for data in data_dirs:
            yield {
                'filePath': urllib.parse.unquote(data['filePath']),
                'fileType': 'd'
            }

            yield from self.yield_walk_files(data['filePath'])
