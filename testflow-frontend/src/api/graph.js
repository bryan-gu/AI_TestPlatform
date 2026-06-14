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

export function generateGraph(params) {
  return request({ url: '/graphs/generate', method: 'post', params })
}

export function deleteGraph(id) {
  return request({ url: `/graphs/${id}`, method: 'delete' })
}

export function regenerateGraph(id) {
  return request({ url: `/graphs/${id}/regenerate`, method: 'post' })
}

export function getSubgraph(id, params) {
  return request({ url: `/graphs/${id}/subgraph`, method: 'get', params })
}

export function getNodeNeighbors(id, nodeId, params) {
  return request({ url: `/graphs/${id}/node/${nodeId}/neighbors`, method: 'get', params })
}

export function searchGraphNodes(id, keyword) {
  return request({ url: `/graphs/${id}/search`, method: 'get', params: { keyword } })
}
