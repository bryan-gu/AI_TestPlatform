import request from '../utils/request'

// ============ Providers ============

export function getProviders() {
  return request({ url: '/ai/providers', method: 'get' })
}

export function createProvider(data) {
  return request({ url: '/ai/providers', method: 'post', data })
}

export function updateProvider(id, data) {
  return request({ url: `/ai/providers/${id}`, method: 'put', data })
}

export function deleteProvider(id) {
  return request({ url: `/ai/providers/${id}`, method: 'delete' })
}

export function testProvider(id) {
  return request({ url: `/ai/providers/${id}/test`, method: 'post' })
}

// ============ Strategies ============

export function getStrategies() {
  return request({ url: '/ai/strategies', method: 'get' })
}

export function batchUpdateStrategies(strategies) {
  return request({ url: '/ai/strategies', method: 'put', data: { strategies } })
}

// ============ Global Config ============

export function getGlobalConfig() {
  return request({ url: '/ai/config', method: 'get' })
}

export function batchUpdateGlobalConfig(configs) {
  return request({ url: '/ai/config', method: 'put', data: { configs } })
}

// ============ Call Logs ============

export function getCallLogs(params) {
  return request({ url: '/ai/call-logs', method: 'get', params })
}

// ============ Stats ============

export function getAIStats() {
  return request({ url: '/ai/stats', method: 'get' })
}
