"""
数据导出API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.utils.export import ExportService
from app.services.data_asset_service import DataAssetService
from app.services.scenario_service import ScenarioService
from app.services.audit_service import AuditService
import io

router = APIRouter()


@router.get("/data-assets")
async def export_data_assets(
    format: str = Query("csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db)
):
    """导出数据资产"""
    service = DataAssetService(db)
    assets = service.list_assets(limit=10000)
    
    # 格式化数据
    export_service = ExportService()
    formatted_data = export_service.format_data_for_export(assets)
    
    if format == "csv":
        content, filename = export_service.export_to_csv(formatted_data)
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        content, filename = export_service.export_to_json(formatted_data)
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@router.get("/scenarios")
async def export_scenarios(
    format: str = Query("csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db)
):
    """导出跨境场景"""
    service = ScenarioService(db)
    scenarios = service.list_scenarios(limit=10000)
    
    export_service = ExportService()
    formatted_data = export_service.format_data_for_export(scenarios)
    
    if format == "csv":
        content, filename = export_service.export_to_csv(formatted_data, "scenarios_export.csv")
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        content, filename = export_service.export_to_json(formatted_data, "scenarios_export.json")
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@router.get("/audit-logs")
async def export_audit_logs(
    format: str = Query("csv", regex="^(csv|json)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """导出审计日志"""
    service = AuditService(db)
    logs = service.list_logs(limit=10000)
    
    export_service = ExportService()
    formatted_data = export_service.format_data_for_export(logs)
    
    if format == "csv":
        content, filename = export_service.export_to_csv(formatted_data, "audit_logs_export.csv")
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        content, filename = export_service.export_to_json(formatted_data, "audit_logs_export.json")
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

