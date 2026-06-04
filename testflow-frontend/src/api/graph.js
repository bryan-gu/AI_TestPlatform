import request from '../utils/request'

// ============ Graphs ============

export function getGraphs(params) {
  return request({ url: '/graphs', method: 'get', params })
}

export function getGraphStats() {
  return request({ url: '/graphs/stats', method: 'get' })
}

export function getGraphDetail(id) {
  return request({ url: `/graphs/${id}`, method: 'get' })
}

export function createGraph(data) {
  return request({ url: '/graphs', method: 'post', data })
}

export function deleteGraph(id) {
  return request({ url: `/graphs/${id}`, method: 'delete' })
}

export function regenerateGraph(id) {
  return request({ url: `/graphs/${id}/regenerate`, method: 'post' })
}
