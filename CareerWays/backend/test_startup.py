"""Quick test script to debug app startup"""
from app import create_app
from app import db
from flask import Flask
import sys
import time

sys.path.insert(0, 'C:\\Users\\delac\\Pictures\\bitch\\CareerWays\\backend')

print("Step 1: Importing Flask...")

print("Step 2: Importing db...")

print("Step 3: Creating app...")

print("Step 4: Calling create_app()...")
start = time.time()
app = create_app()
elapsed = time.time() - start

print(f"Step 5: App created in {elapsed:.2f} seconds")
print("Success!")
