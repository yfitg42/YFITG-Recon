# Contributing to YFITG Network Scout

## Development Setup

### Device Development

1. Clone repository
2. Set up virtual environment:
```bash
cd device
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy and configure:
```bash
cp config.example.json .config.json
# Edit .config.json
```

4. Run in development mode:
```bash
python main.py
```

### Portal Development

1. Navigate to portal directory:
```bash
cd portal
npm install
```

2. Copy environment file:
```bash
cp .env.example .env.local
# Edit .env.local
```

3. Run development server:
```bash
npm run dev
```

### API Development

1. Navigate to server directory:
```bash
cd server
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export API_TOKEN="dev-token"
export STORAGE_DIR="./reports"
```

3. Run development server:
```bash
uvicorn main:app --reload
```

## Code Style

- Python: Follow PEP 8
- TypeScript/JavaScript: Follow ESLint rules
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

## Testing

- Test device software on actual Raspberry Pi hardware
- Test portal in development mode
- Test API with curl or Postman
- Verify MQTT message flow

## Pull Requests

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Update documentation
5. Submit PR with description

## Security

- Never commit secrets or credentials
- Use environment variables
- Validate all inputs
- Follow security best practices

