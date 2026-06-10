import request from '../utils/request'

export function getTestCases(project, keyword, filters = {}) {
  const params = { ...filters }
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

export function exportTestCases(projectId, sprintId) {
  const params = {}
  if (projectId) params.project_id = projectId
  if (sprintId) params.sprint_id = sprintId
  return request({
    url: '/testcases/export',
    method: 'get',
    params,
    responseType: 'blob',
    timeout: 60000
  })
}

export function downloadTemplate() {
  return request({
    url: '/testcases/template',
    method: 'get',
    responseType: 'blob',
    timeout: 30000
  })
}

export function importTestCases(projectId, file, sprintId) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('project_id', projectId)
  if (sprintId) fd.append('sprint_id', sprintId)
  return request({
    url: '/testcases/import',
    method: 'post',
    data: fd,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}
