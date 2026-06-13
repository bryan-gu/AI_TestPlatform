import request from '../utils/request'

export function getKnowledgeAssets(params) {
  return request({ url: '/knowledge-assets', method: 'get', params })
}

export function getKnowledgeAsset(id) {
  return request({ url: `/knowledge-assets/${id}`, method: 'get' })
}

export function createKnowledgeAsset(data) {
  return request({ url: '/knowledge-assets', method: 'post', data })
}

export function updateKnowledgeAsset(id, data) {
  return request({ url: `/knowledge-assets/${id}`, method: 'put', data })
}

export function deleteKnowledgeAsset(id) {
  return request({ url: `/knowledge-assets/${id}`, method: 'delete' })
}

export function importLocalProject(data) {
  return request({ url: '/knowledge-assets/import-local-project', method: 'post', data })
}
