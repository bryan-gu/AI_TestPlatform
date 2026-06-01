import request from '../utils/request'

export function getTestCases(project) {
  const params = project ? { project } : {}
  return request({ url: '/testcases', method: 'get', params })
}

export function getTestCaseStats() {
  return request({ url: '/testcases/stats', method: 'get' })
}

export function createTestCase(data) {
  return request({ url: '/testcases', method: 'post', data })
}

export function updateTestCase(id, data) {
  return request({ url: `/testcases/${id}`, method: 'put', data })
}

export function deleteTestCase(id) {
  return request({ url: `/testcases/${id}`, method: 'delete' })
}
