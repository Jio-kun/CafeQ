"""Self-contained demo cafes and their sample menus."""

DEMO_SHOPS = {
    "demo-sunrise-cafe": {
        "slug": "demo-sunrise-cafe",
        "name": "Sunrise Cafe",
        "tagline": "A bright start, brewed locally.",
        "description": "Neighborhood coffee, fresh bakes, and sunny mornings.",
        "theme": "sunrise",
        "menu": [
            {"id": 1, "category": "Coffee", "name": "Honey Oat Flat White", "price": 110, "description": "Double espresso, silky oat milk, and local wildflower honey."},
            {"id": 2, "category": "Coffee", "name": "Sunrise Spanish Latte", "price": 125, "description": "Our house espresso with chilled milk and a touch of sweetness."},
            {"id": 3, "category": "Coffee", "name": "Coconut Cold Brew", "price": 120, "description": "Slow-steeped coffee finished with creamy coconut."},
            {"id": 4, "category": "Tea & Coolers", "name": "Calamansi Mint Cooler", "price": 95, "description": "Fresh calamansi, garden mint, and sparkling water."},
            {"id": 5, "category": "Bakery", "name": "Ube Morning Bun", "price": 75, "description": "Flaky cinnamon bun swirled with purple yam."},
            {"id": 6, "category": "Bakery", "name": "Cheddar Pandesal", "price": 55, "description": "Soft baked rolls with a savory cheese center."},
        ],
    },
    "demo-moonlight-coffee": {
        "slug": "demo-moonlight-coffee",
        "name": "Moonlight Coffee",
        "tagline": "Slow evenings. Deep flavors.",
        "description": "A cozy late-night coffee bar for thoughtful sips and sweet treats.",
        "theme": "moonlight",
        "menu": [
            {"id": 1, "category": "Night Brews", "name": "Midnight Mocha", "price": 145, "description": "Dark chocolate, double espresso, and a cloud of milk foam."},
            {"id": 2, "category": "Night Brews", "name": "Brown Sugar Shaken Espresso", "price": 135, "description": "Bold espresso shaken over ice with smoky brown sugar."},
            {"id": 3, "category": "Night Brews", "name": "Black Sesame Latte", "price": 150, "description": "Nutty black sesame blended into a smooth, rich latte."},
            {"id": 4, "category": "Tea & Sips", "name": "Blue Pea Vanilla Tea", "price": 105, "description": "Butterfly pea flower tea with vanilla and citrus."},
            {"id": 5, "category": "After Dark", "name": "Tablea Lava Cake", "price": 125, "description": "Warm Filipino chocolate cake with a molten center."},
            {"id": 6, "category": "After Dark", "name": "Sea Salt Caramel Cookie", "price": 85, "description": "A chewy brown butter cookie with a salty caramel core."},
        ],
    },
}
