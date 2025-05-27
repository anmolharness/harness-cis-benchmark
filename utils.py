from datetime import datetime

def generate_html(results, account_id, output_file="report.html"):
    passed = sum(r["level"] for r in results if r["result"] == "PASS")
    total = sum(r["level"] for r in results)
    score_pct = (passed / total) * 100 if total else 0
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Harness CIS Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .pass {{ background-color: #e0ffe0; }}
        .fail {{ background-color: #ffe0e0; }}
    </style>
</head>
<body>
    <h1>Harness CIS Benchmark Report</h1>
    <p><strong>Account ID:</strong> {account_id}<br>
    <strong>Score:</strong> {passed} / {total} ({score_pct:.1f}%)<br>
    <strong>Generated:</strong> {timestamp}</p>

    <table>
        <tr>
            <th>ID</th>
            <th>Description</th>
            <th>Level</th>
            <th>Result</th>
            <th>Details</th>
        </tr>"""

    for rule in results:
        result_class = "pass" if rule["result"] == "PASS" else "fail"
        html += f"""
        <tr class="{result_class}">
            <td>{rule['id']}</td>
            <td>{rule['description']}</td>
            <td>{rule['level']}</td>
            <td>{rule['result']}</td>
            <td>{rule['details']}</td>
        </tr>"""

    html += """
    </table>
</body>
</html>
"""
    with open(output_file, "w") as f:
        f.write(html)
    print(f"[✓] HTML report exported to {output_file}")
