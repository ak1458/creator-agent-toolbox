#!/usr/bin/env python3
"""
Pre-beta verification script.
Run: python scripts/verify_local.py
"""

import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"

async def verify():
    print("🔍 Verifying local setup...")
    
    # 1. Health check
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/api/v1/health")
            if resp.status_code != 200:
                print("❌ Backend not running (expected 200)")
                sys.exit(1)
            print("✅ Backend healthy")
        except Exception as e:
            print(f"❌ Backend not reachable: {e}")
            sys.exit(1)
            
        # 2. Create workflow
        resp = await client.post(
            f"{BASE_URL}/api/v1/workflows/start",
            json={"topic": "Verification Test", "platforms": ["youtube"]}
        )
        if resp.status_code != 200:
            print("❌ Cannot create workflow")
            print(resp.json())
            sys.exit(1)
        wf_id = resp.json()["workflow_id"]
        print(f"✅ Workflow created: {wf_id}")
        
        # 3. Check has scripts
        # Poll briefly since LangGraph executes async
        print("⏳ Waiting for scripts to generate...")
        await asyncio.sleep(5)
        
        resp = await client.get(f"{BASE_URL}/api/v1/workflows/{wf_id}")
        data = resp.json()
        if not data.get("scripts"):
            print("❌ No scripts generated")
            print(f"Current state: {data.get('status')} / {data.get('current_step')}")
            sys.exit(1)
        print(f"✅ Scripts generated: {len(data['scripts'])} variants")
        
        print("\n🎉 All verifications passed! Ready for beta.")
        
if __name__ == "__main__":
    asyncio.run(verify())
