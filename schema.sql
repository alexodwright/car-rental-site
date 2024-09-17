DROP TABLE IF EXISTS users;

CREATE TABLE users 
(   
    user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    pfp TEXT NOT NULL DEFAULT "defaultpfp.png"
);
INSERT INTO users (user_id, fname, lname, email, password, is_admin)
VALUES (0, "Admin", "", "admin@admin.mail.ie", "scrypt:32768:8:1$S4LVLjxxT2BSCZxO$372884f95f3e856f6cbd0c319a88d782ad27c2d8f4e1dc9f78caefb74d80a98752ab1df0569d2f4fcc4b70699d3adc25247b563ec09d51edd7b028d82733fd64", 1);

DROP TABLE IF EXISTS cars;

CREATE TABLE cars
(
    car_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    price DECIMAL NOT NULL,
    description TEXT NOT NULL,
    image TEXT DEFAULT "default.jpg"
);

INSERT INTO cars (brand, model, price, description, image)
VALUES ("Porsche", "911 Carrera", 90, "The Porsche 911 Carrera is a classic sports car known for its iconic design and exhilarating performance.", "carerra.jpg"),
("Porsche", "Panamera", 100, "The Porsche Panamera is a luxury sedan offering both comfort and sportiness with its sleek design and powerful engine options.", "panamera.jpg"),
("Porsche", "Cayenne", 120, "The Porsche Cayenne is a high-performance SUV blending luxury and capability, perfect for both daily driving and off-road adventures.", "cayenne.jpg"),
("Porsche", "Macan", 150, "The Porsche Macan is a compact SUV that combines agility with practicality, making it an ideal choice for urban environments and weekend getaways.", "macan.jpg"),
("Porsche", "Taycan", 110, "The Porsche Taycan is an all-electric sports car that delivers thrilling performance and cutting-edge technology, redefining the future of driving.", "taycan.jpg"),
("Porsche", "911 GT3", 190, "The Porsche 911 GT3 is a track-focused sports car designed for enthusiasts seeking the ultimate driving experience, featuring a naturally aspirated engine and race-inspired technology.", "gt3rs.jpg"),
("Toyota", "Camry", 80, "Mid-size sedan with excellent fuel efficiency.", "camry.jpg"),
("Honda", "Civic", 70, "Compact car known for reliability and efficiency.", "civic.jpg"),
("Ford", "Mustang", 140, "Iconic American muscle car with powerful performance.", "mustang.jpg"),
("Chevrolet", "Corvette", 140, "Legendary sports car with sleek design and high-speed performance.", "corvette.jpg"),
("BMW", "3 Series", 130, "Luxury compact sedan with advanced technology features.", "3_series.jpg"),
("Mercedes-Benz", "E-Class", 160, "Executive luxury sedan renowned for comfort and safety.", "e_class.jpg"),
("Audi", "A4", 100, "Premium compact sedan with sophisticated styling and advanced features.", "a4.jpg"),
("Tesla", "Model S", 60, "Electric luxury sedan with groundbreaking performance and technology.", "model_s.jpg"),
("Subaru", "Outback", 50, "Versatile crossover SUV with off-road capabilities.", "outback.jpg"),
("Jeep", "Wrangler", 80, "Iconic off-road SUV designed for rugged terrain.", "wrangler.jpg")

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    days INTEGER NOT NULL
);

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews (
    review_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    content TEXT NOT NULL
)

DROP TABLE IF EXISTS favourites;

CREATE TABLE favourites (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL
)