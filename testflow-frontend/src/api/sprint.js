import request from '../utils/request'

// ========== Sprint CRUD ==========
export function getSprints(params) {
  return request({ url: '/sprints', method: 'get', params })
}

export function getSprintStats(projectId) {
  return request({ url: '/sprints/stats', method: 'get', params: { project_id: projectId } })
}

export function getSprint(id) {
  return request({ url: `/sprints/${id}`, method: 'get' })
}

export function createSprint(data) {
  return request({ url: '/sprints', method: 'post', data })
}

export function updateSprint(id, data) {
  return request({ url: `/sprints/${id}`, method: 'put', data })
}

export function deleteSprint(id) {
  return request({ url: `/sprints/${id}`, method: 'delete' })
}

// ========== Sprint 下文档 ==========
export function getSprintDocuments(sprintId) {
  return request({ url: `/sprints/${sprintId}/documents`, method: 'get' })
}

export function uploadSprintDocument(sprintId, formData) {
  return request({
    url: `/sprints/${sprintId}/documents`,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function updateSprintDocument(sprintId, docId, data) {
  return request({ url: `/sprints/${sprintId}/documents/${docId}`, method: 'put', data })
}

export function deleteSprintDocument(sprintId, docId) {
  return request({ url: `/sprints/${sprintId}/documents/${docId}`, method: 'delete' })
}

// ========== Module 标签 CRUD ==========
export function getModules(params) {
  return request({ url: '/modules', method: 'get', params })
}

export function getModule(id) {
  return request({ url: `/modules/${id}`, method: 'get' })
}

export function createModule(data) {
  return request({ url: '/modules', method: 'post', data })
}

export function updateModule(id, data) {
  return request({ url: `/modules/${id}`, method: 'put', data })
}

export function deleteModule(id) {
  return request({ url: `/modules/${id}`, method: 'delete' })
}
