"""
数据模型
作者：张彦龙
"""
from app.models.user import User, Role
from app.models.data_asset import DataAsset, DataClassification, SensitiveTag
from app.models.scenario import CrossBorderScenario, TransferApproval
from app.models.risk import RiskAssessment
from app.models.audit import AuditLog

__all__ = [
    "User",
    "Role",
    "DataAsset",
    "DataClassification",
    "SensitiveTag",
    "CrossBorderScenario",
    "TransferApproval",
    "RiskAssessment",
    "AuditLog",
]

