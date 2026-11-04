import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from card_schema import CARD_FIELDS, ENERGY


def canonical_card_url(url):
    # make sure the URL is from PkmnCards
    parts = urlsplit(url)

    if parts.scheme not in {'http', 'https'}:
        return None

    if parts.hostname not in {'pkmncards.com', 'www.pkmncards.com'}:
        return None

    # only accept individual card pages
    if not re.fullmatch(r'/card/[^/]+/?', parts.path):
        return None

    # remove anything extra from the URL to avoid duplicates
    path = parts.path.rstrip('/') + '/'

    return urlunsplit(('https', 'pkmncards.com', path, '', ''))


def parse_card(soup, url):
    # get the card information from the HTML page
    url = canonical_card_url(url)

    if url is None:
        return None

    panel = soup.select_one('.card-tabs .tab.text')

    if panel is None:
        raise ValueError('Card text panel missing; check the page or its HTML layout')

    def clean(text):
        return ' '.join(text.split())

    # helper to get the text from an HTML element
    def value(selector):
        element = panel.select_one(selector)

        if element is not None:
            return clean(element.get_text(' ', strip=True))

        return None

    # create an empty card to store all the information
    card = {}

    for field in CARD_FIELDS:
        card[field] = None

    card['id'] = urlsplit(url).path.strip('/').split('/')[-1]
    card['source_url'] = url
    card['types'] = []
    card['attacks'] = []
    card['warnings'] = []

    # get the basic card information
    selectors = {
        'name': '.name',
        'set': '.release-meta [title="Set"]',
        'set_code': '[title="Set Abbreviation"]',
        'card_number': '.number',
        'series': '.release-meta [title="Series"]',
        'stage': '.stage',
        'rarity': '.rarity',
        'artist': '.illus a',
        'weakness': '.weak',
        'resistance': '.resist'
    }

    for field in selectors:
        card[field] = value(selectors[field])

    # get the number fields
    number_fields = {
        'hp': '.hp',
        'set_total': '.out-of',
        'retreat_cost': '.retreat'
    }

    for field in number_fields:
        text = value(number_fields[field])
        number = re.search(r'\d+', text or '')

        if number:
            card[field] = int(number.group())

    # remove the labels from weakness and resistance
    if card['weakness']:
        card['weakness'] = card['weakness'].removeprefix('weak:').strip()

    if card['resistance']:
        card['resistance'] = card['resistance'].removeprefix('resist:').strip()

    # get the Pokemon types
    types = panel.select('.color abbr[title]')

    for item in types:
        card['types'].append(item['title'])

    # get the card image
    image = soup.select_one('meta[property="og:image"]')

    if image is not None:
        image_url = image.get('content')

        if image_url:
            card['image_url'] = urljoin(url, image_url)

    # get the card text
    card['card_text'] = value(':scope > .text')

    # go through the paragraphs to find the attacks
    paragraphs = panel.select(':scope > .text > p')

    for paragraph in paragraphs:
        raw = clean(paragraph.get_text(' ', strip=True))

        if '→' not in raw:
            continue

        name = paragraph.find('span', recursive=False)
        line_break = paragraph.find('br', recursive=False)

        if name is None:
            card['warnings'].append(
                'Unrecognized attack structure: ' + raw
            )
            continue

        # get the energy needed for the attack
        energy_cost = []

        energy_text = raw.split('→', 1)[0]
        symbols = re.findall(r'\{\s*([^{}]+?)\s*\}', energy_text)

        for symbol in symbols:
            symbol = symbol.strip()

            if symbol in ENERGY:
                energy_cost.append(ENERGY[symbol])
            else:
                energy_cost.append(symbol)

        # get the attack description
        description_parts = []

        if line_break is not None:
            for node in line_break.next_siblings:
                if hasattr(node, 'get_text'):
                    description_parts.append(
                        node.get_text(' ', strip=True)
                    )
                else:
                    description_parts.append(str(node))

        description = clean(' '.join(description_parts))

        # get the damage from the attack
        damage_parts = []

        for node in name.next_siblings:
            if node is line_break:
                break

            if hasattr(node, 'get_text'):
                damage_parts.append(node.get_text(' ', strip=True))
            else:
                damage_parts.append(str(node))

        damage_text = ''.join(damage_parts)
        damage_match = re.search(r':\s*(\S+)', damage_text)

        damage = None

        if damage_match:
            damage = damage_match.group(1)

        # save the attack information
        attack = {
            'name': clean(name.get_text(' ', strip=True)),
            'energy_cost': energy_cost,
            'damage': damage,
            'text': description
        }

        card['attacks'].append(attack)

    # check if any important card information is missing
    required_fields = ['name', 'set', 'card_number']

    for field in required_fields:
        if not card[field]:
            card['warnings'].append(
                'Missing required field: ' + field
            )

    return card
