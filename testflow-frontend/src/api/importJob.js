import request from '../utils/request'

export function createImportJob(data) {
  return request({ url: '/import-jobs/local-project', method: 'post', data })
}

export function getImportJob(id) {
  return request({ url: `/import-jobs/${id}`, method: 'get' })
}

export function cancelImportJob(id) {
  return request({ url: `/import-jobs/${id}/cancel`, method: 'post' })
}
