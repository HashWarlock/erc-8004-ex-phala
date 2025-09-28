# CRITICAL RULES - NEVER FORGET

## Date: 2025-08-23

### ALWAYS USE FLOX - NO EXCEPTIONS

**RULE**: ALWAYS use `flox activate --` before ANY Python, Node, or development commands.

**NEVER** run:
- `python` directly
- `docker run` with plain python
- `npm` directly  
- `pip` directly
- Any development tool without Flox

**ALWAYS** run:
- `flox activate -- python`
- `flox activate -- npm`
- `flox activate -- pip`
- `flox activate -- pytest`
- For Docker: Use the Flox-built container image

### Why This Matters
1. Flox manages ALL dependencies
2. Python is NOT installed globally on the client
3. All tools and packages are contained within Flox environment
4. Breaking this rule causes commands to fail

### Examples

❌ WRONG:
```bash
python test.py
docker run image python script.py
npm install
```

✅ CORRECT:
```bash
flox activate -- python test.py
docker run image flox activate -- python script.py
flox activate -- npm install
```

### Container Testing
When testing containers, the container was built WITH Flox, so it includes the Flox environment. Test using:
```bash
docker run --rm -it erc-8004-ex-phala:erc8004-phala /bin/bash -c "command"
```

The container image already has Flox environment baked in from `flox containerize`.