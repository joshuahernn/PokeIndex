# PokeIndex

**A dedicated search engine for Pokémon trading cards.**

PokeIndex is a team project to build a search and discovery platform for Pokémon TCG players and collectors. Our goal is to connect card search, competitive deck insights, evolution lines, and market information in one place, helping users find specific printings and understand how cards are used in the game.

> **Status:** Planning and design. The features and roadmap below describe our planned implementation.

## Purpose

Finding the right card can mean more than remembering its name. Collectors may be looking for a particular set, rarity, or alternate artwork, while competitive players may want to find a useful ability or see which tournament decks use a card.

We aim to make both workflows easier through flexible searches and connected card information. The planned catalog covers English and Japanese cards from modern and vintage sets.

## Planned Features

### Card search and discovery

- **Two search modes:** Search by Pokémon name or through card text, including attacks, abilities, mechanics, and descriptions.
- **Specific version lookup:** Use an optional set name and card number to find a particular printing or alternate art version.
- **Typo tolerance:** Handle minor spelling mistakes, such as “Charzard” when searching for “Charizard.”
- **Detailed filters:** Narrow results by Energy Type, Trainer Type, Series, Expansion Set, Release Year, and Rarity.
- **Flexible sorting:** Sort alphabetically, by Energy Type or Trainer Type, or by release date in either direction.
- **Visual card previews:** Show high-resolution artwork, set symbols, card numbers, and market prices when available.

### Competitive deck insights

Explore tournament decks that include a selected card using data from Limitless TCG. Decklists, archetype placements, and card usage statistics will help players understand where a card appears in competitive play and discover possible deck combinations.

### Evolution lines and card versions

An interactive evolution tree will connect a Pokémon to its previous and next evolutions. Users will also be able to explore different card versions across sets and generations.

### Card details and market information

A card detail view will bring together artwork, set information, tournament deck appearances, evolution information, and market pricing. Planned pricing features include current prices, recent sales, and historical trends. Price freshness and historical coverage will depend on the data available from each source.

## Data and Scope

| Area | Planned coverage and sources |
| --- | --- |
| Card catalog | English and Japanese cards across modern and vintage sets, using PkmnCards and Limitless TCG. |
| Card information | Names, card numbers, artwork, set symbols, series, expansion sets, release dates, types, rarity, language, and searchable card text. |
| Competitive play | Tournament decklists, archetype placements, and card usage statistics from Limitless TCG. |
| Market information | Prices, recent sales, and historical trends from PriceCharting, with TCGplayer as a potential additional source. |
| Data organization | Structured relational database tables to connect card records and support filtering. |

Permission has been granted to use PriceCharting data for this project. TCGplayer remains a potential source. Data integrations will follow the access and usage permissions applicable to each source.

## Roadmap

### 1. Establish the card catalog

- [ ] Define a relational schema for cards, sets, languages, and related information.
- [ ] Collect and normalize English and Japanese card records from the planned sources.
- [ ] Check data quality and distinguish individual printings across sets and languages.

### 2. Build the search experience

- [ ] Implement name search and card text search.
- [ ] Add set and card number inputs for specific version lookup.
- [ ] Support typo tolerance, filters, and sorting.
- [ ] Display card previews with artwork and identifying details.

### 3. Connect cards to decks and evolutions

- [ ] Associate cards with tournament decklists and usage information from Limitless TCG.
- [ ] Build an interactive evolution tree.
- [ ] Support exploration of card versions across sets and generations.
- [ ] Bring deck and evolution information into the card detail view.

### 4. Add market context

- [ ] Integrate PriceCharting data within the granted permission scope.
- [ ] Display available prices, recent sales, and historical trends.
- [ ] Evaluate TCGplayer as an additional source.
- [ ] Make pricing sources and update times clear to users.

### 5. Evaluate and refine

- [ ] Test exact searches, misspellings, card text queries, and combined filters.
- [ ] Evaluate result relevance and search performance.
- [ ] Verify links between cards, printings, tournament decks, and evolution lines.
- [ ] Refine the experience for both competitive players and collectors.

## Team

- Max Wang
- Joshua Hernandez
