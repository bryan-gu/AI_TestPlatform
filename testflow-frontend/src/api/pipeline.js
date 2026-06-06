import request from '../utils/request'

// ============ Pipeline Executions ============

export function getExecutions(params) {
  return request({ url: '/pipeline/executions', method: 'get', params })
}

export function getExecution(id) {
  return request({ url: `/pipeline/executions/${id}`, method: 'get' })
}

export function createExecution(data) {
  return request({ url: '/pipeline/executions', method: 'post', data })
}

export function pauseExecution(id) {
  return request({ url: `/pipeline/executions/${id}/pause`, method: 'post' })
}

export function resumeExecution(id) {
  return request({ url: `/pipeline/executions/${id}/resume`, method: 'post' })
}

export function getExecutionStatus(id) {
  return request({ url: `/pipeline/executions/${id}/status`, method: 'get' })
}

export function deleteExecution(id) {
  return request({ url: `/pipeline/executions/${id}`, method: 'delete' })
}

// ============ 产物查询 ============

export function getExecutionFeaturePoints(id) {
  return request({ url: `/pipeline/executions/${id}/feature-points`, method: 'get' })
}

export function getExecutionTestCases(id) {
  return request({ url: `/pipeline/executions/${id}/test-cases`, method: 'get' })
}

export function downloadExecutionExcel(id) {
  return request({
    url: `/pipeline/executions/${id}/download/excel`,
    method: 'get',
    responseType: 'blob',
  })
}
