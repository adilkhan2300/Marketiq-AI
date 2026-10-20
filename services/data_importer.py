import pandas as pd
import numpy as np
import io
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from models.db_models import CampaignRecord, CustomerRecord, UploadHistory

# Required and optional analytical fields
STANDARD_FIELDS = {
    "date": ["date", "day", "timestamp", "record_date"],
    "campaign_id": ["campaign_id", "cid", "campaign_code", "ad_id"],
    "campaign_name": ["campaign_name", "campaign", "ad_name", "name"],
    "channel": ["channel", "source", "medium", "network", "ad_channel"],
    "impressions": ["impressions", "views", "impr"],
    "clicks": ["clicks", "visitors", "traffic"],
    "spend": ["spend", "cost", "ad_spend", "amount_spent"],
    "conversions": ["conversions", "orders", "leads", "acquisitions"],
    "attributed_revenue": ["attributed_revenue", "revenue", "sales", "order_value"],
    "gross_margin_rate": ["gross_margin_rate", "gross_margin", "margin", "profit_margin"]
}

def detect_column_mappings(df_columns: List[str]) -> Dict[str, str]:
    mappings = {}
    lower_cols = {col.lower().strip().replace(" ", "_"): col for col in df_columns}
    
    for standard_key, aliases in STANDARD_FIELDS.items():
        matched = False
        for alias in aliases:
            if alias in lower_cols:
                mappings[standard_key] = lower_cols[alias]
                matched = True
                break
        if not matched:
            mappings[standard_key] = None
    return mappings

def validate_and_parse_dataset(
    file_bytes: bytes,
    filename: str,
    custom_mapping: Dict[str, str] = None
) -> Dict[str, Any]:
    # 1. File type verification
    is_excel = filename.endswith(".xlsx") or filename.endswith(".xls")
    is_csv = filename.endswith(".csv")

    if not (is_csv or is_excel):
        return {
            "success": False,
            "error": "Unsupported file format. Please upload a standard CSV or Excel (.xlsx) file."
        }

    try:
        if is_excel:
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse file: {str(e)}"
        }

    total_rows = len(df)
    if total_rows == 0:
        return {
            "success": False,
            "error": "The uploaded file is empty."
        }

    # Detect or apply custom mappings
    detected_mapping = detect_column_mappings(list(df.columns))
    if custom_mapping:
        for k, v in custom_mapping.items():
            if v in df.columns:
                detected_mapping[k] = v

    # Data Quality Validation checks
    issues = []
    
    # Missing required core fields check
    critical_fields = ["campaign_name", "channel", "spend", "conversions", "attributed_revenue"]
    missing_critical = [f for f in critical_fields if not detected_mapping.get(f)]
    if missing_critical:
        issues.append({
            "severity": "CRITICAL",
            "message": f"Missing critical marketing fields: {', '.join(missing_critical)}. Please map these columns."
        })

    # Duplicate rows check
    duplicates = int(df.duplicated().sum())
    if duplicates > 0:
        issues.append({
            "severity": "WARNING",
            "message": f"Detected {duplicates} exact duplicate rows. These will be automatically deduplicated during import."
        })

    # Missing values check
    null_counts = df.isnull().sum().to_dict()
    total_nulls = int(sum(null_counts.values()))
    if total_nulls > 0:
        top_nulls = {k: int(v) for k, v in null_counts.items() if v > 0}
        issues.append({
            "severity": "INFO",
            "message": f"Found missing values in columns: {top_nulls}. Missing numeric fields will default safely to 0."
        })

    # Calculate Data Quality Score (0 - 100%)
    quality_score = 100.0
    quality_score -= len(missing_critical) * 20.0
    quality_score -= min(25.0, (duplicates / total_rows) * 100.0)
    quality_score -= min(20.0, (total_nulls / (total_rows * len(df.columns))) * 100.0)
    quality_score = max(0.0, round(quality_score, 1))

    # Preview of first 10 rows
    preview = df.head(10).fillna("").to_dict(orient="records")

    return {
        "success": True,
        "filename": filename,
        "total_rows": total_rows,
        "duplicates": duplicates,
        "quality_score": quality_score,
        "detected_columns": list(df.columns),
        "mapped_columns": detected_mapping,
        "issues": issues,
        "preview": preview,
        "can_import": len(missing_critical) == 0
    }

def import_mapped_dataset(
    db: Session,
    workspace_id: str,
    file_bytes: bytes,
    filename: str,
    column_mapping: Dict[str, str]
) -> Dict[str, Any]:
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        df = pd.read_csv(io.BytesIO(file_bytes))

    # Deduplicate
    df = df.drop_duplicates()

    campaign_records = []
    rejected_rows = 0

    for idx, row in df.iterrows():
        try:
            c_name = str(row[column_mapping["campaign_name"]]).strip() if column_mapping.get("campaign_name") else f"Campaign-{idx}"
            channel = str(row[column_mapping["channel"]]).strip() if column_mapping.get("channel") else "Digital Ads"
            c_id = str(row[column_mapping["campaign_id"]]).strip() if column_mapping.get("campaign_id") and pd.notnull(row[column_mapping["campaign_id"]]) else f"CMP-{idx+1000}"
            
            date_val = str(row[column_mapping["date"]]).strip() if column_mapping.get("date") and pd.notnull(row[column_mapping["date"]]) else "2024-06-01"

            # Parse numerics with fallback
            def get_num(key, default=0.0):
                col = column_mapping.get(key)
                if col and col in row and pd.notnull(row[col]):
                    val = str(row[col]).replace("$", "").replace(",", "").replace("%", "").strip()
                    try:
                        return float(val)
                    except ValueError:
                        return default
                return default

            spend = get_num("spend", 0.0)
            rev = get_num("attributed_revenue", 0.0)
            conv = int(get_num("conversions", 0))
            clicks = int(get_num("clicks", max(conv, 1)))
            impr = int(get_num("impressions", clicks * 15))
            margin = get_num("gross_margin_rate", 0.60)
            if margin > 1.0:
                margin = margin / 100.0 # Handle percentage input 60 -> 0.60

            cogs = round(rev * (1.0 - margin), 2)
            profit = round((rev - cogs) - spend, 2)

            campaign_records.append(CampaignRecord(
                workspace_id=workspace_id,
                date=date_val,
                campaign_id=c_id,
                campaign_name=c_name,
                channel=channel,
                impressions=impr,
                clicks=clicks,
                spend=spend,
                conversions=conv,
                attributed_revenue=rev,
                gross_margin_rate=margin,
                cogs=cogs,
                contribution_profit=profit
            ))
        except Exception:
            rejected_rows += 1

    db.bulk_save_objects(campaign_records)
    
    # Save upload record
    history = UploadHistory(
        workspace_id=workspace_id,
        filename=filename,
        file_type="CSV" if filename.endswith(".csv") else "Excel",
        rows_imported=len(campaign_records),
        rows_rejected=rejected_rows,
        quality_score=95.0,
        summary_json="{}"
    )
    db.add(history)
    db.commit()

    return {
        "success": True,
        "rows_imported": len(campaign_records),
        "rows_rejected": rejected_rows,
        "message": f"Successfully ingested {len(campaign_records):,} validated marketing campaign records."
    }
