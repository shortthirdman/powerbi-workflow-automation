from pbi_auth import PowerBIClient
from datetime import datetime
import numpy as np


def validate_data_quality(client, workspace_id, dataset_id, rules):
    """Run DAX validation queries against a dataset"""
    results = []

    for rule in rules:
        # Execute DAX query
        response = client.post(
            f"groups/{workspace_id}/datasets/{dataset_id}/executeQueries",
            data={
                "queries": [{"query": rule["dax_query"]}],
                "serializerSettings": {"includeNulls": True}
            }
        )

        if response.status_code == 200:
            data = response.json()
            rows = data["results"][0]["tables"][0]["rows"]
            actual_value = list(rows[0].values())[0] if rows else None

            # Check against expected
            passed = True
            message = "OK"

            if rule["check_type"] == "min_threshold":
                if actual_value < rule["threshold"]:
                    passed = False
                    message = f"Below minimum: {actual_value} < {rule['threshold']}"

            elif rule["check_type"] == "max_threshold":
                if actual_value > rule["threshold"]:
                    passed = False
                    message = f"Above maximum: {actual_value} > {rule['threshold']}"

            elif rule["check_type"] == "range":
                if not (rule["min"] <= actual_value <= rule["max"]):
                    passed = False
                    message = f"Out of range: {actual_value} not in [{rule['min']}, {rule['max']}]"

            elif rule["check_type"] == "not_null_pct":
                if actual_value > rule["threshold"]:
                    passed = False
                    message = f"Null rate too high: {actual_value}% > {rule['threshold']}%"

            results.append({
                "rule_name": rule["name"],
                "actual_value": actual_value,
                "passed": passed,
                "message": message
            })

    return results


# Example usage — Ravi's manufacturing rules
manufacturing_rules = [
    {
        "name": "Daily Revenue > ₹0",
        "dax_query": "EVALUATE ROW(\"Rev\", [Total Revenue])",
        "check_type": "min_threshold",
        "threshold": 0
    },
    {
        "name": "All 12 Plants Reporting",
        "dax_query": "EVALUATE ROW(\"Plants\", DISTINCTCOUNT(Plants[PlantID]))",
        "check_type": "min_threshold",
        "threshold": 12
    },
    {
        "name": "Null Rate in Revenue < 1%",
        "dax_query": """
            EVALUATE ROW("NullPct", 
                DIVIDE(
                    COUNTBLANK(Sales[Revenue]),
                    COUNTROWS(Sales)
                ) * 100
            )
        """,
        "check_type": "not_null_pct",
        "threshold": 1.0
    },
    {
        "name": "Margin Between 15-45%",
        "dax_query": "EVALUATE ROW(\"Margin\", [Gross Margin %])",
        "check_type": "range",
        "min": 15.0,
        "max": 45.0
    }
]