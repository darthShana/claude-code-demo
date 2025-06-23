#!/usr/bin/env python3
"""
Entry point to run the GAP Quote Service API
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "claude_code_demo.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )