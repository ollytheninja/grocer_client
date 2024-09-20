# Grocer Client

This is an unofficial client for interacting with the grocer.nz API.

## Cloudscraper

This project uses [cloudscraper](https://github.com/VeNoMouS/cloudscraper) to avoid being treated as a bot by CloudFlare.
While the API doesn't have anti-bot explicitly turned on, I like keeping my IP at least slightly clean.

Cloudscraper is a drop-in replacement for [requests](https://docs.python-requests.org/en/latest/index.html)
you're more than welcome to switch back to requests!

## Usage

Check out the code to see how the inputs and outputs are structured.

Note currently it very closely aligns with the API, 
in future I'd like to make it a little more pythonic and easier to use.

Below is a basic example to get you started.

```python
from grocer_client import Grocer

# Instantiate the client
grocer = Grocer()

# Search for products
results = grocer.search(query="standard milk 2l")
target_product = results.hits[0]

# Fetch stores
stores = grocer.get_stores()
target_store = stores[0]

# Fetch the current price for a product from a store
# You can pass multiple products and stores at once, 
# just be aware your query will get big quickly
product_results = grocer.get_products_by_id(
    product_ids=[target_product.id],
    store_ids=[target_store.id],
)

for i in product_results:
    print(f"{target_product.name} from {target_store.name} is usually ${i.prices[0].original_price}")
```

## Legal note

This is a bit "scrapy" but the developer of the API has [said on discord](https://discord.com/channels/1092929416419614720/1092929416981647482/1113643700837433344)
that he's fine with people talking directly to the API.
