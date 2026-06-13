import request from '../utils/request'

// ========== 接口端点 ==========

export function getApiEndpoints(params) {
  return request({ url: '/api-endpoints', method: 'get', params })
}

export function getApiEndpoint(id) {
  return request({ url: `/api-endpoints/${id}`, method: 'get' })
}

export function importOpenApi(data) {
  return request({ url: '/api-endpoints/import-openapi', method: 'post', data })
}

export function importMarkdownApi(data) {
  return request({ url: '/api-endpoints/import-markdown', method: 'post', data })
}

export function deleteApiEndpoint(id) {
  return request({ url: `/api-endpoints/${id}`, method: 'delete' })
}

// ========== 接口-用例关联 ==========

export function getApiEndpointTestCases(endpointId) {
  return request({ url: `/api-endpoints/${endpointId}/testcases`, method: 'get' })
}

export function linkApiEndpointTestCase(endpointId, caseId, data = {}) {
  return request({ url: `/api-endpoints/${endpointId}/link-testcase/${caseId}`, method: 'post', params: data })
}

export function unlinkApiEndpointTestCase(endpointId, caseId) {
  return request({ url: `/api-endpoints/${endpointId}/link-testcase/${caseId}`, method: 'delete' })
}

export function getTestCaseApiEndpoints(caseId) {
  return request({ url: `/api-endpoints/testcases/${caseId}`, method: 'get' })
}
