#!/usr/bin/env python3
"""
Test script for parcelle CRUD operations
"""
import httpx
import json
import asyncio

BASE_URL = "http://localhost:8000"

async def test_parcelle_crud():
    """Test CRUD operations for parcelles"""
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get forests to use in tests
        print("🔍 Fetching forests...")
        resp = await client.get(f"{BASE_URL}/forests/")
        if resp.status_code != 200:
            print(f"❌ Failed to fetch forests: {resp.status_code}")
            return
        
        forests = resp.json()
        if not forests:
            print("❌ No forests found. Create a forest first!")
            return
        
        forest_id = forests[0]['id']
        print(f"✅ Using forest: {forests[0]['name']} (ID: {forest_id})")
        
        # Step 2: Create a test parcelle
        print("\n📝 Creating test parcelle...")
        parcelle_data = {
            "forest_id": forest_id,
            "name": "Test Parcelle CRUD",
            "description": "Test for CRUD operations",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[48.8, 2.3], [48.81, 2.3], [48.81, 2.31], [48.8, 2.31], [48.8, 2.3]]]
            }
        }
        
        resp = await client.post(
            f"{BASE_URL}/parcelles/",
            json=parcelle_data
        )
        
        if resp.status_code != 201:
            print(f"❌ Failed to create parcelle: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return
        
        parcelle = resp.json()
        parcelle_id = parcelle['id']
        print(f"✅ Created parcelle: {parcelle['name']} (ID: {parcelle_id})")
        
        # Step 3: Read parcelle
        print("\n📖 Reading parcelle...")
        resp = await client.get(f"{BASE_URL}/parcelles/{parcelle_id}")
        
        if resp.status_code != 200:
            print(f"❌ Failed to read parcelle: {resp.status_code}")
            return
        
        parcelle = resp.json()
        print(f"✅ Read parcelle: {parcelle['name']}")
        print(f"   Description: {parcelle.get('description', 'No description')}")
        
        # Step 4: Update parcelle
        print("\n✏️  Updating parcelle...")
        update_data = {
            "name": "Updated Test Parcelle",
            "description": "Updated description via CRUD test"
        }
        
        resp = await client.put(
            f"{BASE_URL}/parcelles/{parcelle_id}",
            json=update_data
        )
        
        if resp.status_code != 200:
            print(f"❌ Failed to update parcelle: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return
        
        parcelle = resp.json()
        print(f"✅ Updated parcelle: {parcelle['name']}")
        print(f"   New description: {parcelle.get('description', 'No description')}")
        
        # Step 5: List parcelles
        print("\n📋 Listing all parcelles for forest...")
        resp = await client.get(f"{BASE_URL}/parcelles/by_forest/{forest_id}")
        
        if resp.status_code != 200:
            print(f"❌ Failed to list parcelles: {resp.status_code}")
            return
        
        parcelles = resp.json()
        print(f"✅ Found {len(parcelles)} parcelle(s) in forest:")
        for p in parcelles:
            print(f"   - {p['name']} (ID: {p['id']})")
        
        # Step 6: Delete parcelle
        print("\n🗑️  Deleting parcelle...")
        resp = await client.delete(f"{BASE_URL}/parcelles/{parcelle_id}")
        
        if resp.status_code != 204:
            print(f"❌ Failed to delete parcelle: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return
        
        print(f"✅ Deleted parcelle ID: {parcelle_id}")
        
        # Step 7: Verify deletion
        print("\n🔍 Verifying deletion...")
        resp = await client.get(f"{BASE_URL}/parcelles/{parcelle_id}")
        
        if resp.status_code == 404:
            print(f"✅ Parcelle successfully deleted (404 confirmed)")
        else:
            print(f"⚠️  Unexpected status after deletion: {resp.status_code}")
        
        print("\n✅ All CRUD tests passed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_parcelle_crud())
    except Exception as e:
        print(f"❌ Test failed: {e}")
