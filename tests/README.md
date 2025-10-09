# Tests

This directory contains test files for the Classroom Interaction Platform.

## Test Files

- `test_app.py` - Basic application functionality tests
- `test_ark_api.py` - AI API integration tests

## Running Tests

### Test Application
```bash
python tests/test_app.py
```

### Test AI API Integration
```bash
python tests/test_ark_api.py
```

## Test Requirements

Make sure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```

For AI API tests, configure your API keys in the `.env` file:
```env
ARK_API_KEY=your-bytedance-ark-api-key
OPENAI_API_KEY=your-openai-api-key
```
