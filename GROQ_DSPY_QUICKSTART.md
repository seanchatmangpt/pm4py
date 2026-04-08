# Groq + DSPy + litellm Quick Start

This guide shows how to use Groq's fast inference with DSPy via litellm.

## Prerequisites

```bash
# Install dependencies
uv pip install dspy-ai litellm groq

# Set your Groq API key
export GROQ_API_KEY='gsk_...'
```

## Quick Start

```python
import dspy
import os

# Configure Groq via litellm
lm = dspy.LM(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    api_base="https://api.groq.com/openai/v1",
    temperature=0.0,
    custom_llm_provider="groq"
)

dspy.configure(lm=lm)

# Use DSPy as normal
class QuestionAnswer(dspy.Signature):
    """Answer questions."""
    question = dspy.InputField()
    answer = dspy.OutputField()

predictor = dspy.Predict(QuestionAnswer)
result = predictor(question="What is process mining?")
print(result.answer)
```

## Available Groq Models

| Model | litellm format | Best for |
|-------|---------------|----------|
| GPT-OSS 20B | `groq/openai/gpt-oss-20b` | Fast, efficient (recommended) |
| GPT-OSS 120B | `groq/openai/gpt-oss-120b` | High quality |
| GPT-OSS Safeguard 20B | `groq/openai/gpt-oss-safeguard-20b` | Safety-focused |

## litellm Configuration

### Method 1: Direct DSPy LM (Recommended)

```python
lm = dspy.LM(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    api_base="https://api.groq.com/openai/v1",
    custom_llm_provider="groq"
)
```

### Method 2: Environment Variables

```python
import os
os.environ["GROQ_API_KEY"] = "your-key"

# DSPy will pick up the env var
lm = dspy.LM(model="groq/openai/gpt-oss-20b")
```

### Method 3: Configuration File

Create `.env`:
```
GROQ_API_KEY=gsk_...
DSPY_CACHEDIR=./cache/dspy
```

Load with python-dotenv:
```python
from dotenv import load_dotenv
load_dotenv()

lm = dspy.LM(model="groq/openai/gpt-oss-20b")
```

## Examples

### Process Mining Assistant

```python
import dspy
import os

# Configure
lm = dspy.LM(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    custom_llm_provider="groq"
)
dspy.configure(lm=lm)

# Define module
class ProcessMiningQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.generate(question=question)

# Use
assistant = ProcessMiningQA()
answer = assistant("What is token-based replay?")
print(answer.answer)
```

### Few-Shot Learning

```python
class FewShotProcessQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        # Few-shot examples are handled by DSPy's KNN or teleprompter
        return self.generate(question=question)

# Configure with teleprompter for few-shot
teleprompter = dspy.BootstrapFewShot(
    max_bootstrapped_demos=3,
    max_labeled_demos=3
)

optimized = teleprompter.compile(
    FewShotProcessQA(),
    trainset=train_data  # Your training examples
)
```

## Performance Tips

1. **Use Caching**: Enable response caching to reduce API calls
   ```python
   os.environ["DSPY_CACHEDIR"] = "./cache"
   ```

2. **Batch Requests**: Process multiple questions at once
   ```python
   questions = ["Q1", "Q2", "Q3"]
   results = [assistant(q) for q in questions]
   ```

3. **Choose Right Model**:
   - Use `gpt-oss-20b` for most tasks (fast, best value)
   - Use `gpt-oss-120b` for higher quality requirements

## Troubleshooting

### "ModuleNotFoundError: No module named 'dspy'"
```bash
uv pip install dspy-ai
```

### "GROQ_API_KEY not set"
```bash
export GROQ_API_KEY='your-key-here'
```

### "litellm error"
Make sure litellm is installed:
```bash
uv pip install litellm
```

### Slow responses
- Try a smaller model like `gemma2-9b-it`
- Reduce `max_tokens` parameter
- Enable caching

## Full Example Script

See `groq_litellm_config.py` for a complete working example including:
- Multiple Groq models
- Caching configuration
- Process mining assistant
- Quick test function

Run it:
```bash
python groq_litellm_config.py
```

## References

- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [Groq Documentation](https://console.groq.com/docs)
- [litellm Documentation](https://docs.litellm.ai/)
