import json

def update_dashboard_for_servername(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Add server_name variable to templating
    new_variable = {
        "allValue": None,
        "current": {
            "selected": True,
            "text": "All",
            "value": "$__all"
        },
        "datasource": {
            "type": "prometheus",
            "uid": "${ds_prometheus}"
        },
        "definition": "label_values(node_uname_info, server_name)",
        "hide": 0,
        "includeAll": True,
        "label": "서버 선택",
        "multi": True,
        "name": "server_name",
        "options": [],
        "query": {
            "query": "label_values(node_uname_info, server_name)",
            "refId": "Prometheus-servername-Variable-Query"
        },
        "refresh": 1,
        "regex": "",
        "skipUrlSync": False,
        "sort": 1,
        "type": "query"
    }

    # Insert at the beginning of the list or before 'job'
    variables = data.get("templating", {}).get("list", [])
    # Check if already exists
    if not any(v.get("name") == "server_name" for v in variables):
        variables.insert(0, new_variable)
    
    # 2. Update other variables to depend on $server_name
    for var in variables:
        if var.get("name") in ["job", "node", "nodename"]:
            if isinstance(var.get("query"), str):
                if "{" in var["query"]:
                    var["query"] = var["query"].replace("{", '{server_name=~"$server_name", ', 1)
                else:
                    var["query"] = var["query"].replace("(", '(node_uname_info{server_name=~"$server_name"}, ', 1)
            elif isinstance(var.get("query"), dict) and "query" in var["query"]:
                q_str = var["query"]["query"]
                if "{" in q_str:
                    var["query"]["query"] = q_str.replace("{", '{server_name=~"$server_name", ', 1)
                else:
                    # e.g. label_values(job) -> label_values(node_uname_info{server_name=~"$server_name"}, job)
                    var["query"]["query"] = q_str.replace("(", '(node_uname_info{server_name=~"$server_name"}, ', 1)
            
            if var.get("definition"):
                if "{" in var["definition"]:
                    var["definition"] = var["definition"].replace("{", '{server_name=~"$server_name", ', 1)
                else:
                    var["definition"] = var["definition"].replace("(", '(node_uname_info{server_name=~"$server_name"}, ', 1)

    # 3. Recursively update all panel expressions
    def update_expr(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "expr" and isinstance(v, str):
                    # Replace instance filter with server_name filter
                    # Most common pattern: instance="$node" or instance=~"$node"
                    new_v = v.replace('instance="$node"', 'server_name=~"$server_name"')
                    new_v = new_v.replace('instance=~"$node"', 'server_name=~"$server_name"')
                    # Also handle cases where only instance is specified without $node (rare in this dashboard)
                    obj[k] = new_v
                else:
                    update_expr(v)
        elif isinstance(obj, list):
            for item in obj:
                update_expr(item)

    update_expr(data.get("panels", []))

    # 4. Save the updated JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_dashboard_for_servername(
        "./dash_board_ko.json",
        "./dash_board_ko.json"
    )
    print("Dashboard updated successfully with $server_name variable.")
