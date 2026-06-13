import request from '../utils/request'

// ========== 功能点-用例覆盖关系 ==========

export function getFeaturePointTestCases(featurePointId) {
  return request({ url: `/coverage/feature-points/${featurePointId}/testcases`, method: 'get' })
}

export function getTestCaseFeaturePoints(testcaseId) {
  return request({ url: `/coverage/testcases/${testcaseId}/feature-points`, method: 'get' })
}

export function createFeaturePointTestCaseCoverage(featurePointId, testcaseId, data = {}) {
  return request({
    url: `/coverage/feature-points/${featurePointId}/testcases/${testcaseId}`,
    method: 'post',
    data,
  })
}

export function updateCoverage(coverageId, data) {
  return request({ url: `/coverage/${coverageId}`, method: 'put', data })
}

export function deleteCoverage(coverageId) {
  return request({ url: `/coverage/${coverageId}`, method: 'delete' })
}
