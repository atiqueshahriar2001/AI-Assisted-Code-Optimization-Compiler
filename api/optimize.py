import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from optimizer.engine import optimize_code


def handler(request):
    try:
        body = request.get('body', '{}')
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        payload = json.loads(body) if body else {}
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")

        source = payload.get("source", "")
        if not isinstance(source, str):
            raise ValueError("The 'source' field must be a string.")

        enabled_passes = payload.get("enabled_passes")
        if enabled_passes is not None and not isinstance(enabled_passes, list):
            raise ValueError("The 'enabled_passes' field must be a list when provided.")

        result = optimize_code(source, enabled_passes=enabled_passes)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result, indent=2)
        }
    except Exception as exc:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(exc)})
        }