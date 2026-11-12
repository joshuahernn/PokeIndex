import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from card_schema import CARD_FIELDS, ENERGY


def canonical_card_url(url):
    parts = urlsplit(url)

    if parts.scheme not in {'http', 'https'}:
        return None

    if parts.hostname not in {'limitlesstcg.com', 'www.limitlesstcg.com'}:
        return None

    match = re.fullmatch(
        r'/cards/(?:([a-z]{2})/)?([A-Za-z0-9-]+)/([A-Za-z0-9-]+)/?',
        parts.path
    )

    if match is None:
        return None

    language, set_code, number = match.groups()

    # '/cards/en/DLR' is a set listing, not a card
    if language is None and re.fullmatch(r'[a-z]{2}', set_code):
        return None

    # English only for now
    if language not in (None, 'en'):
        return None

    path = f'/cards/en/{set_code}/{number}'
    return urlunsplit(('https', 'limitlesstcg.com', path, '', ''))

def parse_card(soup, url):
    # get the card information from the HTML page
    url = canonical_card_url(url)

    if url is None:
        return None

    panel = soup.select_one('.card-page-main')

    if panel is None:
        raise ValueError('Card panel missing; check the page or its HTML layout')

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

    path_parts = urlsplit(url).path.strip('/').split('/')

    card['id'] = 'limitless-' + '-'.join(path_parts[1:])
    card['source_url'] = url
    card['types'] = []
    card['attacks'] = []
    card['warnings'] = []

    # get the basic card information
    selectors = {
        'name': '.card-text-name',
        'artist': '.card-text-artist a'
    }

    for field in selectors:
        card[field] = value(selectors[field])

    # get the Pokemon HP from the title
    title = value('.card-text-title') or ''

    hp = re.search(r'\b(\d+)\s+HP\b', title)

    if hp:
        card['hp'] = int(hp.group(1))

    # get the Pokemon types
    type_match = re.search(r' - (.*?) - \d+\s+HP\b', title)

    if type_match:
        types = type_match.group(1).split('/')

        for pokemon_type in types:
            card['types'].append(clean(pokemon_type))

    # get the Pokemon stage
    card_type = value('.card-text-type') or ''
    type_parts = [clean(part) for part in card_type.split(' - ')]

    if type_parts and type_parts[0]:
        card['supertype'] = type_parts[0]

    if len(type_parts) > 1:
        if type_parts[0] == 'Pokémon':
            card['stage'] = clean(type_parts[1])
        else:
            card['subtype'] = clean(type_parts[1])

    # get the card set and set code
    set_text = value('.prints-current-details .text-lg') or ''

    set_match = re.fullmatch(r'(.*?)\s*\(([^()]+)\)', set_text)

    if set_match:
        card['set'] = clean(set_match.group(1))
        card['set_code'] = clean(set_match.group(2))

    else:
        if set_text:
            card['set'] = set_text

        card['set_code'] = path_parts[2]

    # get the card number and total cards in the set
    printing = value('.prints-current-details > span:not(.text-lg)') or ''

    number = re.search(
        r'#\s*([A-Za-z0-9-]+)(?:\s*/\s*(\d+))?',
        printing
    )

    if number:
        card['card_number'] = number.group(1)

        if number.group(2):
            card['set_total'] = int(number.group(2))

    else:
        card['card_number'] = path_parts[3]

    # get the card rarity
    if '·' in printing:
        rarity = clean(printing.split('·', 1)[1])

        if rarity:
            card['rarity'] = rarity

    # get weakness, resistance, and retreat cost
    wrr = value('.card-text-wrr') or ''

    weakness = re.search(r'Weakness:\s*(.*?)\s+Resistance:', wrr)
    resistance = re.search(r'Resistance:\s*(.*?)\s+Retreat:', wrr)
    retreat = re.search(r'Retreat:\s*(\d+)', wrr)

    if weakness:
        card['weakness'] = clean(weakness.group(1))

    if resistance:
        card['resistance'] = clean(resistance.group(1))

    if retreat:
        card['retreat_cost'] = int(retreat.group(1))

    # change none to n/a for weakness and resistance
    for field in ['weakness', 'resistance']:
        if card[field]:
            if card[field].lower() == 'none':
                card[field] = 'n/a'

    # get the card image
    image = panel.select_one('.card-image img')

    if image is not None:
        image_url = image.get('data-src') or image.get('src')

        if image_url:
            card['image_url'] = urljoin(url, image_url)

    # get the card text
    card['card_text'] = value('.card-text')

    # go through the attacks on the card
    attacks = panel.select('.card-text-attack')

    for attack in attacks:
        info = attack.select_one('.card-text-attack-info')

        if info is None:
            raw = clean(attack.get_text(' ', strip=True))

            card['warnings'].append(
                'Unrecognized attack structure: ' + raw
            )
            continue

        # get the energy needed for the attack
        energy_cost = []

        symbols = info.select('.ptcg-symbol')

        for symbol in symbols:
            energy_text = symbol.get_text(strip=True)

            for energy in energy_text:
                if energy.isspace() or energy == '0':
                    continue

                if energy in ENERGY:
                    energy_cost.append(ENERGY[energy])
                else:
                    energy_cost.append(energy)

        # get the attack name without including the energy
        heading_parts = []

        for node in info.children:
            if getattr(node, 'name', None) is not None:

                if 'ptcg-symbol' in node.get('class', []):
                    continue

                heading_parts.append(node.get_text(' ', strip=True))

            else:
                heading_parts.append(str(node))

        heading = clean(' '.join(heading_parts))

        # get the attack name and damage
        name = heading
        damage = None

        damage_match = re.fullmatch(
            r'(.+?)\s+(\d+[+×x−-]?)',
            heading
        )

        if damage_match:
            name = clean(damage_match.group(1))
            damage = damage_match.group(2)

        # skip attacks without a name
        if not name:
            raw = clean(info.get_text(' ', strip=True))

            card['warnings'].append(
                'Attack name missing: ' + raw
            )
            continue

        # get the attack description
        description = ''

        effect = attack.select_one('.card-text-attack-effect')

        if effect is not None:
            description = clean(effect.get_text(' ', strip=True))

        # save the attack information
        attack_info = {
            'name': name,
            'energy_cost': energy_cost,
            'damage': damage,
            'text': description
        }

        card['attacks'].append(attack_info)

    # check if any important card information is missing
    required_fields = ['name', 'set', 'card_number']

    for field in required_fields:
        if not card[field]:
            card['warnings'].append(
                'Missing required field: ' + field
            )

    return card
