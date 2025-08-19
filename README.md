# Literate - Narrative Text Analyzer

A Python command-line tool that extracts narrative structure from free text in real-time using AI. Features a colorful TUI with live analysis and supports both local (Ollama) and cloud (OpenAI) LLM providers.

## ✨ Features

- **Real-time Analysis**: 2-second debounce timer for responsive text processing
- **Dual LLM Support**: Works with local Ollama or OpenAI API
- **Smart Object Tracking**: Preserves narrative continuity across text additions
- **Interactive TUI**: Three-panel interface with live updates
- **Rich Formatting**: Colorful display with relationship mapping

## 🚀 Quick Start

### Prerequisites

**For Ollama (Default):**
- [Ollama](https://ollama.ai) installed and running
- `gemma3:1b` model downloaded: `ollama pull gemma3:1b`

**For OpenAI (Optional):**
- OpenAI API key

### Installation

```bash
# Clone repository
git clone <repository-url>
cd literate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setup for OpenAI (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

## 🎯 Usage

### Basic Usage

```bash
# Use local Ollama (default)
python main.py

# Use OpenAI API
python main.py --openai

# Get help
python main.py --help
```

### Interface

The application displays a three-panel TUI:

- **Left Panel**: Text input area
- **Right Top Panel**: Extracted narrative objects with relationships
- **Right Bottom Panel**: Status messages and errors

### Controls

- **Type/Paste**: Enter text in the left panel
- **Ctrl+1, Ctrl+2, etc.**: Retry specific narrative objects
- **Ctrl+C or Ctrl+Q**: Exit application

## 📖 How It Works

1. **Input**: Type or paste text into the left panel
2. **Processing**: After 2 seconds of inactivity, text is sent to the LLM
3. **Extraction**: AI identifies people, places, events, and relationships
4. **Display**: Objects appear in the right panel with descriptions
5. **Continuity**: New text adds to existing objects without losing history

### Example

**Input:**
```
Alice met Bob at the coffee shop. They discussed their upcoming trip to Paris.
Later, Charlie joined them and they talked about visiting the Louvre Museum.
```

**Output:**
```
📚 Narrative Objects (4)
🔗 2 relationships found

1. Alice
│ A person who met Bob at the coffee shop
│ Relationships:
├─ Bob: Met at the coffee shop
└─ Updated: 14:23:15

2. Bob  
│ A person who met Alice and discussed a trip to Paris
│ Relationships:
├─ Alice: Met at the coffee shop
└─ Updated: 14:23:15

3. Paris
│ A destination for an upcoming trip
└─ Updated: 14:23:15

4. Charlie
│ A person who joined Alice and Bob later
└─ Updated: 14:23:28
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for OpenAI configuration:

```bash
# Required for OpenAI
OPENAI_API_KEY=your_api_key_here

# Optional settings
OPENAI_MODEL=gpt-3.5-turbo  # Default model
OPENAI_TEMPERATURE=0.1      # Response consistency (0.0-1.0)
```

### LLM Providers

| Provider | Command | Requirements |
|----------|---------|--------------|
| Ollama (default) | `python main.py` | Ollama installed, `gemma3:1b` model |
| OpenAI | `python main.py --openai` | API key in `.env` file |

## 🧪 Testing

The project includes comprehensive test scripts:

```bash
# Test LLM connectivity
python test_llm.py

# Test provider integrations  
python test_providers.py

# Test object preservation
python test_incremental_objects.py

# Test full pipeline
python test_full_pipeline.py

# Test UI components
python test_tui.py
```

## 🏗️ Architecture

- **Language**: Python 3.7+
- **TUI Framework**: Textual 5.3.0
- **Local LLM**: Ollama with gemma3:1b
- **Cloud LLM**: OpenAI gpt-3.5-turbo
- **Data Models**: Rich object relationships with timestamps

### Key Components

- `main.py` - Entry point and argument parsing
- `tui_app.py` - Textual-based user interface
- `llm_client.py` - Dual provider LLM interface
- `object_manager.py` - State management and object merging
- `models.py` - Data models for objects and relationships

## 🐛 Troubleshooting

### Common Issues

**"Failed to connect to Ollama server"**
```bash
# Check if Ollama is running
ollama list

# Start Ollama if needed
ollama serve

# Download model if missing
ollama pull gemma3:1b
```

**"OPENAI_API_KEY not found"**
```bash
# Check .env file exists
ls -la .env

# Verify API key format
cat .env
```

**Mouse control characters on exit**
- Use Ctrl+Q instead of Ctrl+C if experiencing terminal issues

## 📝 Development

See `CLAUDE.md` for detailed development guidelines and `PLAN.md` for implementation details.

```bash
# Run with development mode
source venv/bin/activate
python main.py

# Run tests
python test_providers.py
```

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]
