#!/usr/bin/env python3
"""
Google Product Category Updater - Enhanced Description Analysis Version
Automatically updates Google product categories with advanced description analysis for better accuracy.

Usage:
1. Place this script in the same folder as your 'google_merchant_feed.csv' file
2. Optional: Create 'manual_overrides.txt' for specific product overrides
3. Run: python category_updater.py
4. Check the generated files and follow quick-fix recommendations

New Features:
- Advanced description analysis with context understanding
- Specialized categories for perfumes, home decor, photo frames, etc.
- Smart material and function detection
- Enhanced scoring with description bonuses
"""

import pandas as pd
import re
import os
from datetime import datetime
from collections import defaultdict

def load_csv_file():
    """Load the merchant feed CSV file"""
    csv_file = 'google_merchant_feed.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found in current directory")
        print("Please make sure the file exists and try again.")
        return None
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} products from {csv_file}")
        return df
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None

def load_manual_overrides():
    """Load manual category overrides from file"""
    overrides = {}
    override_file = 'manual_overrides.txt'
    
    if os.path.exists(override_file):
        try:
            with open(override_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            product_id, category_id = line.split(',')
                            overrides[product_id.strip()] = int(category_id.strip())
                        except ValueError:
                            print(f"⚠️ Invalid format in {override_file} line {line_num}: {line}")
            
            if overrides:
                print(f"✅ Loaded {len(overrides)} manual overrides from {override_file}")
        except Exception as e:
            print(f"⚠️ Error reading {override_file}: {e}")
    
    return overrides

def get_comprehensive_category_mappings():
    """Comprehensive category mappings with specialized categories"""
    return {
        # Kitchen & Dining - Drinkware (Enhanced)
        'coffee cup': 6049, 'coffee cups': 6049, 'tea cup': 6049, 'tea cups': 6049,
        'espresso cup': 6049, 'cappuccino cup': 6049, 'latte cup': 6049,
        'mug': 2169, 'mugs': 2169, 'coffee mug': 2169, 'tea mug': 2169,
        'tumbler': 2951, 'tumblers': 2951, 'travel mug': 2951, 'insulated mug': 2951,
        'glass': 674, 'glasses': 674, 'drinking glass': 674, 'water glass': 674,
        'wine glass': 674, 'beer glass': 674, 'cocktail glass': 674,
        'cup': 6049, 'cups': 6049, 'teacup': 6049, 'coffee cup': 6049,
        
        # Kitchen & Dining - Dinnerware (Enhanced)
        'dinner plate': 3553, 'dessert plate': 3553, 'serving plate': 3553, 'salad plate': 3553,
        'plate': 3553, 'plates': 3553, 'ceramic plate': 3553, 'porcelain plate': 3553,
        'charger plate': 3553, 'side plate': 3553, 'bread plate': 3553,
        'deep plate': 3498, 'bowl': 3498, 'bowls': 3498, 'serving bowl': 3498,
        'dish': 3498, 'dishes': 3498, 'pasta bowl': 3498, 'cereal bowl': 3498,
        'soup bowl': 3498, 'salad bowl': 3498, 'mixing bowl': 3498, 'fruit bowl': 3498,
        'rice bowl': 3498, 'noodle bowl': 3498, 'ramen bowl': 3498,
        
        # Kitchen & Dining - Serveware (Enhanced)
        'serving tray': 4009, 'tray': 4009, 'trays': 4009, 'platter': 4009,
        'cheese board': 4009, 'cutting board': 4009, 'serving board': 4009,
        'jug': 3330, 'pitcher': 3330, 'serving pitcher': 3330, 'carafe': 3330,
        'water jug': 3330, 'milk jug': 3330, 'gravy boat': 3330, 'sauce boat': 3330,
        'teapot': 3330, 'coffee pot': 3330, 'creamer': 3330, 'sugar bowl': 3330,
        
        # Home & Garden - Decor (Significantly Enhanced)
        'vase': 602, 'vases': 602, 'flower vase': 602, 'decorative vase': 602,
        'bud vase': 602, 'floor vase': 602, 'table vase': 602,
        'trinket tray': 6456, 'decorative tray': 6456, 'jewelry tray': 6456, 'catchall tray': 6456,
        'ornament': 602, 'decoration': 602, 'figurine': 602, 'sculpture': 602,
        'statue': 602, 'decorative object': 602, 'accent piece': 602,
        
        # NEW: Photo Frames & Wall Decor
        'photo frame': 3367, 'picture frame': 3367, 'frame': 3367, 'frames': 3367,
        'wall art': 500044, 'artwork': 500044, 'painting': 500044, 'print': 500044,
        'poster': 500044, 'canvas': 500044, 'wall decor': 500044,
        'mirror': 583, 'mirrors': 583, 'wall mirror': 583, 'decorative mirror': 583,
        
        # NEW: Perfumes & Fragrances (Major Addition)
        'perfume': 2915, 'cologne': 2915, 'fragrance': 2915, 'eau de parfum': 2915,
        'eau de toilette': 2915, 'eau de cologne': 2915, 'scent': 2915,
        'oud': 2915, 'oud perfume': 2915, 'oud fragrance': 2915, 'arabic perfume': 2915,
        'attar': 2915, 'essential oil': 2915, 'perfume oil': 2915,
        'body spray': 2915, 'body mist': 2915, 'aftershave': 2915,
        
        # Home & Garden - Home Fragrance (Enhanced)
        'candle holder': 2784, 'candle': 588, 'candles': 588, 'scented candle': 588,
        'tea light': 588, 'pillar candle': 588, 'votive candle': 588, 'jar candle': 588,
        'candlestick': 2784, 'candelabra': 2784, 'lantern': 2784, 'oil lamp': 2784,
        'diffuser': 2915, 'reed diffuser': 2915, 'air freshener': 2915,
        'incense': 588, 'incense burner': 2784, 'wax melt': 588,
        
        # Kitchen & Dining - Flatware (Enhanced)
        'spoon': 3939, 'spoons': 3939, 'teaspoon': 3939, 'tablespoon': 3939,
        'soup spoon': 3939, 'dessert spoon': 3939, 'serving spoon': 3939,
        'fork': 4015, 'forks': 4015, 'dinner fork': 4015, 'salad fork': 4015,
        'dessert fork': 4015, 'serving fork': 4015,
        'knife': 3844, 'knives': 3844, 'butter knife': 3844, 'steak knife': 3844,
        'dinner knife': 3844, 'cheese knife': 3844,
        'cutlery': 3939, 'flatware': 3939, 'silverware': 3939, 'utensils': 3939,
        
        # Kitchen & Dining - Cookware & Bakeware (Enhanced)
        'pot': 663, 'pots': 663, 'stock pot': 663, 'soup pot': 663, 'sauce pot': 663,
        'pan': 662, 'pans': 662, 'frying pan': 662, 'skillet': 662, 'saute pan': 662,
        'baking pan': 641, 'cookie sheet': 641, 'baking tray': 641, 'sheet pan': 641,
        'casserole': 663, 'dutch oven': 663, 'roasting pan': 641, 'cake pan': 641,
        'muffin pan': 641, 'loaf pan': 641, 'pie pan': 641,
        
        # Storage & Organization (Enhanced)
        'jar': 674, 'jars': 674, 'storage jar': 674, 'cookie jar': 674, 'spice jar': 674,
        'bottle': 674, 'bottles': 674, 'water bottle': 674, 'wine bottle': 674,
        'container': 674, 'containers': 674, 'food container': 674, 'storage box': 674,
        'basket': 574, 'baskets': 574, 'storage basket': 574, 'wicker basket': 574,
        
        # NEW: Textiles & Linens
        'tablecloth': 1985, 'table cloth': 1985, 'table linen': 1985,
        'napkin': 1985, 'napkins': 1985, 'table napkin': 1985,
        'placemat': 1985, 'placemats': 1985, 'table mat': 1985,
        'runner': 1985, 'table runner': 1985, 'linen runner': 1985,
        'coaster': 1985, 'coasters': 1985, 'drink coaster': 1985,
        
        # NEW: Lighting
        'lamp': 594, 'lamps': 594, 'table lamp': 594, 'desk lamp': 594,
        'floor lamp': 594, 'bedside lamp': 594, 'reading lamp': 594,
        'light': 594, 'lights': 594, 'lighting': 594,
        'chandelier': 594, 'pendant light': 594, 'ceiling light': 594,
        
        # NEW: Clocks & Timepieces
        'clock': 3890, 'clocks': 3890, 'wall clock': 3890, 'table clock': 3890,
        'desk clock': 3890, 'alarm clock': 3890, 'mantle clock': 3890,
        
        # Material-based defaults (Enhanced)
        'ceramic': 3553, 'porcelain': 3553, 'stoneware': 3553, 'earthenware': 3553,
        'bone china': 3553, 'fine china': 3553, 'china': 3553,
        'glass': 674, 'crystal': 674, 'lead crystal': 674, 'cut glass': 674,
        'bamboo': 3553, 'wood': 3553, 'wooden': 3553, 'teak': 3553,
        'melamine': 3553, 'plastic': 674, 'acrylic': 674,
        'stainless steel': 3939, 'metal': 3939, 'aluminum': 3939, 'copper': 3939,
        'brass': 3939, 'silver': 3939, 'gold': 3939,
        
        # Function-based patterns (Enhanced)
        'serving': 4009, 'decorative': 602, 'ornamental': 602, 'accent': 602,
        'statement': 602, 'centerpiece': 602, 'display': 602,
        'handmade': 602, 'artisan': 602, 'handcrafted': 602, 'artistic': 602,
        'vintage': 602, 'antique': 602, 'retro': 602, 'classic': 3553,
        'modern': 3553, 'contemporary': 3553, 'minimalist': 3553, 'elegant': 3553,
        
        # Size/quantity indicators (Enhanced)
        'set': 3553, 'collection': 3553, 'series': 3553, 'range': 3553,
        'pair': 3553, 'duo': 3553, 'individual': 6049, 'single': 6049,
        'mini': 6049, 'small': 6049, 'large': 4009, 'jumbo': 4009,
        'family': 4009, 'party': 4009, 'entertaining': 4009,
        
        # Room/usage context (New)
        'kitchen': 3553, 'dining': 3553, 'tableware': 3553, 'dinnerware': 3553,
        'serveware': 4009, 'drinkware': 674, 'cookware': 662, 'bakeware': 641,
        'bedroom': 602, 'living room': 602, 'bathroom': 2915, 'office': 3367,
        'study': 3367, 'home': 602, 'garden': 602, 'outdoor': 4009,
    }

def get_description_specific_keywords():
    """Keywords that are more likely to appear in descriptions than titles"""
    return {
        # Perfume/Fragrance descriptions
        'long lasting': 2915, 'long-lasting': 2915, 'all day': 2915,
        'oriental scent': 2915, 'floral notes': 2915, 'woody notes': 2915,
        'citrus notes': 2915, 'musky': 2915, 'fresh scent': 2915,
        'luxury fragrance': 2915, 'premium perfume': 2915,
        'arabic scent': 2915, 'middle eastern': 2915,
        'spray bottle': 2915, 'atomizer': 2915, 'perfume bottle': 2915,
        
        # Home decor descriptions
        'wall hanging': 500044, 'hang on wall': 500044, 'wall mounted': 500044,
        'living room decor': 602, 'bedroom decor': 602, 'home decoration': 602,
        'decorative piece': 602, 'accent piece': 602, 'conversation starter': 602,
        'centerpiece': 602, 'focal point': 602, 'eye catching': 602,
        
        # Photo frame descriptions
        'holds photo': 3367, 'picture display': 3367, 'photo display': 3367,
        'memory keeper': 3367, 'cherished moments': 3367, 'family photo': 3367,
        'wedding photo': 3367, 'graduation photo': 3367,
        
        # Lighting descriptions
        'provides light': 594, 'illumination': 594, 'ambient lighting': 594,
        'mood lighting': 594, 'task lighting': 594, 'warm glow': 594,
        'bright light': 594, 'soft light': 594, 'dimmer': 594,
        
        # Tableware usage descriptions
        'dining experience': 3553, 'meal time': 3553, 'dinner party': 3553,
        'special occasion': 3553, 'everyday use': 3553, 'family dinner': 3553,
        'entertaining guests': 4009, 'hosting': 4009, 'serve food': 4009,
        'serve drinks': 674, 'beverage service': 674, 'drink serving': 674,
        
        # Functional descriptions
        'dishwasher safe': 3553, 'microwave safe': 3553, 'oven safe': 641,
        'food grade': 674, 'bpa free': 674, 'leak proof': 674,
        'easy to clean': 3553, 'non slip': 4009, 'stackable': 3553,
        
        # Material quality descriptions
        'handcrafted': 602, 'artisan made': 602, 'hand painted': 602,
        'glazed finish': 3553, 'matte finish': 602, 'glossy finish': 674,
        'textured surface': 602, 'smooth surface': 674,
        
        # Size and capacity descriptions
        'holds 8 ounces': 674, 'holds 12 ounces': 2169, 'holds 16 ounces': 2951,
        'family size': 4009, 'individual portion': 6049, 'single serving': 6049,
        'large capacity': 4009, 'compact size': 6049,
    }

def get_brand_defaults():
    """Default categories for specific brands (customize as needed)"""
    return {
        # Add your brand-specific defaults here
        # 'brand_name': category_id,
    }

def get_category_reference():
    """Expanded category ID to Name mapping for reference"""
    return {
        588: 'Home & Garden > Decor > Home Fragrances > Candles',
        574: 'Home & Garden > Decor > Baskets',
        583: 'Home & Garden > Decor > Mirrors',
        594: 'Home & Garden > Lighting > Lamps',
        602: 'Home & Garden > Decor > Vases',
        641: 'Home & Garden > Kitchen & Dining > Cookware & Bakeware > Bakeware > Baking & Cookie Sheets',
        662: 'Home & Garden > Kitchen & Dining > Cookware & Bakeware > Cookware > Skillets & Frying Pans',
        663: 'Home & Garden > Kitchen & Dining > Cookware & Bakeware > Cookware > Stock Pots',
        674: 'Home & Garden > Kitchen & Dining > Tableware > Drinkware',
        1985: 'Home & Garden > Kitchen & Dining > Table Linens',
        2169: 'Home & Garden > Kitchen & Dining > Tableware > Drinkware > Mugs',
        2784: 'Home & Garden > Decor > Home Fragrance Accessories > Candle Holders',
        2915: 'Health & Beauty > Personal Care > Cosmetics > Fragrance',
        2951: 'Home & Garden > Kitchen & Dining > Tableware > Drinkware > Tumblers',
        3330: 'Home & Garden > Kitchen & Dining > Tableware > Serveware > Serving Pitchers & Carafes',
        3367: 'Home & Garden > Decor > Picture Frames',
        3498: 'Home & Garden > Kitchen & Dining > Tableware > Dinnerware > Bowls',
        3553: 'Home & Garden > Kitchen & Dining > Tableware > Dinnerware > Plates',
        3844: 'Home & Garden > Kitchen & Dining > Tableware > Flatware > Table Knives',
        3890: 'Home & Garden > Decor > Clocks',
        3939: 'Home & Garden > Kitchen & Dining > Tableware > Flatware > Spoons',
        4009: 'Home & Garden > Kitchen & Dining > Tableware > Serveware > Serving Trays',
        4015: 'Home & Garden > Kitchen & Dining > Tableware > Flatware > Forks',
        6049: 'Home & Garden > Kitchen & Dining > Tableware > Drinkware > Coffee & Tea Cups',
        6456: 'Home & Garden > Decor > Decorative Trays',
        500044: 'Home & Garden > Decor > Artwork'
    }

def extract_enhanced_keywords(text):
    """Enhanced keyword extraction with phrase detection"""
    if pd.isna(text) or not text:
        return []
    
    # Convert to lowercase and clean
    text = str(text).lower()
    text = re.sub(r'[^\w\s-]', ' ', text)
    
    # Split into words
    words = text.split()
    
    # Create keywords: individual words + 2-word phrases + 3-word phrases
    keywords = []
    for i, word in enumerate(words):
        if len(word) > 2:
            keywords.append(word)
        
        # Add 2-word phrases
        if i < len(words) - 1:
            phrase2 = f"{word} {words[i+1]}"
            keywords.append(phrase2)
        
        # Add 3-word phrases (important for descriptions)
        if i < len(words) - 2:
            phrase3 = f"{word} {words[i+1]} {words[i+2]}"
            keywords.append(phrase3)
    
    # Filter out common stop words but keep meaningful phrases
    stop_words = {
        'the', 'and', 'for', 'with', 'from', 'this', 'that', 'are', 'was', 'will',
        'have', 'has', 'been', 'they', 'their', 'them', 'than', 'your', 'you',
        'our', 'all', 'any', 'can', 'new', 'made', 'home', 'design',
        'style', 'color', 'size', 'each', 'perfect', 'beautiful', 'premium',
        'quality', 'studio', 'creative', 'features', 'brought',
        'graphic', 'images', 'expressed', 'wonder', 'inch', 'inches',
        'great', 'best', 'good', 'nice', 'amazing', 'awesome'
    }
    
    # Only filter single words that are stop words, keep phrases
    filtered_keywords = []
    for kw in keywords:
        if ' ' in kw:  # Multi-word phrase - keep it
            filtered_keywords.append(kw)
        elif kw not in stop_words:  # Single word not in stop words
            filtered_keywords.append(kw)
    
    return filtered_keywords

def categorize_product_enhanced(row, category_mappings, description_keywords, brand_defaults, manual_overrides):
    """Enhanced categorization with advanced description analysis"""
    product_id = str(row.get('id', '')) if row.get('id') is not None else ''
    
    # Handle NaN values properly
    title_raw = row.get('title', '')
    title = str(title_raw) if pd.notna(title_raw) and title_raw is not None else ''
    
    description_raw = row.get('description', '')
    description = str(description_raw) if pd.notna(description_raw) and description_raw is not None else ''
    
    brand_raw = row.get('brand', '')
    brand = str(brand_raw) if pd.notna(brand_raw) and brand_raw is not None else ''
    
    current_category = row.get('google_product_category', '')
    
    # Check manual overrides first
    if product_id in manual_overrides:
        return {
            'original_category': current_category,
            'suggested_category': manual_overrides[product_id],
            'confidence': 'MANUAL',
            'score': 100,
            'matched_keyword': 'manual_override',
            'changed': manual_overrides[product_id] != current_category,
            'source': 'Manual Override'
        }
    
    title_lower = title.lower()
    description_lower = description.lower()
    combined_text = f"{title_lower} {description_lower}"
    
    best_match = None
    best_score = 0
    matched_keyword = None
    match_source = None
    
    # Strategy 1: Enhanced keyword matching with description analysis
    all_keywords = {**category_mappings, **description_keywords}
    
    for keyword, category_id in all_keywords.items():
        if keyword in combined_text:
            score = 15  # Increased base score
            
            # Title match bonus (still highest priority)
            if keyword in title_lower:
                score += 30
                location = "title"
            
            # Description match bonus (NEW - significant improvement)
            elif keyword in description_lower:
                score += 15  # Good bonus for description matches
                location = "description"
            
            # Exact word boundary matches (enhanced)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text):
                score += 20  # Increased bonus for exact matches
            
            # Keyword specificity bonus (enhanced)
            score += len(keyword) * 1.2  # Increased multiplier
            
            # Phrase bonus (multi-word keywords are more specific)
            word_count = len(keyword.split())
            if word_count == 2:
                score += 15
            elif word_count >= 3:
                score += 25  # Big bonus for 3+ word phrases
            
            # Position bonus (earlier in title = more important)
            title_pos = title_lower.find(keyword)
            if title_pos != -1:
                score += max(0, 15 - (title_pos / 8))  # Enhanced position bonus
            
            # Description-specific keyword bonus
            if keyword in description_keywords and keyword in description_lower:
                score += 10  # Bonus for description-specific terms
            
            # Context bonus for related keywords
            context_bonus = calculate_context_bonus(keyword, combined_text, category_id)
            score += context_bonus
            
            if score > best_score:
                best_score = score
                best_match = category_id
                matched_keyword = keyword
                match_source = f'Keyword Match ({location})'
    
    # Strategy 2: Brand-based defaults
    if not best_match and brand.lower() in brand_defaults:
        best_match = brand_defaults[brand.lower()]
        best_score = 20  # Increased brand score
        matched_keyword = f"brand:{brand}"
        match_source = 'Brand Default'
    
    # Strategy 3: Enhanced pattern-based fallbacks
    if not best_match:
        fallback_score = analyze_fallback_patterns(combined_text)
        if fallback_score['category']:
            best_match = fallback_score['category']
            best_score = fallback_score['score']
            matched_keyword = fallback_score['pattern']
            match_source = 'Pattern Fallback'
    
    # Determine confidence level (adjusted thresholds)
    confidence = 'LOW'
    if best_score >= 50:  # Raised threshold for HIGH
        confidence = 'HIGH'
    elif best_score >= 30:  # Raised threshold for MEDIUM
        confidence = 'MEDIUM'
    elif match_source == 'Manual Override':
        confidence = 'MANUAL'
    
    return {
        'original_category': current_category,
        'suggested_category': best_match if best_match else current_category,
        'confidence': confidence,
        'score': best_score,
        'matched_keyword': matched_keyword,
        'changed': bool(best_match and best_match != current_category),
        'source': match_source or 'No Match'
    }

def calculate_context_bonus(keyword, text, category_id):
    """Calculate bonus score based on context and related keywords"""
    bonus = 0
    
    # Perfume/Fragrance context
    if category_id == 2915:  # Fragrance category
        perfume_context = ['scent', 'smell', 'aroma', 'fragrant', 'perfumed', 'aromatic', 
                          'spray', 'bottle', 'ml', 'fluid', 'liquid', 'essential', 'oil']
        bonus += sum(3 for ctx in perfume_context if ctx in text)
    
    # Photo frame context
    elif category_id == 3367:  # Picture frames
        frame_context = ['photo', 'picture', 'image', 'display', 'wall', 'desk', 
                        'memory', 'family', 'wedding', 'graduation']
        bonus += sum(3 for ctx in frame_context if ctx in text)
    
    # Lighting context
    elif category_id == 594:  # Lamps
        light_context = ['bulb', 'watt', 'bright', 'dim', 'glow', 'illumination', 
                        'switch', 'shade', 'cord', 'plug']
        bonus += sum(3 for ctx in light_context if ctx in text)
    
    # Kitchen/Dining context
    elif category_id in [3553, 3498, 674, 2169]:  # Plates, bowls, drinkware
        kitchen_context = ['kitchen', 'dining', 'meal', 'food', 'eat', 'drink', 
                          'dishwasher', 'microwave', 'table', 'dinner']
        bonus += sum(2 for ctx in kitchen_context if ctx in text)
    
    return min(bonus, 15)  # Cap the context bonus

def analyze_fallback_patterns(text):
    """Enhanced fallback pattern analysis"""
    patterns = {
        # Material patterns with smarter defaults
        'glass': {'category': 674, 'score': 18},
        'ceramic': {'category': 3553, 'score': 18},
        'porcelain': {'category': 3553, 'score': 18},
        'crystal': {'category': 674, 'score': 18},
        'wood': {'category': 602, 'score': 16},
        'metal': {'category': 3939, 'score': 16},
        
        # Function patterns
        'decorative': {'category': 602, 'score': 16},
        'serving': {'category': 4009, 'score': 16},
        'storage': {'category': 574, 'score': 16},
        'display': {'category': 3367, 'score': 16},
        
        # Room/usage patterns
        'kitchen': {'category': 3553, 'score': 14},
        'dining': {'category': 3553, 'score': 14},
        'bedroom': {'category': 602, 'score': 14},
        'bathroom': {'category': 2915, 'score': 14},
        'living room': {'category': 602, 'score': 14},
        
        # Set/collection patterns
        'set': {'category': 3553, 'score': 14},
        'collection': {'category': 3553, 'score': 14},
    }
    
    for pattern, info in patterns.items():
        if pattern in text:
            return info
    
    return {'category': None, 'score': 0, 'pattern': None}

def analyze_low_confidence_patterns(results):
    """Analyze patterns in low confidence items for quick fixes"""
    low_confidence_items = [r for r in results if r['analysis']['confidence'] == 'LOW']
    
    if not low_confidence_items:
        return {}
    
    # Group by similar title patterns
    patterns = defaultdict(list)
    
    for result in low_confidence_items:
        title = result['row_data'].get('title', '')
        
        # Handle NaN or non-string titles
        if pd.isna(title) or not isinstance(title, str):
            title = str(title) if title is not None else ''
        
        title = title.lower()
        
        # Extract first 2-3 meaningful words
        words = [w for w in title.split()[:4] if len(w) > 2]
        if len(words) >= 2:
            pattern = ' '.join(words[:2])
            patterns[pattern].append(result)
    
    # Filter patterns with multiple items
    significant_patterns = {k: v for k, v in patterns.items() if len(v) > 1}
    
    return significant_patterns

def generate_quick_fix_recommendations(patterns, category_reference):
    """Generate quick fix recommendations file"""
    if not patterns:
        return
    
    with open('quick_fix_patterns.txt', 'w', encoding='utf-8') as f:
        f.write("QUICK FIX RECOMMENDATIONS - Enhanced Description Analysis\n")
        f.write("=" * 60 + "\n\n")
        f.write("These patterns were found in low-confidence items.\n")
        f.write("Review and assign appropriate categories for batch fixing.\n\n")
        
        for pattern, items in patterns.items():
            f.write(f"PATTERN: '{pattern}' ({len(items)} items)\n")
            f.write("-" * 50 + "\n")
            
            # Show sample titles and descriptions
            f.write("Sample products:\n")
            for item in items[:5]:
                title = item['row_data'].get('title', 'No title')
                desc = item['row_data'].get('description', 'No description')
                desc_short = (desc[:100] + '...') if len(str(desc)) > 100 else desc
                f.write(f"  • {title}\n")
                f.write(f"    Description: {desc_short}\n")
            
            # Suggest most common category from the group
            categories = [item['analysis']['suggested_category'] for item in items 
                         if item['analysis']['suggested_category']]
            if categories:
                most_common = max(set(categories), key=categories.count)
                cat_name = category_reference.get(most_common, f"Category {most_common}")
                f.write(f"\nSuggested category: {most_common} ({cat_name})\n")
            
            f.write(f"\nProduct IDs for batch update:\n")
            for item in items:
                product_id = item['row_data'].get('id', 'No ID')
                f.write(f"{product_id},{most_common if categories else '3553'}\n")
            
            f.write("\n" + "="*60 + "\n\n")

def process_products_enhanced(df, manual_overrides):
    """Process all products with enhanced description analysis"""
    print("\n🔄 Processing products with enhanced description analysis...")
    
    category_mappings = get_comprehensive_category_mappings()
    description_keywords = get_description_specific_keywords()
    brand_defaults = get_brand_defaults()
    results = []
    
    for index, row in df.iterrows():
        analysis = categorize_product_enhanced(row, category_mappings, description_keywords, brand_defaults, manual_overrides)
        
        # Create updated row
        updated_row = row.copy()
        updated_row['google_product_category'] = analysis['suggested_category']
        
        # Add analysis info for review
        result = {
            'row_data': updated_row,
            'analysis': analysis
        }
        results.append(result)
        
        if (index + 1) % 100 == 0:
            print(f"   Processed {index + 1} products...")
    
    print(f"✅ Processed {len(results)} products with enhanced analysis")
    return results

def generate_enhanced_summary(results):
    """Generate enhanced summary statistics"""
    total = len(results)
    changed = sum(1 for r in results if r['analysis']['changed'])
    manual = sum(1 for r in results if r['analysis']['confidence'] == 'MANUAL')
    high_conf = sum(1 for r in results if r['analysis']['confidence'] == 'HIGH')
    medium_conf = sum(1 for r in results if r['analysis']['confidence'] == 'MEDIUM')
    low_conf = sum(1 for r in results if r['analysis']['confidence'] == 'LOW')
    
    # Analyze match sources
    title_matches = sum(1 for r in results if 'title' in str(r['analysis'].get('source', '')))
    desc_matches = sum(1 for r in results if 'description' in str(r['analysis'].get('source', '')))
    
    return {
        'total_products': total,
        'products_changed': changed,
        'manual_overrides': manual,
        'high_confidence': high_conf,
        'medium_confidence': medium_conf,
        'low_confidence': low_conf,
        'title_matches': title_matches,
        'description_matches': desc_matches
    }

def save_enhanced_results(results, original_df):
    """Save the updated CSV and enhanced review report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create updated DataFrame
    updated_rows = [r['row_data'] for r in results]
    updated_df = pd.DataFrame(updated_rows)
    
    # Save updated CSV
    output_file = 'google_merchant_feed_updated.csv'
    updated_df.to_csv(output_file, index=False)
    print(f"✅ Updated feed saved as: {output_file}")
    
    # Create enhanced review report
    category_reference = get_category_reference()
    review_data = []
    
    for i, result in enumerate(results):
        row = result['row_data']
        analysis = result['analysis']
        
        original_cat_name = category_reference.get(analysis['original_category'], 
                                                 f"Category {analysis['original_category']}")
        new_cat_name = category_reference.get(analysis['suggested_category'], 
                                            f"Category {analysis['suggested_category']}")
        
        # Truncate description for readability
        desc_raw = row.get('description', '')
        description = str(desc_raw) if pd.notna(desc_raw) and desc_raw is not None else ''
        desc_short = (description[:150] + '...') if len(description) > 150 else description
        
        review_data.append({
            'id': str(row.get('id', '')) if row.get('id') is not None else '',
            'title': str(row.get('title', '')) if pd.notna(row.get('title')) and row.get('title') is not None else '',
            'description_preview': desc_short,
            'brand': str(row.get('brand', '')) if pd.notna(row.get('brand')) and row.get('brand') is not None else '',
            'original_category': analysis['original_category'],
            'original_category_name': original_cat_name,
            'new_category': analysis['suggested_category'],
            'new_category_name': new_cat_name,
            'confidence': analysis['confidence'],
            'score': analysis['score'],
            'matched_keyword': analysis['matched_keyword'] or '',
            'match_source': analysis.get('source', ''),
            'changed': 'YES' if analysis['changed'] else 'NO',
            'priority': 'HIGH' if analysis['confidence'] == 'LOW' and analysis['changed'] else 'LOW'
        })
    
    review_df = pd.DataFrame(review_data)
    review_file = 'categorization_review_report.csv'
    review_df.to_csv(review_file, index=False)
    print(f"✅ Enhanced review report saved as: {review_file}")
    
    return output_file, review_file, review_df

def print_enhanced_summary_report(summary, results, patterns):
    """Print enhanced summary with description analysis insights"""
    print("\n" + "="*70)
    print("ENHANCED CATEGORIZATION SUMMARY - Description Analysis")
    print("="*70)
    print(f"Total products: {summary['total_products']}")
    print(f"Products with changed categories: {summary['products_changed']}")
    print(f"Manual overrides applied: {summary['manual_overrides']}")
    print(f"High confidence assignments: {summary['high_confidence']}")
    print(f"Medium confidence assignments: {summary['medium_confidence']}")
    print(f"Low confidence assignments: {summary['low_confidence']}")
    
    # NEW: Description analysis insights
    print(f"\n🔍 DESCRIPTION ANALYSIS INSIGHTS:")
    print(f"Title-based matches: {summary['title_matches']}")
    print(f"Description-based matches: {summary['description_matches']}")
    
    improvement_rate = (summary['products_changed'] / summary['total_products']) * 100
    print(f"Overall improvement rate: {improvement_rate:.1f}%")
    
    # Show examples of description-based improvements
    desc_matches = [r for r in results if 'description' in str(r['analysis'].get('source', ''))]
    if desc_matches:
        print(f"\n{'='*70}")
        print("🎯 DESCRIPTION-BASED DISCOVERIES")
        print("="*70)
        print("Products categorized using description analysis:")
        
        category_reference = get_category_reference()
        
        for i, result in enumerate(desc_matches[:5]):
            row = result['row_data']
            analysis = result['analysis']
            title = row.get('title', 'No title')
            desc = str(row.get('description', ''))
            desc_short = (desc[:80] + '...') if len(desc) > 80 else desc
            
            print(f"\n{i+1}. \"{title}\"")
            print(f"   Description: {desc_short}")
            print(f"   Keyword found: \"{analysis['matched_keyword']}\"")
            cat_name = category_reference.get(analysis['suggested_category'], 'Unknown')
            print(f"   Category: {analysis['suggested_category']} ({cat_name})")
            print(f"   Confidence: {analysis['confidence']} (Score: {analysis['score']:.1f})")
    
    # Quick fix recommendations
    if patterns:
        print(f"\n{'='*70}")
        print("🚀 QUICK FIX OPPORTUNITIES")
        print("="*70)
        print(f"Found {len(patterns)} patterns for batch fixing:")
        
        for pattern, items in list(patterns.items())[:3]:
            print(f"\n📋 Pattern: '{pattern}' ({len(items)} items)")
            sample_title = items[0]['row_data'].get('title', 'No title')
            print(f"   Example: {sample_title}")
        
        if len(patterns) > 3:
            print(f"\n   ... and {len(patterns) - 3} more patterns")
        
        print(f"\n💡 Check 'quick_fix_patterns.txt' for detailed batch fix instructions")
    
    # Show high confidence changes
    high_conf_changes = [r for r in results if r['analysis']['changed'] and r['analysis']['confidence'] == 'HIGH']
    if high_conf_changes:
        print(f"\n{'='*70}")
        print("✅ HIGH CONFIDENCE CHANGES (Ready to use)")
        print("="*70)
        
        category_reference = get_category_reference()
        
        for i, result in enumerate(high_conf_changes[:5]):
            row = result['row_data']
            analysis = result['analysis']
            print(f"{i+1}. \"{row.get('title', 'No title')}\"")
            print(f"   {analysis['original_category']} → {analysis['suggested_category']}")
            print(f"   Score: {analysis['score']:.1f}, Keyword: \"{analysis['matched_keyword']}\"")
            print(f"   Source: {analysis.get('source', 'Unknown')}")

def main():
    """Enhanced main function with advanced description analysis"""
    print("🚀 Google Product Category Updater - Enhanced Description Analysis")
    print("="*70)
    print("🔍 NEW FEATURES:")
    print("• Advanced description keyword analysis")
    print("• Specialized categories for perfumes, photo frames, lighting")
    print("• Context-aware scoring with usage patterns")
    print("• Enhanced phrase detection (2-3 word combinations)")
    print("• Smart material and function recognition")
    print("="*70)
    
    # Load CSV file
    df = load_csv_file()
    if df is None:
        return
    
    # Load manual overrides
    manual_overrides = load_manual_overrides()
    
    # Check required columns
    required_columns = ['title', 'google_product_category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Process products with enhanced analysis
    results = process_products_enhanced(df, manual_overrides)
    
    # Analyze patterns for quick fixes
    patterns = analyze_low_confidence_patterns(results)
    
    # Generate enhanced summary
    summary = generate_enhanced_summary(results)
    
    # Save results
    output_file, review_file, review_df = save_enhanced_results(results, df)
    
    # Generate quick fix recommendations
    category_reference = get_category_reference()
    generate_quick_fix_recommendations(patterns, category_reference)
    
    # Print enhanced summary
    print_enhanced_summary_report(summary, results, patterns)
    
    print(f"\n{'='*70}")
    print("PROCESS COMPLETE - Enhanced Description Analysis")
    print("="*70)
    print(f"📁 Files created:")
    print(f"   • {output_file} - Your updated merchant feed")
    print(f"   • {review_file} - Enhanced review report with descriptions")
    if patterns:
        print(f"   • quick_fix_patterns.txt - Batch fix recommendations")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Review description-based discoveries above")
    print(f"   2. Check high confidence changes (ready to use)")
    print(f"   3. Use quick_fix_patterns.txt for remaining items")
    print(f"   4. Create manual_overrides.txt for specific cases")
    print(f"   5. Re-run script after adding overrides")
    print(f"   6. Upload final CSV to merchant center")
    
    print(f"\n🎯 ENHANCED CATEGORIES ADDED:")
    print(f"   • Perfumes & Fragrances (oud, cologne, etc.)")
    print(f"   • Photo Frames & Picture Displays")
    print(f"   • Lighting & Lamps")
    print(f"   • Table Linens & Runners") 
    print(f"   • Clocks & Timepieces")
    print(f"   • Mirrors & Wall Decor")
    print(f"   • Baskets & Storage")

if __name__ == "__main__":
    main()