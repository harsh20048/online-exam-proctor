from pymongo import MongoClient
import sys

try:
    print("Attempting to connect to MongoDB...")
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    server_info = client.server_info()
    print("MongoDB connection successful!")
    print(f"Server info: {server_info}")
    
    # Test database and collection
    db = client["examproctordb"]
    students_collection = db["students"]
    
    # Check if admin user exists, if not create it
    if students_collection.count_documents({"Email": "admin@example.com"}) == 0:
        print("Creating admin user...")
        students_collection.insert_one({
            "Id": 1,
            "Name": "Admin User",
            "Email": "admin@example.com",
            "Password": "admin123",
            "Role": "ADMIN"
        })
        print("Admin user created.")
    else:
        print("Admin user already exists.")
    
    # Check if sample student exists, if not create it
    if students_collection.count_documents({"Email": "student1@example.com"}) == 0:
        print("Creating sample student...")
        students_collection.insert_one({
            "Id": 2,
            "Name": "Student One",
            "Email": "student1@example.com",
            "Password": "student123",
            "Role": "STUDENT"
        })
        print("Sample student created.")
    else:
        print("Sample student already exists.")
        
    print("MongoDB setup completed successfully!")
    
except Exception as e:
    print(f"MongoDB connection error: {e}")
    sys.exit(1) 