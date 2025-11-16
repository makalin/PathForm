# PathForm Quick Start Guide

Get started with PathForm in 5 minutes!

## Installation

### Python
```bash
pip install -e .
```

### Node.js
```bash
npm install
```

### Go
```bash
go get github.com/makalin/pathform
```

## Basic Usage

### 1. Parse PathForm Text

**Python:**
```python
from pathform import parse_pathform

text = """
user.name = "Mehmet"
user.age = 49
items[0] = "first"
items[1] = "second"
"""

data = parse_pathform(text)
print(data)
# {'user': {'name': 'Mehmet', 'age': 49}, 'items': ['first', 'second']}
```

**JavaScript:**
```javascript
const { parsePathform } = require('./pathform.js');

const text = `
user.name = "Mehmet"
user.age = 49
items[0] = "first"
items[1] = "second"
`;

const data = parsePathform(text);
console.log(data);
```

### 2. Convert to JSON

**Python:**
```python
from pathform import to_json

json_str = to_json(text)
print(json_str)
```

**JavaScript:**
```javascript
const { toJSON } = require('./pathform.js');
const jsonStr = toJSON(text);
console.log(jsonStr);
```

### 3. Convert from JSON

**Python:**
```python
from pathform import from_json

json_obj = {"user": {"name": "Mehmet", "age": 49}}
pathform = from_json(json_obj)
print(pathform)
```

**JavaScript:**
```javascript
const { fromJSON } = require('./pathform.js');
const jsonObj = {user: {name: "Mehmet", age: 49}};
const pathform = fromJSON(jsonObj);
console.log(pathform);
```

## CLI Usage

### Convert PathForm to JSON
```bash
pathform2json input.pf > output.json
```

### Convert JSON to PathForm
```bash
json2pathform input.json > output.pf
```

### Validate PathForm
```bash
pathform_validator.py file.pf
```

### Format PathForm
```bash
pathform_formatter.py -i file.pf
```

## Examples

Check out the `examples/` directory:
- `simple.pf` - Basic example
- `nested.pf` - Nested structures
- `green_wave.pf` - Real-world example
- `integration_python.py` - Python integration
- `integration_node.js` - Node.js integration

## Next Steps

1. Read the full [README.md](README.md) for complete documentation
2. Check out [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
3. Run tests: `make test`
4. Explore the examples in `examples/`

Happy coding! 🚀

