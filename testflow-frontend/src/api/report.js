import request from '../utils/request'

export function getReports() {
  return request({ url: '/reports', method: 'get' })
}

export function getReportStats() {
  return request({ url: '/reports/stats', method: 'get' })
}

export function createReport(data) {
  return request({ url: '/reports', method: 'post', data })
}

export function updateReport(id, data) {
  return request({ url: `/reports/${id}`, method: 'put', data })
}

export function deleteReport(id) {
  return request({ url: `/reports/${id}`, method: 'delete' })
}
