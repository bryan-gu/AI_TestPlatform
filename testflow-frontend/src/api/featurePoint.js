import request from '../utils/request'

export function getFeaturePoints(params) {
  return request({ url: '/feature-points', method: 'get', params })
}

export function createFeaturePoint(data) {
  return request({ url: '/feature-points', method: 'post', data })
}

export function updateFeaturePoint(id, data) {
  return request({ url: `/feature-points/${id}`, method: 'put', data })
}

export function deleteFeaturePoint(id) {
  return request({ url: `/feature-points/${id}`, method: 'delete' })
}
