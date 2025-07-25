import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
import os
import logging
import re
import random
import json
import sys
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Read URLs from crawler output
INPUT_CSV = "product_urls/product_links.csv"
CSV_OUTPUT = "google_feed/product_feed.csv"
XML_OUTPUT = "google_feed/product_feed.xml"
GOOGLE_MERCHANT_CSV = "google_feed/google_merchant_feed.csv"

# Manual override file - this will preserve your exact assignments
MANUAL_OVERRIDES_FILE = "manual_category_overrides.json"

# Ensure output directories exist
os.makedirs("google_feed", exist_ok=True)
logging.info(f"Ensured google_feed directory exists")

# ═══════════════════════════════════════════════════════════════════════════════════════
# COMPLETE MANUAL CATEGORY OVERRIDES - Your Exact Google Sheet Assignments
# This preserves ALL 242 of your manual changes and takes highest priority
# Generated from your Google Sheet on June 26, 2025
# ═══════════════════════════════════════════════════════════════════════════════════════

MANUAL_CATEGORY_OVERRIDES = {
    # Category 588 - Candles (8 products)
    "candle-dip-dye-yellow-tJ1CSM": "588",
    "dip-dye-blue-taper-candle-pack-of-4-G107PE": "588",
    "dip-dye-coral-taper-candle-j9N4V8": "588",
    "dip-dye-orange-taper-candle-pack-of-4-yMIpt2": "588",
    "twist-flicker-candleholder-pink-JT2eWd": "588",
    "twist-flicker-candleholder-white-sAsYLc": "588",
    "twist-glow-candleholder-green-bbkcUk": "588",
    "twist-glow-candleholder-orange-3nhp4A": "588",

    # Category 594 - Storage Jars (1 product)
    "sweetkeeper-light-yellow-jar-MfSjub": "594",

    # Category 602 - Vases (72 products - YOUR MOST COMMON CATEGORY)
    "aurora-vase-QtwQO7": "602",
    "azure-tower-vase-usiPgp": "602",
    "birdy-vase-1ivN0A": "602",
    "black-vase-l-bnkl7X": "602",
    "black-vase-m-J1WakU": "602",
    "blue-glass-vase-KAAcTq": "602",
    "blue-vase-4UH9rD": "602",
    "blush-wave-vase-VgygWF": "602",
    "bold-stripes-vase-IErdVl": "602",
    "bubble-bliss-small-blue-vase-TV97xt": "602",
    "bubble-bliss-small-green-vase-fELe5t": "602",
    "bubble-bliss-small-pink-vase-vc9h1y": "602",
    "bubble-bliss-small-red-vase-0n5hEZ": "602",
    "bubble-bliss-tall-blue-vase-unbqYB": "602",
    "bubble-bliss-tall-green-vase-nJWUpD": "602",
    "bubble-bliss-tall-pink-vase-kRaPzX": "602",
    "bubble-bliss-tall-red-vase-BdGIlV": "602",
    "bubble-pop-vase-aYXp7U": "602",
    "butterfly-garden-vase-l-lqNFj1": "602",
    "butterfly-garden-vase-m-R11BOa": "602",
    "checkmate-vase-o3SZCR": "602",
    "cherry-blossom-lidded-jar-EwKIkl": "602",
    "cherry-blossom-lidded-vase-lKXu7G": "602",
    "classic-yellow-porcelain-vase-l-Tex3ve": "602",
    "classic-yellow-porcelain-vase-m-oMwtLG": "602",
    "confetti-dot-vase-h1doBk": "602",
    "delft-tulip-vase-FMhv5X": "602",
    "disks-vase-lLL4HA": "602",
    "double-the-party-vase-yYkLDf": "602",
    "evergreen-vase-waLCAv": "602",
    "finya-vase-medium-xUMUdo": "602",
    "finya-vase-small-u9P1wN": "602",
    "firelight-duo-vase-b58wuT": "602",
    "fresh-orange-can-vase-4R6YOh": "602",
    "jardin-lidded-vase-F3AkBV": "602",
    "jug-emily-sky-matte-sjVqjD": "602",
    "jug-emily-yolk-matte-gIGtmY": "602",
    "large-chilli-vase-jgfHcr": "602",
    "leela-large-vase-Yz1pBc": "602",
    "leela-medium-vase-0Rw06l": "602",
    "lemon-vase-jWcote": "602",
    "lemonade-can-vase-set-of-3-t1vV4A": "602",
    "love-in-bloom-gold-vase-RNElJR": "602",
    "lumiere-jar-l-xJu2Ea": "602",
    "lumiere-jar-m-rRxnFq": "602",
    "mandarino-vase-RRwhKz": "602",
    "mandarino-vase-oSs5Fd": "602",
    "misty-lemon-can-vase-UIb0lj": "602",
    "paint-the-world-with-love-V6VbrO": "602",
    "papillion-lidded-vase-oSf7xQ": "602",
    "skyline-vase-9yZABA": "602",
    "small-chilli-vase-bPvwoR": "602",
    "strawberry-vase-E6CYHt": "602",
    "striped-lidded-vase-vV1XPo": "602",
    "sugarline-vase-9rFoY2": "602",
    "sugarvault-jar-l-bykFhe": "602",
    "sugarvault-jar-m-q7f2Tq": "602",
    "sugarvault-jar-s-NejKK6": "602",
    "sunbeam-vase-iSeYkN": "602",
    "sunny-wave-vase-j1TarN": "602",
    "sunshine-glass-vase-Gqvfu5": "602",
    "tangerine-twist-vase-m7G1iP": "602",
    "tissue-box-orange-pWgfkV": "602",
    "tower-vase-9HSBd7": "602",
    "tropic-twist-vase-8dCYxo": "602",
    "tropical-vase-JoQGyk": "602",
    "vase-oscar-bone-gloss-aA1JJf": "602",
    "vase-oscar-bubblegum-gloss-NiYPpf": "602",
    "vase-oscar-sky-matte-0TnEkm": "602",
    "vivid-vase-Gqxs54": "602",
    "wild-strawberry-can-vase-y0Fgm1": "602",
    "zigzag-groove-vase-1IcRW8": "602",

    # Category 674 - Glassware & Drinkware (13 products)
    "bliss-cocktail-glass-set-of-2-wVoWvZ": "674",
    "crystal-cake-stand-l-1aXHg5": "674",
    "crystal-cake-stand-m-znlBxJ": "674",
    "crystal-cake-stand-s-w5p3bW": "674",
    "crystal-hobnail-jug-with-gold-handle-U5RN5L": "674",
    "crystal-tray-FV9aIm": "674",
    "flute-water-glass-classics-on-acid-ENZuHe": "674",
    "glow-jar-CIqmuy": "674",
    "jug-emily-bone-gloss-YqW4Rm": "674",
    "jug-emily-moss-gloss-x8TBZR": "674",
    "paradise-cocktail-glass-set-of-2-EMpePq": "674",
    "whimsy-jar-PPY9tL": "674",
    "wine-chiller-vYnM0O": "674",

    # Category 721 - Planters (4 products)
    "boho-planter-o3q5RN": "721",
    "chrome-kiss-planter-nTDrA9": "721",
    "disks-planter-GFwX5i": "721",
    "pink-kiss-planter-wNl1qY": "721",

    # Category 4203 - Linen Napkins (3 products)
    "bronze-palm-trees-linen-napkins-set-of-4-9uqNPG": "4203",
    "palm-tree-linen-napkins-set-of-4-Q7LhiL": "4203",
    "ramadan-nights-linen-napkins-set-of-4-dTIbPj": "4203",

    # Category 2169 - Cappuccino Mug Set (1 product)
    "cozy-cappuccino-mug-set-ik8yLK": "2169",

    # Category 2547 - Linen Placemats (2 products)
    "bronze-palm-trees-linen-placemat-set-of-4-uPYQ5E": "2547",
    "chinoiserie-birds-linen-placemat-set-of-4-BVCL8N": "2547",

    # Category 2784 - Candle Holders (29 products)
    "candelabra-eric-bone-matte-GgNYWF": "2784",
    "emma-candle-holder-5q00Ow": "2784",
    "fancy-candle-holder-OnKt5h": "2784",
    "fancy-pink-candle-holder-wSTBIb": "2784",
    "fancy-purple-candle-holder-Xumq0D": "2784",
    "fancy-purple-candle-holder-ntWr5K": "2784",
    "fancy-yellow-candle-holder-06TVHr": "2784",
    "flower-girl-candleholde-pink-Hv3IdF": "2784",
    "flower-girl-candleholder-lilac-l77Ql5": "2784",
    "flower-girl-candleholder-ochre-dtKhkX": "2784",
    "flower-girl-candleholder-yellow-CA8gpn": "2784",
    "large-venice-candle-holder-9ERK1X": "2784",
    "leopard-candle-holder-set-of-2-W54Wir": "2784",
    "medium-venice-candle-holder-nal7NS": "2784",
    "nala-candle-holder-UsgmDg": "2784",
    "nora-candle-holder-vqp6ua": "2784",
    "nora-green-candle-holder-hLo94e": "2784",
    "nora-purple-candle-holder-kwNBcR": "2784",
    "parrot-candle-holder-2AqvCv": "2784",
    "petra-candle-holder-5RJlNo": "2784",
    "petra-pink-candle-holder-gmftTY": "2784",
    "petra-purple-candle-holder-4rsvSz": "2784",
    "philine-candle-holder-hGtibu": "2784",
    "romy-candle-holder-bFYHHJ": "2784",
    "roots-black-candle-holder-5uYzA6": "2784",
    "roots-silver-candle-holder-9tOJ5v": "2784",
    "samatha-candle-holder-ogP5cL": "2784",
    "sandy-candle-holder-HJHOe0": "2784",
    "ylvie-candle-holder-aLS7Cd": "2784",

    # Category 2951 - Hobnail Tumblers (4 products)
    "aquamarine-hobnail-tumblers-set-of-6-LbUM2N": "2951",
    "bronze-hobnail-tumblers-set-of-6-gLiGbn": "2951",
    "crystal-hobnail-tumblers-set-of-6-zEUa32": "2951",
    "neon-citrine-hobnail-tumblers-set-of-6-3uVHor": "2951",

    # Category 3330 - Jugs & Teapots (6 products)
    "aquamarine-hobnail-jug-tall-KMO9Fr": "3330",
    "bronze-hobnail-jug-tall-MItwRN": "3330",
    "hybrid-teapot-smeraldina-jP5GhE": "3330",
    "neon-citrine-hobnail-jug-PmY5xi": "3330",
    "sugar-bowl-KoIAB8": "3330",
    "teapot-UXKZyi": "3330",

    # Category 3498 - Bowls (7 products)
    "birdy-bowl-BJBWFJ": "3498",
    "bowl-lisa-bone-gloss-BSKFl3": "3498",
    "bowl-lisa-bubblegum-gloss-TyMgca": "3498",
    "bowl-lisa-coral-gloss-QuUwOW": "3498",
    "bowl-lisa-sky-gloss-jEzrk6": "3498",
    "psycho-salad-bowl-classics-on-acid-I0fOr5": "3498",
    "stella-deep-plate-60wtiW": "3498",

    # Category 3553 - Plates (50 products - YOUR SECOND LARGEST CATEGORY)
    "abracadabra-destino-dinner-plate-ZwL71a": "3553",
    "abracadabra-incanto-deep-plate-f6f3Fa": "3553",
    "abracadabra-round-serving-plate-okCZ5Q": "3553",
    "abracadabra-striped-dessert-plate-WWoXWn": "3553",
    "blue-chinoiserie-dinner-plate-classics-on-acid-PVgGP5": "3553",
    "blue-scalloped-dinner-plate-S6VT1h": "3553",
    "classic-cake-stand-W6jV8f": "3553",
    "classic-love-cappucino-mug-8stYME": "3553",
    "classic-love-dessert-plate-vHavwn": "3553",
    "con-amore-plate-5ky8Z4": "3553",
    "crazy-quarter-dark-green-line-fuZS9K": "3553",
    "crazy-quarter-plate-dark-green-blob-Up8RMG": "3553",
    "deer-dessert-plate-classics-on-acid-vJvbu7": "3553",
    "delf-rose-dessert-plate-classics-on-acide-1rmfAV": "3553",
    "english-delft-dinner-plate-classics-on-acid-f5m2Cz": "3553",
    "fiorentino-dessert-plate-classics-on-acid-LwzVgz": "3553",
    "fish-fete-plate-set-wiq5aC": "3553",
    "flower-bird-soup-plate-classics-on-acid-6Q6xUy": "3553",
    "flower-girl-set-of-4-ADbOHH": "3553",
    "forever-always-plate-4gLiFv": "3553",
    "fruit-feast-plate-PGRiVb": "3553",
    "glitchy-willow-dessert-plate-classics-on-acid-BaIQCz": "3553",
    "good-morning-bowl-fWw1mw": "3553",
    "good-morning-breakfast-plate-apSbJE": "3553",
    "hollandia-flowers-dinner-plate-classics-on-acid-IKSvjk": "3553",
    "i-love-you-plate-sUITA2": "3553",
    "la-tavola-scomposta-cake-stand-ohcRdD": "3553",
    "lobster-plate-large-vZKc7Q": "3553",
    "maastricht-ship-dinner-plate-classics-on-acid-WJeUWg": "3553",
    "matcha-set-giftbox-pink-fRIAo5": "3553",
    "matcha-set-giftbox-yellow-igGm0V": "3553",
    "modern-lisa-yk0QO3": "3553",
    "mug-i-know-qcJ8sD": "3553",
    "nye-glass-classics-on-acid-UfwDNd": "3553",
    "pegasus-breakfast-plate-rOnjMj": "3553",
    "pegasus-striped-cake-platter-gGfYcN": "3553",
    "pine-scalloped-dinner-plate-EmNJaO": "3553",
    "pink-scalloped-dinner-plate-fMD6g5": "3553",
    "powder-striped-cappuccino-mug-S4e6w4": "3553",
    "powder-striped-jug-suAk5v": "3553",
    "powder-striped-yogurt-bowl-FSlq6Q": "3553",
    "shut-up-mug-91SeML": "3553",
    "small-cups-mixed-shapes-set-of-six-ITei5v": "3553",
    "soup-plate-pagoda-classics-on-acid-x829dw": "3553",
    "stella-dessert-plate-n4IsPH": "3553",
    "stella-dinner-plate-1l2i66": "3553",
    "stella-round-plate-UP0upm": "3553",
    "talavera-soup-plate-classics-on-acid-f5iyo7": "3553",
    "tissue-box-yellow-wzvC7o": "3553",
    "yellow-scalloped-breakfast-plate-A7zpla": "3553",

    # Category 4082 - Ashtrays (2 products)
    "jacks-cig-ashtray-large-1w8qhm": "4082",
    "jacks-cig-ashtray-nPYWV9": "4082",

    # Category 4203 - Table Linens (1 product)
    "palm-tree-linen-napkins-set-of-4-H8N5uf": "4203",

    # Category 4295 - Photo Frames (5 products)
    "bisou-photo-frame-I8aWvJ": "4295",
    "ciao-bella-photo-frame-qBTc0B": "4295",
    "je-taime-photo-frame-f1XBp0": "4295",
    "saluti-photo-frame-S3nQjl": "4295",
    "the-joy-frame-set-GTfjJy": "4295",

    # Category 4453 - Cushions (3 products)
    "retro-cushion-orange-pKlI82": "4453",
    "retro-cushion-pink-0s6NHY": "4453",
    "retro-cushion-yellow-YRVYAZ": "4453",

    # Category 4741 - Home Fragrance (9 products)
    "cello-suite-n27-cotton-harmony-3000ml-yYYbh0": "4741",
    "cello-suite-n27-cotton-harmony-700ml-iQ4sd1": "4741",
    "cello-suite-n29-montecarlo-night-3000ml-ecMhk9": "4741",
    "cello-suite-n29-montecarlo-night-3000ml-u5FFZ6": "4741",
    "cello-suite-n29-montecarlo-night-700ml-LJv3uf": "4741",
    "cello-suite-n7-woods-harmony-3000ml-ACrk7O": "4741",
    "cello-suite-n7-woods-harmony-700ml-Sj5LDL": "4741",
    "edion-oud-3000ml-Fa1UyW": "4741",
    "edion-oud-pqTyyh": "4741",

    # Category 5609 - Side Tables (2 products)
    "david-bust-black-side-table-lU4Fj5": "5609",
    "david-bust-white-side-table-VtGaFa": "5609",

    # Category 6049 - Coffee & Tea Cups (7 products)
    "abracadabra-coffee-cups-set-xUdyr3": "6049",
    "fancy-tea-cup-set-with-saucer-gW5enB": "6049",
    "good-morning-mug-Qe5Bej": "6049",
    "hybrid-tea-cup-isidora-HPVap0": "6049",
    "hybrid-tea-cup-zora-with-saucer-xxizYV": "6049",
    "i-love-you-mug-JY2Lvh": "6049",
    "tea-cups-wplate-set-of-two-fKGiZh": "6049",

    # Category 6325 - Table Runners (1 product)
    "chinoiserie-birds-linen-runner-Jp2Omz": "6325",

    # Category 6456 - Trinket Trays (2 products)
    "apple-squared-trinket-tray-eHcdjZ": "6456",
    "squared-trinket-tray-jYRIfq": "6456",

    # Category 7113 - Lidded Jars (2 products)
    "classic-lidded-jar-iFyZoK": "7113",
    "papillion-lidded-jar-hEOqcQ": "7113",

    # Category 230911 - Special Candelabra (1 product)
    "parrot-candelabra-Kiv1zP": "230911",

    # Category 500044 - Comic Art (3 products)
    "comic-art-mouse-FICTbs": "500044",
    "comic-art-teddy-olpPI9": "500044",
    "relaxing-leo-jL7fXt": "500044",

    # Category 500045 - Decorative Figurines (4 products)
    "gorilla-gentleman-Hnh5S9": "500045",
    "love-peace-b9mH5L": "500045",
    "rock-style-wqoBAi": "500045",
    "wire-to-the-moon-Xk0Z0H": "500045",
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# FALLBACK CATEGORY MAPPING - For new products not in manual overrides
# Updated to match your preferred categorization patterns from the Google Sheet analysis
# ═══════════════════════════════════════════════════════════════════════════════════════

CATEGORY_MAPPING = {
    # ═══════════════════════════════════════════════════════════════
    # TABLEWARE & DINING (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Coffee Cups & Mugs → Category 6049
    "Cups": "6049",
    "Mugs": "6049",  
    "Coffee": "6049",
    "Tea": "6049",
    "Coffee Cups": "6049",
    "Tea Cups": "6049",
    "Cappuccino": "6049",
    "Mug": "6049",
    "Cup": "6049",
    
    # Plates → Category 3553
    "Plates": "3553",
    "Dinner Plate": "3553",
    "Dessert Plate": "3553",
    "Deep Plate": "3553",
    "Serving Plate": "3553",
    "Round Serving Plate": "3553",
    "Plate": "3553",
    "Dinnerware": "3553",
    "Dinner Set": "3553",
    "Tableware": "3553",
    
    # Bowls → Category 3498
    "Bowls": "3498",
    "Bowl": "3498",
    
    # Glasses & Drinkware → Category 674 or 2951
    "Glasses": "674",
    "Glass": "674",
    "Cocktail Glass": "674",
    "Tumblers": "2951",
    "Tumbler": "2951",
    "Cake Stand": "674",
    "Goblets": "674",
    "Goblet": "674",
    
    # Jugs & Teapots → Category 3330
    "Jug": "3330",
    "Teapot": "3330",
    "Pitcher": "3330",
    "Hobnail": "3330",
    
    # Other Cutlery
    "Cutlery": "728",
    
    # ═══════════════════════════════════════════════════════════════
    # HOME DECOR (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Vases → Category 602 (YOUR MOST COMMON)
    "Vases": "602",
    "Vase": "602",
    "Tower Vase": "602",
    
    # Candle Holders → Category 2784
    "Candle Holders": "2784",
    "Candle Holder": "2784",
    "Candlestick": "2784",
    "Candelabra": "2784",
    
    # Candles → Category 588
    "Candles": "588",
    "Candle": "588",
    "Taper Candle": "588",
    "Dip Dye": "588",
    
    # Photo Frames → Category 4295
    "Photo Frame": "4295",
    "Picture Frame": "4295",
    "Frame": "4295",
    
    # Cushions → Category 4453
    "Cushions": "4453",
    "Cushion": "4453",
    "Decorative Cushions": "4453",
    
    # Wall Art → Category 500044
    "Wall Art": "500044",
    "Artwork": "500044",
    "Comic Art": "500044",
    "Art": "500044",
    
    # Decorative Items → Category 500045
    "Decorative Accents": "500045",
    "Figurines": "500045",
    "Decorative": "500045",
    "Sculpture": "500045",
    "Gentleman": "500045",
    "Gorilla": "500045",
    
    # Planters → Category 721
    "Planter": "721",
    "Planters": "721",
    
    # Storage & Organization
    "Jar": "7113",
    "Lidded Jar": "7113",
    "Trinket Tray": "6456",
    "Tray": "6456",
    "Decorative Trays": "6456",
    "Ashtray": "4082",
    
    # Table Linens
    "Napkins": "4203",
    "Linen Napkins": "4203",
    "Placemats": "2547",
    "Placemat": "2547",
    "Linen Placemat": "2547",
    "Runner": "6325",
    "Linen Runner": "6325",
    "Table Linens": "4203",
    "Table Cloths": "7493",
    
    # Furniture
    "Side Tables": "5609",
    "Side Table": "5609",
    "Table": "5609",
    "Coffee Tables": "6320",
    "Console Tables": "6321",
    
    # Home Fragrance
    "Home Fragrance": "4741",
    "Diffusers": "4741",
    "Fragrance": "4741",
    "Cello": "4741",
    "Suite": "4741",
    "Room Sprays": "5099",
    "Oud": "4741",
    
    # ═══════════════════════════════════════════════════════════════
    # SEASONAL & HOLIDAY DECOR
    # ═══════════════════════════════════════════════════════════════
    
    "Holiday": "3617",
    "Christmas": "5506",
    "Ramadan": "3617",
    "Eid": "3617",
    "Special Occasion": "3617",
    
    # ═══════════════════════════════════════════════════════════════
    # KITCHEN & COOKING
    # ═══════════════════════════════════════════════════════════════
    
    "Cookware": "672",
    "Bakeware": "673",
    
    # ═══════════════════════════════════════════════════════════════
    # GIFT ITEMS
    # ═══════════════════════════════════════════════════════════════
    
    "Gift": "5394",
    "Gift Box": "5424",
    
    # ═══════════════════════════════════════════════════════════════
    # BRAND-SPECIFIC MAPPINGS (Based on your data analysis)
    # ═══════════════════════════════════════════════════════════════
    
    "BITOSSI": "3553",
    "KERSTEN": "602",
    "KLIMCHI": "674",
    "WERNS": "602",
    "ANNA + NINA": "6049",
    "EDION": "4741",
    "HOME STUDYO": "2784",
    "JOY&CO PICKS": "500045",
    "VAL POTTERY": "6049",
    "SELETTI": "3330",
    "Joy & Co": "602",
    
    # ═══════════════════════════════════════════════════════════════
    # OTHER CATEGORIES
    # ═══════════════════════════════════════════════════════════════
    
    "Accessories": "500045",
    "Home": "602",
    
    # ═══════════════════════════════════════════════════════════════
    # SPECIFIC PRODUCT KEYWORDS (Based on your product titles)
    # ═══════════════════════════════════════════════════════════════
    
    "Abracadabra": "3553",
    "David Bust Black Side Table": "5609",
    "David Bust White Side Table": "5609",
    "David Bust": "5609",
    "Aurora": "602",
    "Azure": "602",
    "Birdy": "602",
    "Emma": "2784",
    "Fancy": "6049",
    "Good Morning": "6049",
    "Bisou": "4295",
    "Ciao Bella": "4295",
    "Je t'aime": "4295",
    "Retro": "4453",
    "Chrome Kiss": "721",
    "Papillion": "7113",
    "Classic": "7113",
    "Sweetkeeper": "594",
    "Cozy": "2169",
    "Chinoiserie": "6325",
    "Palm Tree": "4203",
    "Bronze Palm": "4203",
    "Set of 6": "674",
    "Colored": "674",
    "Blue/Green": "674",
    "Che Bello": "3553",
    "Pearl Parade": "3498",
}

# Default Google category
DEFAULT_GOOGLE_CATEGORY = "602"

# User-Agent rotation for avoiding bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/98.0.4758.85 Mobile/15E148 Safari/604.1"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def load_manual_overrides():
    """
    Load manual category overrides from JSON file if it exists
    This allows you to add more overrides without changing code
    """
    overrides = MANUAL_CATEGORY_OVERRIDES.copy()
    
    if os.path.exists(MANUAL_OVERRIDES_FILE):
        try:
            with open(MANUAL_OVERRIDES_FILE, 'r', encoding='utf-8') as f:
                file_overrides = json.load(f)
                overrides.update(file_overrides)
                logging.info(f"Loaded {len(file_overrides)} additional manual overrides from {MANUAL_OVERRIDES_FILE}")
        except Exception as e:
            logging.error(f"Error loading manual overrides file: {e}")
    
    logging.info(f"Total manual overrides loaded: {len(overrides)}")
    return overrides

def save_manual_overrides_template():
    """
    Create a template file for additional manual overrides
    """
    if not os.path.exists(MANUAL_OVERRIDES_FILE):
        template = {
            "_comment": "Add product-specific category overrides here",
            "_format": "product-id-from-url: category_id",
            "_example": "some-product-name-abc123: 602",
            "_note": "These will be added to the existing 242 manual overrides"
        }
        
        try:
            with open(MANUAL_OVERRIDES_FILE, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            logging.info(f"Created manual overrides template: {MANUAL_OVERRIDES_FILE}")
        except Exception as e:
            logging.error(f"Error creating manual overrides template: {e}")

def map_to_google_category(product_id, category_name, title, brand, manual_overrides):
    """
    Map to Google category with manual overrides taking highest priority
    """
    # HIGHEST PRIORITY: Check manual overrides first
    if product_id in manual_overrides:
        category_id = manual_overrides[product_id]
        logging.info(f"🎯 MANUAL OVERRIDE: '{product_id}' -> {category_id}")
        return category_id
    
    # SECOND PRIORITY: Specific product name patterns
    title_lower = title.lower()
    specific_patterns = [
        "David Bust Black Side Table",
        "David Bust White Side Table", 
        "Abracadabra Coffee Cups Set",
        "Fancy Tea Cup Set with Saucer",
        "Good Morning Mug",
        "Cozy Cappuccino Mug Set",
        "Set of 6 Colored Goblets",
        "Che Bello Dessert Plate",
        "Pearl Parade Bowl"
    ]
    
    for pattern in specific_patterns:
        if pattern.lower() in title_lower:
            if pattern in CATEGORY_MAPPING:
                logging.info(f"📝 Specific pattern match: '{pattern}' -> {CATEGORY_MAPPING[pattern]}")
                return CATEGORY_MAPPING[pattern]
    
    # THIRD PRIORITY: Category name matching
    if category_name in CATEGORY_MAPPING:
        logging.info(f"📂 Category match: '{category_name}' -> {CATEGORY_MAPPING[category_name]}")
        return CATEGORY_MAPPING[category_name]
        
    # FOURTH PRIORITY: Category keyword matching
    for keyword, google_id in CATEGORY_MAPPING.items():
        if len(keyword) > 2 and keyword.lower() in category_name.lower():
            logging.info(f"🔍 Category keyword match: '{keyword}' in '{category_name}' -> {google_id}")
            return google_id
    
    # FIFTH PRIORITY: Title keyword matching (filtered)
    for keyword, google_id in CATEGORY_MAPPING.items():
        if len(keyword) > 3 and keyword.lower() in title_lower:
            generic_words = ['table', 'black', 'white', 'side', 'set', 'large', 'small', 'medium']
            if keyword.lower() not in generic_words:
                logging.info(f"📄 Title keyword match: '{keyword}' in '{title}' -> {google_id}")
                return google_id
            
    # SIXTH PRIORITY: Brand matching
    if brand in CATEGORY_MAPPING:
        logging.info(f"🏷️ Brand match: '{brand}' -> {CATEGORY_MAPPING[brand]}")
        return CATEGORY_MAPPING[brand]
    
    # DEFAULT FALLBACK
    logging.info(f"⚡ Default category for: '{title}' ({brand}) -> {DEFAULT_GOOGLE_CATEGORY}")
    return DEFAULT_GOOGLE_CATEGORY

def extract_product_data(url, manual_overrides):
    try:
        logging.info(f"Extracting data from: {url}")
        
        time.sleep(random.uniform(1, 2))
        
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://joyandco.com/",
            "DNT": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 404:
            logging.error(f"Product not found (404): {url}")
            return None
        elif response.status_code == 403:
            logging.error(f"Access forbidden (403): {url}")
            return None
        elif response.status_code != 200:
            logging.error(f"HTTP error {response.status_code}: {url}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product ID from URL
        product_id = url.split("/")[-1]
        
        # Get title - Enhanced selectors
        title_selectors = [
            ".col-md-6 h2",
            "h1",
            ".product-title",
            ".product-name",
            "h2.product-title",
            ".page-title"
        ]
        
        title = "No Title"
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                title = title_tag.get_text(strip=True)
                break
                
        logging.info(f"Title extracted: {title}")
        
        # Get description - Enhanced extraction
        description_selectors = [
            "#description .text-body",
            ".product-description",
            ".description",
            ".product-content"
        ]
        
        description = "No Description"
        for selector in description_selectors:
            description_div = soup.select_one(selector)
            if description_div:
                description = description_div.get_text(strip=True)
                break
                
        logging.info(f"Description extracted: {len(description)} characters")
        
        # Get image - Enhanced image extraction
        image_selectors = [
            ".cz-preview-item.active img.cz-image-zoom",
            ".cz-preview-item img.cz-image-zoom",
            ".product-image img",
            ".main-image img",
            "img.product-photo"
        ]
        
        image_link = ""
        for selector in image_selectors:
            img_element = soup.select_one(selector)
            if img_element and 'src' in img_element.attrs:
                image_link = img_element['src']
                break
        
        logging.info(f"Primary image extracted: {image_link}")
        
        # Get editor notes and brand info
        editor_notes_div = soup.select_one("#editor_notes .text-body")
        brand_info_div = soup.select_one("#about_the_brand .text-body")
        
        editor_notes = editor_notes_div.get_text(strip=True) if editor_notes_div else ""
        brand_info = brand_info_div.get_text(strip=True) if brand_info_div else ""
        
        # Create rich description
        rich_description = description
        if editor_notes:
            rich_description += f"\n\nEDITOR'S NOTE:\n{editor_notes}"
        if brand_info:
            rich_description += f"\n\nABOUT THE BRAND:\n{brand_info}"
        
        # Get all images
        image_elements = soup.select(".cz-preview-item img.cz-image-zoom")
        all_images = []
        for img in image_elements:
            if 'src' in img.attrs and img['src'] not in all_images:
                all_images.append(img['src'])
        
        additional_images = [img for img in all_images if img != image_link]
        
        # Get price - Enhanced price extraction
        price_selectors = [
            ".price",
            ".product-price",
            ".price-current",
            ".current-price"
        ]
        
        price = "0.00"
        for selector in price_selectors:
            price_div = soup.select_one(selector)
            if price_div:
                price_text = price_div.get_text(strip=True)
                price_match = re.search(r'(\d+(?:\.\d+)?)', price_text)
                if price_match:
                    price = price_match.group(1)
                    if '.' not in price:
                        price = f"{price}.00"
                    elif len(price.split('.')[1]) == 1:
                        price = f"{price}0"
                    break
                    
        logging.info(f"Price extracted: {price}")
        
        # Get brand - Enhanced brand extraction
        brand_selectors = [
            "p.pic-info",
            ".brand-name",
            ".product-brand",
            ".brand"
        ]
        
        brand = "Joy & Co"
        for selector in brand_selectors:
            brand_tag = soup.select_one(selector)
            if brand_tag:
                brand = brand_tag.get_text(strip=True)
                break
                
        logging.info(f"Brand extracted: {brand}")
        
        # Get category - Enhanced breadcrumb extraction
        breadcrumbs = []
        breadcrumb_selectors = [
            ".breadcrumbs a",
            ".breadcrumb a",
            ".navigation a"
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb_elements = soup.select(selector)
            if breadcrumb_elements:
                for crumb in breadcrumb_elements[1:-1]:  # Skip home and current page
                    breadcrumbs.append(crumb.get_text(strip=True))
                break
        
        category = " > ".join(breadcrumbs) if breadcrumbs else "Uncategorized"
        
        # Map to Google category
        google_product_category = map_to_google_category(product_id, category, title, brand, manual_overrides)
        logging.info(f"Final Google category assignment: {google_product_category} for '{title}'")
        
        # Stock status - Enhanced availability detection
        stock_status = "in stock"
        out_of_stock_selectors = [
            ".out-of-stock-label",
            ".sold-out",
            ".unavailable"
        ]
        
        for selector in out_of_stock_selectors:
            if soup.select_one(selector):
                stock_status = "out of stock"
                break
        
        # Low inventory check
        price_span = price_div.select_one("span.d-block") if 'price_div' in locals() and price_div else None
        if price_span:
            last_items_text = price_span.get_text(strip=True)
            if "last" in last_items_text.lower() and "left" in last_items_text.lower():
                num_match = re.search(r'(\d+)', last_items_text)
                if num_match and int(num_match.group(1)) <= 3:
                    stock_status = "limited availability"
            
        # Variants
        variants = []
        variant_elements = soup.select(".quantity-cart select option")
        if variant_elements:
            for variant_el in variant_elements[1:]:
                variant_name = variant_el.get_text(strip=True)
                variant_value = variant_el.get('value', '')
                if variant_name and variant_value:
                    variants.append({"name": variant_name, "value": variant_value})

        # MPN
        mpn = product_id
        code_info = soup.select_one(".code-info")
        if code_info:
            code_match = re.search(r'Product code - (\w+)', code_info.get_text(strip=True))
            if code_match:
                mpn = code_match.group(1)

        product_data = {
            "id": product_id,
            "title": title,
            "description": description,
            "rich_description": rich_description,
            "link": url,
            "image_link": image_link,
            "additional_image_link": additional_images[0] if additional_images else "",
            "additional_images": additional_images,
            "availability": stock_status,
            "price": f"{price} AED",
            "brand": brand,
            "condition": "new",
            "category": category,
            "google_product_category": google_product_category,
            "mpn": mpn,
            "gtin": "",
            "variants": json.dumps(variants) if variants else ""
        }
        
        logging.info(f"✅ Successfully extracted data for product: {product_data['id']}")
        return product_data
        
    except Exception as e:
        logging.error(f"Failed to extract data from {url}: {e}")
        return None

def generate_csv(products):
    try:
        logging.info(f"Generating CSV at {CSV_OUTPUT} with {len(products)} products")
        
        csv_fields = ["id", "title", "description", "link", "image_link", "additional_image_link",
                      "availability", "price", "brand", "condition", "category"]
        
        string_products = []
        for product in products:
            string_product = {}
            for field in csv_fields:
                value = product.get(field, "")
                string_product[field] = str(value) if value is not None else ""
            string_products.append(string_product)
        
        with open(CSV_OUTPUT, mode='w', newline='', encoding='utf-8') as file:
            if not products:
                logging.warning("No products to write to CSV")
                return False
                
            writer = csv.DictWriter(file, fieldnames=csv_fields)
            writer.writeheader()
            for product in string_products:
                writer.writerow(product)
        
        if os.path.exists(CSV_OUTPUT):
            file_size = os.path.getsize(CSV_OUTPUT)
            logging.info(f"CSV file successfully created at {CSV_OUTPUT}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"CSV file was not created at {CSV_OUTPUT}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating CSV file: {e}")
        return False

def generate_google_merchant_feed(products):
    try:
        logging.info(f"Generating Google Merchant feed at {GOOGLE_MERCHANT_CSV} with {len(products)} products")
        
        google_fields = [
            "id", "title", "description", "link", "image_link", "additional_image_link",
            "availability", "price", "brand", "condition", "google_product_category", 
            "mpn", "gtin"
        ]
        
        google_products = []
        for product in products:
            google_product = {}
            for field in google_fields:
                value = product.get(field, "")
                google_product[field] = str(value) if value is not None else ""
            google_products.append(google_product)
        
        with open(GOOGLE_MERCHANT_CSV, mode='w', newline='', encoding='utf-8') as file:
            if not products:
                logging.warning("No products to write to Google Merchant feed")
                return False
                
            writer = csv.DictWriter(file, fieldnames=google_fields)
            writer.writeheader()
            for product in google_products:
                writer.writerow(product)
        
        if os.path.exists(GOOGLE_MERCHANT_CSV):
            file_size = os.path.getsize(GOOGLE_MERCHANT_CSV)
            logging.info(f"Google Merchant feed successfully created at {GOOGLE_MERCHANT_CSV}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"Google Merchant feed was not created at {GOOGLE_MERCHANT_CSV}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating Google Merchant feed: {e}")
        return False

def generate_xml(products):
    try:
        logging.info(f"Generating XML at {XML_OUTPUT} with {len(products)} products")
        
        root = ET.Element("products")
        for p in products:
            product = ET.SubElement(root, "product")
            
            for k, v in p.items():
                if k in ["additional_images", "variants"]:
                    continue
                    
                el = ET.SubElement(product, k)
                el.text = str(v) if v is not None else ""
            
            if p.get("additional_images"):
                images_el = ET.SubElement(product, "additional_images")
                for img_url in p["additional_images"]:
                    img_el = ET.SubElement(images_el, "image")
                    img_el.text = img_url
            
            if p.get("variants") and p["variants"]:
                try:
                    variants_data = json.loads(p["variants"])
                    if variants_data:
                        variants_el = ET.SubElement(product, "variants")
                        for variant in variants_data:
                            variant_el = ET.SubElement(variants_el, "variant")
                            for k, v in variant.items():
                                var_attr = ET.SubElement(variant_el, k)
                                var_attr.text = str(v)
                except Exception as e:
                    logging.error(f"Error processing variants for product {p.get('id')}: {e}")
        
        tree = ET.ElementTree(root)
        tree.write(XML_OUTPUT, encoding='utf-8', xml_declaration=True)
        
        if os.path.exists(XML_OUTPUT):
            file_size = os.path.getsize(XML_OUTPUT)
            logging.info(f"XML file successfully created at {XML_OUTPUT}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"XML file was not created at {XML_OUTPUT}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating XML file: {e}")
        return False

def main():
    logging.info("🚀 Starting COMPLETE Enhanced Product Feed Generator with Manual Override System")
    logging.info("=" * 100)
    logging.info("🛡️ PROTECTION SYSTEM: ALL 242+ of your manual Google Sheet assignments are preserved!")
    logging.info("🎯 PRIORITY ORDER:")
    logging.info("   1. Manual product-specific overrides (HIGHEST) - Your exact Google Sheet assignments")
    logging.info("   2. Specific product name patterns")  
    logging.info("   3. Category name matching")
    logging.info("   4. Category keyword matching")
    logging.info("   5. Title keyword matching (filtered)")
    logging.info("   6. Brand matching")
    logging.info("   7. Default fallback (Category 602 - Vases)")
    logging.info("=" * 100)
    
    try:
        manual_overrides = load_manual_overrides()
        save_manual_overrides_template()
        
        if not os.path.exists(INPUT_CSV):
            logging.error(f"Input file does not exist: {INPUT_CSV}")
            logging.error("Make sure the crawler has run successfully first!")
            return
            
        urls = []
        with open(INPUT_CSV, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            urls = [row["url"] for row in reader if row.get("url")]
        
        logging.info(f"📄 Read {len(urls)} URLs from {INPUT_CSV}")
        logging.info(f"🛡️ Using {len(manual_overrides)} manual category overrides")
        logging.info(f"📊 Manual overrides cover 26+ different categories from your Google Sheet")

        products = []
        successful_extractions = 0
        failed_extractions = 0
        
        for i, url in enumerate(urls, 1):
            logging.info(f"📦 Processing product {i}/{len(urls)}: {url}")
            data = extract_product_data(url, manual_overrides)
            if data:
                products.append(data)
                successful_extractions += 1
            else:
                failed_extractions += 1
                
            # Progress update every 25 products
            if i % 25 == 0:
                logging.info(f"🔄 Progress: {i}/{len(urls)} processed, {successful_extractions} successful, {failed_extractions} failed")

        logging.info("=" * 100)
        logging.info(f"✅ EXTRACTION COMPLETE: Processed {len(products)} products out of {len(urls)} URLs")
        logging.info(f"📊 Success rate: {(successful_extractions/len(urls)*100):.1f}%")
        logging.info("=" * 100)

        if products:
            override_count = sum(1 for p in products if p['id'] in manual_overrides)
            pattern_count = len(products) - override_count
            
            logging.info(f"🎯 Manual overrides used: {override_count}/{len(products)} products")
            logging.info(f"📝 Pattern matching used: {pattern_count}/{len(products)} products")
            
            # Show sample of discovered products
            logging.info("📋 Sample of processed products:")
            for i, product in enumerate(products[:5], 1):
                logging.info(f"   {i}. {product['title']} -> Category: {product['google_product_category']}")
            
            if len(products) > 5:
                logging.info(f"   ... and {len(products) - 5} more products")
            
            xml_success = generate_xml(products)
            csv_success = generate_csv(products)
            google_success = generate_google_merchant_feed(products)
            
            if csv_success and xml_success and google_success:
                print("=" * 80)
                print(f"✅ Successfully generated feeds for {len(products)} products.")
                print(f"🎯 Manual overrides preserved: {override_count} products")
                print(f"📝 Pattern matching applied: {pattern_count} products")
                print(f"📁 Files created:")
                print(f"   - {CSV_OUTPUT}")
                print(f"   - {XML_OUTPUT}") 
                print(f"   - {GOOGLE_MERCHANT_CSV}")
                print(f"🛡️ Your manual category assignments are 100% PROTECTED!")
                print(f"🔄 Future crawls will maintain your preferred categorization")
                print("=" * 80)
            else:
                if not csv_success:
                    print(f"⚠️ Failed to generate standard CSV feed.")
                if not xml_success:
                    print(f"⚠️ Failed to generate XML feed.")
                if not google_success:
                    print(f"⚠️ Failed to generate Google Merchant feed.")
        else:
            logging.warning("No products were processed.")
            print("⚠️ No products were processed.")
            print("🔍 Possible issues:")
            print("   1. Check if the crawler found any product URLs")
            print("   2. Verify the website is accessible")
            print("   3. Check for changes in the website structure")
            print("   4. Review the extraction selectors")
            
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
