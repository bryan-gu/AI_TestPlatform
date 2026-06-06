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

export function exportTestCases(projectId) {
  return request({
    url: '/testcases/export',
    method: 'get',
    params: projectId ? { project_id: projectId } : {},
    responseType: 'blob',
    timeout: 60000
  }).catch(async err => {
    // blob 请求的错误需要从 blob 中解析 JSON
    if (err.response && err.response.data instanceof Blob) {
      const text = await err.response.data.text()
      try {
        const json = JSON.parse(text)
        err.response.data = json
      } catch (e) { /* ignore */ }
    }
    return Promise.reject(err)
  })
}

export function downloadTemplate() {
  return request({
    url: '/testcases/template',
    method: 'get',
    responseType: 'blob',
    timeout: 30000
  }).catch(async err => {
    if (err.response && err.response.data instanceof Blob) {
      const text = await err.response.data.text()
      try {
        const json = JSON.parse(text)
        err.response.data = json
      } catch (e) { /* ignore */ }
    }
    return Promise.reject(err)
  })
}

export function importTestCases(projectId, file) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('project_id', projectId)
  return request({
    url: '/testcases/import',
    method: 'post',
    data: fd,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}
