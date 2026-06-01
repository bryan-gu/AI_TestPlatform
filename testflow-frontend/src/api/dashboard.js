import request from '../utils/request'

export function getDashboardStats() {
  return request({ url: '/dashboard/stats', method: 'get' })
}

export function getDashboardActivities() {
  return request({ url: '/dashboard/activities', method: 'get' })
}
