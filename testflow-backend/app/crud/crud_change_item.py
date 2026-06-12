from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.change_item import ChangeItem
from app.schemas.change_item import ChangeItemCreate, ChangeItemUpdate


CHANGE_TYPE_LABELS = {
    "added": "新增",
    "modified": "修改",
    "removed": "删除",
    "deprecated": "废弃",
    "unknown": "未知",
}

STATUS_LABELS = {
    "open": "待处理",
    "confirmed": "已确认",
    "ignored": "已忽略",
    "resolved": "已解决",
    "applied": "已应用",
}

# 人工终态，重新分析时不会被回退为 open
TERMINAL_STATUSES = {"confirmed", "resolved", "ignored", "applied"}


def get_change_items(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    source_doc_id: int | None = None,
    source_asset_id: int | None = None,
    module_id: int | None = None,
    change_type: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    priority: str | None = None,
    impact_level: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[ChangeItem]:
    query = db.query(ChangeItem).filter(ChangeItem.is_deleted == False)  # noqa: E712
    query = _apply_filters(
        query,
        project_id=project_id,
        sprint_id=sprint_id,
        source_doc_id=source_doc_id,
        source_asset_id=source_asset_id,
        module_id=module_id,
        change_type=change_type,
        target_type=target_type,
        target_id=target_id,
        priority=priority,
        impact_level=impact_level,
        status=status,
        keyword=keyword,
    )
    return query.order_by(ChangeItem.created_at.desc(), ChangeItem.id.desc()).offset(skip).limit(limit).all()


def count_change_items(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    source_doc_id: int | None = None,
    source_asset_id: int | None = None,
    module_id: int | None = None,
    change_type: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    priority: str | None = None,
    impact_level: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> int:
    query = db.query(func.count(ChangeItem.id)).filter(ChangeItem.is_deleted == False)  # noqa: E712
    query = _apply_filters(
        query,
        project_id=project_id,
        sprint_id=sprint_id,
        source_doc_id=source_doc_id,
        source_asset_id=source_asset_id,
        module_id=module_id,
        change_type=change_type,
        target_type=target_type,
        target_id=target_id,
        priority=priority,
        impact_level=impact_level,
        status=status,
        keyword=keyword,
    )
    return query.scalar()


def _apply_filters(
    query,
    *,
    project_id: int | None = None,
    sprint_id: int | None = None,
    source_doc_id: int | None = None,
    source_asset_id: int | None = None,
    module_id: int | None = None,
    change_type: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    priority: str | None = None,
    impact_level: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
):
    if project_id is not None:
        query = query.filter(ChangeItem.project_id == project_id)
    if sprint_id is not None:
        query = query.filter(ChangeItem.sprint_id == sprint_id)
    if source_doc_id is not None:
        query = query.filter(ChangeItem.source_doc_id == source_doc_id)
    if source_asset_id is not None:
        query = query.filter(ChangeItem.source_asset_id == source_asset_id)
    if module_id is not None:
        query = query.filter(ChangeItem.module_id == module_id)
    if change_type:
        query = query.filter(ChangeItem.change_type == change_type)
    if target_type:
        query = query.filter(ChangeItem.target_type == target_type)
    if target_id is not None:
        query = query.filter(ChangeItem.target_id == target_id)
    if priority:
        query = query.filter(ChangeItem.priority == priority)
    if impact_level:
        query = query.filter(ChangeItem.impact_level == impact_level)
    if status:
        query = query.filter(ChangeItem.status == status)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (ChangeItem.title.ilike(kw))
            | (ChangeItem.description.ilike(kw))
            | (ChangeItem.evidence.ilike(kw))
        )
    return query


def get_change_item(db: Session, change_id: int) -> ChangeItem | None:
    return db.query(ChangeItem).filter(
        ChangeItem.id == change_id,
        ChangeItem.is_deleted == False,  # noqa: E712
    ).first()


def create_change_item(db: Session, data: ChangeItemCreate, *, commit: bool = True) -> ChangeItem:
    item = ChangeItem(**data.model_dump())
    db.add(item)
    if commit:
        db.commit()
        db.refresh(item)
    else:
        db.flush()
    return item


def upsert_change_item(db: Session, data: ChangeItemCreate, *, commit: bool = False) -> tuple[ChangeItem, bool]:
    existing = None
    if data.fingerprint:
        existing = db.query(ChangeItem).filter(
            ChangeItem.fingerprint == data.fingerprint,
            ChangeItem.is_deleted == False,  # noqa: E712
        ).first()

    if not existing and data.target_type and data.target_id:
        existing = db.query(ChangeItem).filter(
            ChangeItem.project_id == data.project_id,
            ChangeItem.sprint_id == data.sprint_id,
            ChangeItem.change_type == data.change_type,
            ChangeItem.target_type == data.target_type,
            ChangeItem.target_id == data.target_id,
            ChangeItem.is_deleted == False,  # noqa: E712
        ).first()

    if existing:
        # 保护人工终态状态：confirmed/resolved/ignored/applied 不被重新分析回退为 open
        is_terminal = existing.status in TERMINAL_STATUSES
        for field, value in data.model_dump().items():
            if is_terminal and field == "status":
                continue  # 保留人工状态，不覆盖
            setattr(existing, field, value)
        if commit:
            db.commit()
            db.refresh(existing)
        else:
            db.flush()
        return existing, False

    return create_change_item(db, data, commit=commit), True


def update_change_item(db: Session, item: ChangeItem, data: ChangeItemUpdate) -> ChangeItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def soft_delete_change_item(db: Session, item: ChangeItem) -> None:
    item.is_deleted = True
    item.deleted_at = datetime.utcnow()
    db.commit()
