"""
文档解析服务 — 文本/结构化文件本地解析，复杂文档通过 MinerU API 解析

流程：上传文档 → BackgroundTask 触发 → 本地解析或 MinerU 异步解析 → 存入 content_preview
"""

import json
import os
import time
import zipfile
import io
import logging

import httpx

from app.core.database import SessionLocal
from app.models.document import Document
from app.models.ai_config import AIGlobalConfig
from app.crud import crud_knowledge_asset

logger = logging.getLogger(__name__)

MINERU_BASE_URL = "https://mineru.net/api/v4"
MODEL_VERSION = "vlm"  # 表格/公式处理最好
POLL_INTERVAL = 3  # 轮询间隔秒数
POLL_TIMEOUT = 300  # 最大等待秒数


class DocumentParser:
    """文档解析服务 — 文本/结构化文件本地解析，复杂文档走 MinerU API"""

    def parse_document(self, db_session, document_id: int):
        """主入口（在 BackgroundTask 中运行，使用独立 Session）

        Args:
            db_session: 传入 None 即可，内部会创建独立 Session
            document_id: 文档 ID
        """
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.warning(f"文档 ID={document_id} 不存在，跳过解析")
                return

            # 更新解析状态为"解析中"
            document.parse_status = "解析中"
            db.commit()

            # 纯文本/结构化文件本地解析；复杂文档再调用 MinerU
            local_result = self._parse_local_file(document.file_path)
            if local_result:
                markdown_content, asset_type, metadata = local_result
                document.content_preview = markdown_content
                document.parse_status = "已解析"
                db.commit()
                crud_knowledge_asset.upsert_asset_for_document(
                    db,
                    document,
                    source_kind="uploaded",
                    asset_type=asset_type,
                    metadata=metadata,
                )
                logger.info(
                    f"文档 ID={document_id} 本地解析成功，asset_type={asset_type}, 内容长度={len(markdown_content)}"
                )
                return

            # 从全局配置读取 Token
            token = self._get_token(db)
            if not token:
                document.parse_status = "解析失败"
                document.content_preview = "未配置 MinerU API Token，请在 AI 配置中设置"
                db.commit()
                logger.error("未配置 MinerU API Token")
                return

            # 调用 MinerU 解析
            markdown_content = self._parse_via_mineru(document.file_path, token)

            if markdown_content:
                document.content_preview = markdown_content
                document.parse_status = "已解析"
                db.commit()
                crud_knowledge_asset.upsert_asset_for_document(db, document, source_kind="uploaded")
                logger.info(f"文档 ID={document_id} 解析成功，内容长度={len(markdown_content)}")
            else:
                document.parse_status = "解析失败"
                document.content_preview = "MinerU 解析失败，请检查文件格式或重试"
                db.commit()
                crud_knowledge_asset.upsert_asset_for_document(db, document, source_kind="uploaded")
                logger.warning(f"文档 ID={document_id} MinerU 解析返回空内容")

        except Exception as e:
            logger.exception(f"文档解析异常: {e}")
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.parse_status = "解析失败"
                    document.content_preview = f"解析异常: {str(e)[:200]}"
                    db.commit()
                    crud_knowledge_asset.upsert_asset_for_document(db, document, source_kind="uploaded")
            except Exception:
                pass
        finally:
            db.close()

    def _parse_local_file(self, file_path: str) -> tuple[str, str, dict] | None:
        """本地解析 MinerU 不支持或不需要解析的文本/结构化文件。"""
        ext = os.path.splitext(file_path or "")[1].lower()
        if ext == ".json":
            return self._parse_json_file(file_path)
        if ext in (".md", ".txt", ".yaml", ".yml"):
            return self._parse_text_file(file_path, ext)
        return None

    def _parse_json_file(self, file_path: str) -> tuple[str, str, dict]:
        """解析 JSON 文件，OpenAPI/Swagger 标记为接口文档资产。"""
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        data = json.loads(raw_content)
        is_openapi = isinstance(data, dict) and (
            "openapi" in data or data.get("swagger") == "2.0" or "paths" in data
        )
        asset_type = "api_doc_openapi" if is_openapi else "test_case_json"
        metadata = {
            "parser": "local_json",
            "is_openapi": is_openapi,
        }

        if isinstance(data, dict):
            metadata.update({
                "top_level_keys": list(data.keys())[:50],
                "path_count": len(data.get("paths", {})) if isinstance(data.get("paths"), dict) else 0,
                "title": data.get("info", {}).get("title", "") if isinstance(data.get("info"), dict) else "",
                "version": data.get("info", {}).get("version", "") if isinstance(data.get("info"), dict) else "",
            })

        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        preview = formatted if len(formatted) <= 30000 else formatted[:30000] + "\n\n...（内容过长，已截断预览）"
        title = "OpenAPI / Swagger 接口文档" if is_openapi else "JSON 文件"
        content = f"# {title}\n\n```json\n{preview}\n```"
        return content, asset_type, metadata

    def _parse_text_file(self, file_path: str, ext: str) -> tuple[str, str, dict]:
        """解析 Markdown/TXT/YAML 等纯文本文件。"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lower_name = os.path.basename(file_path).lower()
        is_api_doc = "api" in lower_name or "接口" in lower_name
        asset_type = "api_doc_md" if is_api_doc and ext in (".md", ".yaml", ".yml") else "requirement_doc"
        metadata = {
            "parser": "local_text",
            "extension": ext,
            "is_api_doc": is_api_doc,
        }

        preview = content if len(content) <= 30000 else content[:30000] + "\n\n...（内容过长，已截断预览）"
        if ext == ".md":
            return preview, asset_type, metadata
        fence = "yaml" if ext in (".yaml", ".yml") else "text"
        return f"```{fence}\n{preview}\n```", asset_type, metadata

    def _get_token(self, db) -> str:
        """从 AIGlobalConfig 读取 MinerU Token"""
        config = db.query(AIGlobalConfig).filter(
            AIGlobalConfig.key == "mineru_api_token"
        ).first()
        return config.value if config and config.value else ""

    def _parse_via_mineru(self, file_path: str, token: str) -> str | None:
        """通过 MinerU 精准解析 API 解析文档"""
        file_name = os.path.basename(file_path)

        # Step 1: 获取签名上传 URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        data = {
            "files": [{"name": file_name, "data_id": file_name}],
            "model_version": MODEL_VERSION,
        }

        logger.info(f"MinerU: 申请上传 URL, 文件={file_name}")
        resp = httpx.post(
            f"{MINERU_BASE_URL}/file-urls/batch",
            headers=headers, json=data, timeout=30,
        )
        result = resp.json()
        if result.get("code") != 0:
            logger.error(f"MinerU 申请上传 URL 失败: code={result.get('code')}, msg={result.get('msg')}")
            return None

        batch_id = result["data"]["batch_id"]
        file_urls = result["data"]["file_urls"]

        # Step 2: PUT 上传文件
        logger.info(f"MinerU: 上传文件到签名 URL, batch_id={batch_id}")
        with open(file_path, "rb") as f:
            upload_resp = httpx.put(file_urls[0], content=f.read(), timeout=60)
        if upload_resp.status_code not in (200, 201):
            logger.error(f"MinerU 文件上传失败: status={upload_resp.status_code}")
            return None

        # Step 3: 轮询等待解析完成
        logger.info(f"MinerU: 开始轮询解析结果, batch_id={batch_id}")
        start = time.time()
        while time.time() - start < POLL_TIMEOUT:
            poll_resp = httpx.get(
                f"{MINERU_BASE_URL}/extract-results/batch/{batch_id}",
                headers=headers, timeout=30,
            )
            poll_result = poll_resp.json()
            extract_results = poll_result.get("data", {}).get("extract_result", [])

            if extract_results:
                file_result = extract_results[0]
                state = file_result.get("state")

                if state == "done":
                    zip_url = file_result.get("full_zip_url")
                    logger.info(f"MinerU: 解析完成, 开始下载 ZIP")
                    return self._download_and_extract_markdown(zip_url)

                if state == "failed":
                    err_msg = file_result.get("err_msg", "未知错误")
                    logger.error(f"MinerU 解析失败: {err_msg}")
                    return None

            elapsed = int(time.time() - start)
            logger.debug(f"MinerU: 轮询中... 已等待 {elapsed}s")
            time.sleep(POLL_INTERVAL)

        logger.error(f"MinerU 解析超时（{POLL_TIMEOUT}s）")
        return None

    def _download_and_extract_markdown(self, zip_url: str) -> str | None:
        """下载 ZIP 并提取 Markdown 文本"""
        resp = httpx.get(zip_url, timeout=60)
        if resp.status_code != 200:
            logger.error(f"MinerU ZIP 下载失败: status={resp.status_code}")
            return None

        # 从 ZIP 中提取 .md 文件
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            md_files = [n for n in zf.namelist() if n.endswith('.md')]
            if not md_files:
                logger.error("MinerU ZIP 中未找到 .md 文件")
                return None
            # 优先取 full.md 或第一个 .md
            target = next((f for f in md_files if f.endswith('full.md')), md_files[0])
            content = zf.read(target).decode('utf-8')
            logger.info(f"MinerU: 提取 Markdown 成功, 文件={target}, 长度={len(content)}")
            return content
