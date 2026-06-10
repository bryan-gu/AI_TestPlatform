import request from '../utils/request'

export function getTraceLinks(params) {
  return request({ url: '/trace-links', method: 'get', params })
}

export function getTraceLink(id) {
  return request({ url: `/trace-links/${id}`, method: 'get' })
}

export function getEntityTraceLinks(entityType, entityId, params = {}) {
  return request({ url: `/trace-links/entity/${entityType}/${entityId}`, method: 'get', params })
}

export function getEntityImpact(entityType, entityId) {
  return request({ url: `/trace-links/entity/${entityType}/${entityId}/impact`, method: 'get' })
}

export function createTraceLink(data) {
  return request({ url: '/trace-links', method: 'post', data })
}

export function updateTraceLink(id, data) {
  return request({ url: `/trace-links/${id}`, method: 'put', data })
}

export function deleteTraceLink(id) {
  return request({ url: `/trace-links/${id}`, method: 'delete' })
}

export function backfillTraceLinks(params) {
  return request({ url: '/trace-links/backfill', method: 'post', params })
}
