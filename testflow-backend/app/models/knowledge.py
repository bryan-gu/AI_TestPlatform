# Legacy knowledge models have been replaced by Sprint, Module, Document
# See:
#   app/models/sprint.py    — Sprint 替代 KnowledgeBase
#   app/models/module.py    — Module 变为项目级 AI 标签字典（替代 Folder 层级容器）
#   app/models/document.py  — Document 直接挂在 Sprint 下，module_ids JSON 存储标签关联
