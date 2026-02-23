from flask import Flask, request, render_template_string, jsonify
from decimal import Decimal, InvalidOperation, getcontext

app = Flask(__name__)
getcontext().prec = 28  # higher precision for safer division

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>DevSecOps Calculator</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 520px; margin: 40px auto; padding: 0 16px; }
    .card { border: 1px solid #ddd; border-radius: 10px; padding: 18px; }
    label { display:block; margin-top: 10px; }
    input, select { width: 100%; padding: 10px; margin-top: 6px; }
    button { margin-top: 14px; width: 100%; padding: 10px; cursor: pointer; }
    .result { margin-top: 16px; padding: 12px; border-radius: 8px; background: #f6f6f6; }
    .error { margin-top: 16px; padding: 12px; border-radius: 8px; background: #ffecec; color: #b00020; }
  </style>
</head>
<body>
  <h2>Simple Calculator</h2>

  <div class="card">
    <form method="POST">
      <label>First number</label>
      <input type="number" step="any" name="num1" value="{{ num1 or '' }}" required>

      <label>Second number</label>
      <input type="number" step="any" name="num2" value="{{ num2 or '' }}" required>

      <label>Operation</label>
      <select name="operation">
        <option value="add" {{ 'selected' if operation=='add' else '' }}>Add</option>
        <option value="subtract" {{ 'selected' if operation=='subtract' else '' }}>Subtract</option>
        <option value="multiply" {{ 'selected' if operation=='multiply' else '' }}>Multiply</option>
        <option value="divide" {{ 'selected' if operation=='divide' else '' }}>Divide</option>
      </select>

      <button type="submit">Calculate</button>
    </form>

    {% if error %}
      <div class="error"><strong>Error:</strong> {{ error }}</div>
    {% endif %}

    {% if result is not none and not error %}
      <div class="result"><strong>Result:</strong> {{ result }}</div>
    {% endif %}
  </div>

  <p style="margin-top:14px; font-size: 12px; color: #666;">
    Tip: You can also use the API endpoint: <code>/api/calc?num1=10&num2=5&op=divide</code>
  </p>
</body>
</html>
"""

OPS = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b,
}

def parse_decimal(value: str):
    """Parse user input safely into Decimal."""
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None

def format_decimal(d: Decimal):
    """Pretty formatting: strip trailing zeros, limit long decimals."""
    # normalize can create scientific notation; quantize lightly for display instead
    s = f"{d:.10f}".rstrip("0").rstrip(".")
    return s if s else "0"

def calculate(a: Decimal, b: Decimal, op: str):
    if op not in OPS:
        return None, "Invalid operation"
    if op == "divide" and b == 0:
        return None, "Cannot divide by zero"
    try:
        return OPS[op](a, b), None
    except Exception:
        return None, "Calculation failed"

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None
    error = None
    num1 = None
    num2 = None
    operation = "add"

    if request.method == "POST":
        num1 = request.form.get("num1", "").strip()
        num2 = request.form.get("num2", "").strip()
        operation = request.form.get("operation", "add")

        a = parse_decimal(num1)
        b = parse_decimal(num2)

        if a is None or b is None:
            error = "Please enter valid numbers."
        else:
            res, error = calculate(a, b, operation)
            if error is None:
                result = format_decimal(res)

    return render_template_string(
        HTML,
        result=result,
        error=error,
        num1=num1,
        num2=num2,
        operation=operation
    )

@app.route("/api/calc", methods=["GET"])
def calculator_api():
    # Example: /api/calc?num1=10&num2=5&op=divide
    num1 = request.args.get("num1", "")
    num2 = request.args.get("num2", "")
    op = request.args.get("op", "add")

    a = parse_decimal(num1)
    b = parse_decimal(num2)

    if a is None or b is None:
        return jsonify({"ok": False, "error": "Invalid numbers"}), 400

    res, error = calculate(a, b, op)
    if error:
        return jsonify({"ok": False, "error": error}), 400

    return jsonify({"ok": True, "result": format_decimal(res), "operation": op})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)