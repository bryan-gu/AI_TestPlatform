import request from '../utils/request'

// ========== 知识库 ==========
export function getKnowledgeBases(keyword) {
  return request({ url: '/knowledge', method: 'get', params: { keyword } })
}

export function getKnowledgeStats() {
  return request({ url: '/knowledge/stats', method: 'get' })
}

export function getKnowledgeBase(id) {
  return request({ url: `/knowledge/${id}`, method: 'get' })
}

export function createKnowledgeBase(data) {
  return request({ url: '/knowledge', method: 'post', data })
}

export function updateKnowledgeBase(id, data) {
  return request({ url: `/knowledge/${id}`, method: 'put', data })
}

export function deleteKnowledgeBase(id) {
  return request({ url: `/knowledge/${id}`, method: 'delete' })
}

// ========== 文件夹 ==========
export function getFolders(kbId) {
  return request({ url: `/knowledge/${kbId}/folders`, method: 'get' })
}

export function createFolder(kbId, data) {
  return request({ url: `/knowledge/${kbId}/folders`, method: 'post', data })
}

export function updateFolder(kbId, folderId, data) {
  return request({ url: `/knowledge/${kbId}/folders/${folderId}`, method: 'put', data })
}

export function deleteFolder(kbId, folderId) {
  return request({ url: `/knowledge/${kbId}/folders/${folderId}`, method: 'delete' })
}

// ========== 文档 ==========
export function getDocuments(kbId, folderId) {
  return request({ url: `/knowledge/${kbId}/folders/${folderId}/documents`, method: 'get' })
}

export function uploadDocument(kbId, folderId, formData) {
  return request({
    url: `/knowledge/${kbId}/folders/${folderId}/documents`,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function updateDocument(kbId, folderId, docId, data) {
  return request({ url: `/knowledge/${kbId}/folders/${folderId}/documents/${docId}`, method: 'put', data })
}

export function deleteDocument(kbId, folderId, docId) {
  return request({ url: `/knowledge/${kbId}/folders/${folderId}/documents/${docId}`, method: 'delete' })
}
