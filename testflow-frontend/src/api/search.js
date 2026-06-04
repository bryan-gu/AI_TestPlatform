import request from '../utils/request'

// ============ Global Search ============

export function globalSearch(q, types = 'project,testcase,document,user') {
  return request({ url: '/search', method: 'get', params: { q, types } })
}
