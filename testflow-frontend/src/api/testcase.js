import request from '../utils/request'

export function getTestCases(project, keyword) {
  const params = {}
  if (project) params.project = project
  if (keyword) params.keyword = keyword
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

export function batchExecuteTestCases(projectId) {
  const params = {}
  if (projectId) params.project_id = projectId
  return request({ url: '/testcases/batch-execute', method: 'post', params })
}
