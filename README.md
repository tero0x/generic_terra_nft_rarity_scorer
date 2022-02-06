# Generic Terra NFT Rarity Scorer

This script helps to scrape all NFTs for a specific project and scores the rank of each NFT based on [Rarity Tools Scoring](https://raritytools.medium.com/ranking-rarity-understanding-rarity-calculation-methods-86ceaeb9b98c).

Do take note that this may take some time as it queries the smart contract on the blockchain.

This also does not work with Galactic Punks NFTs as their all_tokens query has some issues. For scraping galactic punks NFTs refer to my other repo

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the relevant requirements.

```bash
pip install -r requirements.txt
```

## Usage

Run the code below in your terminal to start scraping nft information
```bash
python nft_scraper.py -c <INSERT_CONTRACT_ADDRESS>
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
