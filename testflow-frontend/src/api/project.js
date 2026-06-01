import request from '../utils/request'

export function getProjects() {
  return request({ url: '/projects', method: 'get' })
}

export function getProject(id) {
  return request({ url: `/projects/${id}`, method: 'get' })
}

export function createProject(data) {
  return request({ url: '/projects', method: 'post', data })
}

export function updateProject(id, data) {
  return request({ url: `/projects/${id}`, method: 'put', data })
}

export function deleteProject(id) {
  return request({ url: `/projects/${id}`, method: 'delete' })
}

export function getProjectTestcases(id) {
  return request({ url: `/projects/${id}/testcases`, method: 'get' })
}

export function getProjectReports(id) {
  return request({ url: `/projects/${id}/reports`, method: 'get' })
}
