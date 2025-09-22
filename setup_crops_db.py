import sqlite3

def setup_crops():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Drop the old table to recreate it with the full list
    c.execute("DROP TABLE IF EXISTS crops")

    # Create the new crops table with location and image_filename
    c.execute('''
    CREATE TABLE crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        season TEXT NOT NULL,
        location TEXT NOT NULL,
        equipment TEXT NOT NULL,
        description TEXT,
        image_filename TEXT
    )
    ''')

    # Add 10 major crops with details
    sample_crops = [
        ('Wheat (Gehu)', 'Rabi (Winter)', 'Haryana, Punjab, Uttar Pradesh', 'Rotavator, Cultivator, Seed Drill, Thresher', 'A primary winter cereal crop, forming a staple food.', 'wheat.jpg'),
        ('Rice (Dhan)', 'Kharif (Monsoon)', 'Haryana, Punjab, West Bengal', 'Puddler, Transplanter, Combine Harvester', 'A major monsoon crop requiring significant water.', 'rice.jpg'),
        ('Sugarcane (Ganna)', 'Annual', 'Haryana, Uttar Pradesh', 'Cutter Planter, Ridger, Harvester', 'A long-duration cash crop used for sugar and jaggery.', 'sugarcane.jpg'),
        ('Cotton (Kapas)', 'Kharif (Monsoon)', 'Haryana, Punjab, Gujarat', 'Seed Planter, Sprayer, Cotton Picker', 'A key fiber crop used for textiles.', 'cotton.jpg'),
        ('Mustard (Sarson)', 'Rabi (Winter)', 'Haryana, Rajasthan, Uttar Pradesh', 'Seed Drill, Sprayer, Harvester', 'An important oilseed crop grown in the winter season.', 'mustard.jpg'),
        ('Bajra (Pearl Millet)', 'Kharif (Monsoon)', 'Rajasthan, Haryana, Gujarat', 'Cultivator, Seed Drill, Thresher', 'A drought-resistant coarse grain, suitable for dry regions.', 'bajra.jpg'),
        ('Maize (Makka)', 'Kharif (Monsoon)', 'Karnataka, Bihar, Uttar Pradesh', 'Maize Planter, Sprayer, Harvester', 'A versatile crop used for food, animal feed, and ethanol.', 'maize.jpg'),
        ('Gram (Chana)', 'Rabi (Winter)', 'Madhya Pradesh, Rajasthan', 'Seed Drill, Cultivator, Harvester', 'The most important pulse crop in India, grown in winter.', 'gram.jpg'),
        ('Jute', 'Kharif (Monsoon)', 'Bihar, West Bengal, Assam', 'Seed Drill, Weeder, Jute Rettling Plant', 'Known as the "Golden Fibre," used for making bags and ropes.', 'jute.jpg'),
        ('Barley (Jau)', 'Rabi (Winter)', 'Rajasthan, Uttar Pradesh, Haryana', 'Cultivator, Seed Drill, Thresher', 'A cereal grain used for fodder, malt production, and food.', 'barley.jpg')
    ]

    c.executemany('INSERT INTO crops (crop_name, season, location, equipment, description, image_filename) VALUES (?, ?, ?, ?, ?, ?)', sample_crops)

    conn.commit()
    conn.close()
    print("Crops table has been recreated with 10 sample crops.")

if __name__ == "__main__":
    setup_crops()