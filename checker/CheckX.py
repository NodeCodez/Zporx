from multiprocessing.dummy import Pool as ThreadPool
from os import path, mkdir, system, name
from threading import Thread, Lock
from time import sleep, strftime, gmtime, time
from traceback import format_exc

from colorama import Fore, init
from console.utils import set_title
from easygui import fileopenbox
from requests import Session, exceptions
from yaml import safe_load

default_values = '''checker:

  # Check if current version of CheckX is latest  
  check_for_updates: true
  
  # Remove duplicate proxies
  remove_duplicates: true
  
  # Check site
  check_site: 'https://azenv.net'
  
  # Save dead proxies
  save_dead: true

  # Normal users should keep this false unless problem start happening
  debugging: false
'''
if path.exists('Settings.yml'):
    settings = safe_load(open('Settings.yml', 'r', errors='ignore'))
else:
    open('Settings.yml', 'w').write(default_values)
    settings = safe_load(open('Settings.yml', 'r', errors='ignore'))


class Main:
    def __init__(self):
        self.dead = 0
        self.live = 0
        self.cpm = 0
        self.trasp = 0
        self.checked = 0
        self.stop = True
        self.start_time = 0
        self.announcement = ''
        self.checktype = ''
        self.timeout = 5000
        self.threads = 200
        # self.checkforupdates()
        self.settings()
        self.loadproxy()
        self.resultfolder()
        self.get_announcement()
        self.start()

    def now_time(self):
        return strftime("%H:%M:%S", gmtime(time() - self.start_time))

    def writing(self, line):
        lock.acquire()
        open(f'{self.folder}/{line[1]}.txt', 'a', encoding='u8').write(f'{line[0]}\n')
        lock.release()

    def check_proxies(self, proxy):
        proxy_form = {}
        if proxy.count(':') == 3:
            spl = proxy.split(':')
            proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
        if self.checktype in ['https', 'http']:
            proxy_form = {'http': f"http://{proxy}", 'https': f"https://{proxy}"}
        elif self.checktype in ['socks4', 'socks5']:
            line = f"{self.checktype}://{proxy}"
            proxy_form = {'http': line, 'https': line}
        try:
            r = session.get(url=Checker.check_site, proxies=proxy_form, timeout=self.timeout).text
            self.checked += 1
            if r.__contains__(myip):
                self.trasp += 1
                self.writing([proxy, 'Transparent'])
            else:
                self.live += 1
                self.writing([proxy, 'Live'])
            return
        except exceptions.RequestException:
            self.dead += 1
            self.checked += 1
            if Checker.save_dead:
                self.writing([proxy, 'Bad'])
            return
        except:
            if Checker.debug:
                print(f'Error: {format_exc(limit=1)}')
            return

    def tite(self):
        while self.stop:
            proxies = len(self.proxylist)
            set_title(
                f'CheckX-{version} | '
                f'{"" if self.live == 0 else f" | Live: {self.live}"}'
                f'{"" if self.dead == 0 else f" | Dead: {self.dead}"}'
                f'{"" if self.trasp == 0 else f" | Transparent: {self.trasp}"}'
                f' | Left: {proxies - self.checked}/{proxies}'
                f' | CPM: {self.cpm}'
                f' | {self.now_time()} Elapsed')

    def cpmcounter(self):
        while self.stop:
            if self.checked >= 1:
                now = self.checked
                sleep(4)
                self.cpm = (self.checked - now) * 15

    def checkforupdates(self):
        try:
            gitversion = session.get("https://raw.githubusercontent.com/ShadowOxygen/CheckX/master/version").text
            if f'{version}\n' != gitversion:
                print(sign)
                print(f"{red}Your version is outdated.")
                print(f"Your version: {version}\n")
                print(f'Latest version: {gitversion}Get latest version in the link below')
                print(f"https://github.com/ShadowOxygen/CheckX/releases\nStarting in 5 seconds...{cyan}")
                sleep(5)
                clear()
        except:
            if Checker.debug:
                print(f"{red} Error while checking for updates: \n{format_exc(limit=1)}\n")

    def loadproxy(self):
        while True:
            try:
                print(f"\n{cyan}[+] Please Import Your Proxies List.....")
                sleep(0.3)
                loader = open(fileopenbox(title="Load Proxies List", default="*.txt"), 'r', encoding="utf8",
                              errors='ignore').read().split('\n')
                if Checker.remove_dup:
                    self.proxylist = list(set([x.strip() for x in loader if ":" in x and x != '']))
                else:
                    self.proxylist = [x.strip() for x in loader if ":" in x and x != '']
                length_file = len(self.proxylist)
                if length_file == 0:
                    print(f'{red}No proxies found! Please make sure file have proxies...')
                    continue
                print(f"{cyan} > Imported {length_file} proxies from File")
                break
            except:
                if Checker.debug:
                    print(f"{red}Error while loading proxies: \n{format_exc(limit=1)}\n")
                continue

    def get_announcement(self):
        try:
            announcement = session.get(
                'https://raw.githubusercontent.com/ShadowOxygen/OxygenX/master/announcement').text.split("Color: ")
            color = announcement[1].lower()
            if color == 'red\n':
                color = red
            elif color == 'white\n':
                color = white
            elif color == 'blue\n':
                color = Fore.LIGHTBLUE_EX
            elif color == 'green\n':
                color = green
            elif color == 'cyan\n':
                color = cyan
            elif color == 'magenta\n':
                color = Fore.LIGHTMAGENTA_EX
            elif color == 'yellow\n':
                color = Fore.LIGHTYELLOW_EX
            self.announcement = f"{color}{announcement[0]}"
        except:
            if Checker.debug:
                print(f"{red}Error while displaying announcement: \n{format_exc(limit=1)}\n")
            return

    def resultfolder(self):
        unix = str(strftime('[%d-%m-%Y %H-%M-%S]'))
        self.folder = f'results/{unix}'
        if not path.exists('results'):
            mkdir('results')
        if not path.exists(self.folder):
            mkdir(self.folder)

    def start(self):
        print('\nLoading Threads...\n')
        Thread(target=self.cpmcounter, daemon=True).start()
        pool = ThreadPool(processes=self.threads)
        clear()
        Thread(target=self.tite).start()
        print(sign)
        print(self.announcement)
        print(f'{green}=======Settings=========\n'
              f'[S] Threads: {self.threads}\n'
              f'[S] Timeout: {self.timeout}s\n'
              f'[S] Proxy type: {self.checktype}\n'
              '========================\n')
        print(f'{cyan}[Z] Please wait for proxies to finish checking...')
        self.start_time = time()
        pool.imap_unordered(func=self.check_proxies, iterable=self.proxylist)
        pool.close()
        pool.join()
        self.stop = False
        cyanz = f'{white}[{Fore.CYAN}>{white}]'
        results = f'\n{cyanz} Live proxies: {green}{self.live}\n' \
            f'{cyanz} Transparent proxies: {Fore.LIGHTYELLOW_EX}{self.trasp}\n' \
            f'{cyanz} Dead proxies: {red}{self.dead}\n' \
            f'{cyanz} Speed: {cyan}{round(self.checked / (time() - self.start_time), 2)} proxies/s\n' \
            f'{cyanz} Total time checking: {cyan}{self.now_time()}\n\n' \
            f'{red}\n[EXIT] You can now exit the program...'
        print(results)
        input()
        exit()

    def settings(self):
        print(sign)
        self.threads = int(input('[+] Threads for Checking (Needs to be more than 1): '))
        while True:
            self.checktype = str(input('[+] Proxy Type (HTTP, HTTPS, SOCKS4, SOCKS5): ')).lower()
            if self.checktype not in ['https', 'http', 'socks4', 'socks5']:
                print(f'{red}[Error] Proxy type is not https, http, socks4, socks5. Please reenter')
                continue
            else:
                break
        self.timeout = int(input('[+] Proxy timeout (counted in milliseconds: 1000 = 1 second): ')) / 1000


class Checker:
    version_check = bool(settings['checker']['check_for_updates'])
    remove_dup = bool(settings['checker']['remove_duplicates'])
    check_site = str(settings['checker']['check_site']).lower()
    save_dead = bool(settings['checker']['save_dead'])
    debug = bool(settings['checker']['debugging'])


if __name__ == '__main__':
    init()
    clear = lambda: system('cls' if name == 'nt' else 'clear')
    lock = Lock()
    version = '2.0'
    session = Session()
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    cyan = Fore.LIGHTCYAN_EX
    white = Fore.LIGHTWHITE_EX
    sign = f'''{cyan}
_________ .__                   __    ____  ___
\_   ___ \|  |__   ____   ____ |  | __\   \/  /
/    \  \/|  |  \_/ __ \_/ ___\|  |/ / \     /
\\     \___|   Y  \  ___/\  \___|    <  /     \\
 \______  /___|  /\___  >\___  >__|_ \/___/\  \\
        \/     \/     \/     \/     \/      \_/
\n'''
    myip = str(session.get('http://api.ipify.org').text)
    set_title(f'CheckX-{version} | By ShadowOxygen')
    Main()
