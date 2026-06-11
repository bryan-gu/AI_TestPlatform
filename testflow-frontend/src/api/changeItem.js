import request from '../utils/request'

export function getChangeItems(params) {
  return request({ url: '/change-items', method: 'get', params })
}

export function getChangeItem(id) {
  return request({ url: `/change-items/${id}`, method: 'get' })
}

export function createChangeItem(data) {
  return request({ url: '/change-items', method: 'post', data })
}

export function updateChangeItem(id, data) {
  return request({ url: `/change-items/${id}`, method: 'put', data })
}

export function deleteChangeItem(id) {
  return request({ url: `/change-items/${id}`, method: 'delete' })
}

export function analyzeSprintChangeItems(sprintId, data = {}) {
  return request({ url: `/change-items/analyze-sprint/${sprintId}`, method: 'post', data })
}

export function getChangeItemImpact(id, params = {}) {
  return request({ url: `/change-items/${id}/impact`, method: 'get', params })
}
