import os
import pandas as pd
import json
import toons

def parse_kpi_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="PDCA")
    df = df.fillna("")
    
    metadata = {}
    data_points = []
    
    in_data_table = False
    headers = []
    
    for _, row in df.iterrows():
        row_list = list(row.values)
        row_str = [str(x).strip() for x in row_list]
        
        if "الربع/الفترة" in row_str:
            in_data_table = True
            h_list = []
            # Handle merged cells for benchmarking
            for i, h in enumerate(row_str):
                if h == "المقارنة المعيارية (إن وجدت)":
                    h_list.append("المقارنة المعيارية - القيمة")
                    
                    # Assume next two empty cols belong to benchmarking
                    if i+1 < len(row_str) and row_str[i+1] == "":
                        row_str[i+1] = "المقارنة المعيارية - السنة"
                    if i+2 < len(row_str) and row_str[i+2] == "":
                        row_str[i+2] = "المقارنة المعيارية - الدولة/ المنطقة"
                else:
                    h_list.append(h)
            headers = h_list
            continue
            
        if in_data_table:
            first_val = row_str[0]
            if first_val in ["Q1", "Q2", "Q3", "Q4", "H1", "H2", "Y1"] or str(row_str[1]) in ["2023", "2024"]:
                point = {}
                for i, h in enumerate(headers):
                    if h:  
                        point[h] = row_str[i] if i < len(row_str) else ""
                data_points.append(point)
            continue
            
        # For now, we'll try parsing as-is
        for i in range(0, len(row_str) - 1, 2):
            key = row_str[i]
            val = row_str[i+1]
            if key and val and key not in ["اسم الحقل", "نوع الحقل", "الغرض"]:
                metadata[key] = val

    result = {
        "metadata": metadata,
        "data_points": data_points
    }
    
    try:
        if hasattr(file_path, "name"):
            original_filename = file_path.name
        else:
            original_filename = os.path.basename(str(file_path))
            
        base_name = os.path.splitext(original_filename)[0]
        json_filename = f"{base_name}.toon"
        
        # Get path to temp directory
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        output_path = os.path.join(temp_dir, json_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(toons.dumps(result))
    except Exception as e:
        print(f"Could not save TOON output: {e}")

    return result
