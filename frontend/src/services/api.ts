import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果响应有data字段，返回data，否则返回整个response
    return response.data !== undefined ? response.data : response
  },
  (error) => {
    console.error('API Error:', error)
    // 401未授权，清除token并跳转登录
    if (error.response?.status === 401) {
      const token = localStorage.getItem('token')
      if (token) {
        // 只有在有token的情况下才清除，避免无限循环
        localStorage.removeItem('token')
        // 延迟跳转，避免在加载页面时立即跳转
        setTimeout(() => {
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }, 100)
      }
    }
    // 返回错误响应数据
    return Promise.reject(error.response?.data || error)
  }
)

export const dashboardApi = {
  getOverview: (days: number = 7) => api.get('/dashboard/overview', { params: { days } }),
  getTransferTrends: (days: number = 30) => api.get('/dashboard/transfer-trends', { params: { days } }),
  getCountryDistribution: (days: number = 30) => api.get('/dashboard/country-distribution', { params: { days } }),
  getRiskAlerts: () => api.get('/dashboard/risk-alerts'),
  getDataAssetStatistics: () => api.get('/dashboard/data-asset-statistics'),
  getRiskStatistics: () => api.get('/dashboard/risk-statistics'),
  getApprovalStatistics: (days: number = 30) => api.get('/dashboard/approval-statistics', { params: { days } }),
  getOperationStatistics: (days: number = 7) => api.get('/dashboard/operation-statistics', { params: { days } }),
  getHeatmapData: (days: number = 30) => api.get('/dashboard/heatmap', { params: { days } }),
  getApprovalFunnel: (days: number = 30) => api.get('/dashboard/approval-funnel', { params: { days } }),
  getRiskScatter: () => api.get('/dashboard/risk-scatter'),
  getRiskRadar: (assessmentId?: number) => api.get('/dashboard/risk-radar', { params: { assessment_id: assessmentId } })
}

export const dataAssetsApi = {
  list: (params: any) => api.get('/data-assets/', { params }),  // 使用尾部斜杠
  get: (id: number) => api.get(`/data-assets/${id}`),
  create: (data: any) => api.post('/data-assets/', data),  // 使用尾部斜杠
  update: (id: number, data: any) => api.put(`/data-assets/${id}`, data),
  scan: (sourceSystem?: string) => api.post('/data-assets/scan', null, { params: { source_system: sourceSystem } }),
  getLineage: (id: number, depth: number = 2) => api.get(`/data-assets/${id}/lineage`, { params: { depth } })
}

export const scenariosApi = {
  list: (params: any) => api.get('/scenarios/', { params }),  // 使用尾部斜杠
  get: (id: number) => api.get(`/scenarios/${id}`),
  create: (data: any) => api.post('/scenarios/', data),  // 使用尾部斜杠
  update: (id: number, data: any) => api.put(`/scenarios/${id}`, data),
  submit: (id: number) => api.post(`/scenarios/${id}/submit`),
  approve: (id: number, approverId: number, comment?: string) => 
    api.post(`/scenarios/${id}/approve`, null, { params: { approver_id: approverId, comment } }),
  reject: (id: number, approverId: number, reason: string) => 
    api.post(`/scenarios/${id}/reject`, null, { params: { approver_id: approverId, reason } })
}

export const riskAssessmentsApi = {
  list: (params: any) => api.get('/risk-assessments/', { params }),  // 使用尾部斜杠
  get: (id: number) => api.get(`/risk-assessments/${id}`),
  create: (data: any) => api.post('/risk-assessments/', data),  // 使用尾部斜杠
  calculate: (id: number) => api.post(`/risk-assessments/${id}/calculate`),
  checkThresholds: (id: number) => api.get(`/risk-assessments/${id}/threshold-check`)
}

export const approvalsApi = {
  list: (params: any) => api.get('/approvals/', { params }),  // 使用尾部斜杠
  get: (id: number) => api.get(`/approvals/${id}`),
  create: (data: any) => api.post('/approvals/', data),  // 使用尾部斜杠
  approve: (id: number, approverId: number, comment?: string) => 
    api.post(`/approvals/${id}/approve`, null, { params: { approver_id: approverId, comment } }),
  reject: (id: number, approverId: number, reason: string) => 
    api.post(`/approvals/${id}/reject`, null, { params: { approver_id: approverId, reason } })
}

export const auditApi = {
  list: (params: any) => api.get('/audit/', { params }),  // 使用尾部斜杠
  getStatistics: (params: any) => api.get('/audit/statistics', { params }),
  listAnomalies: (params: any) => api.get('/audit/anomalies', { params })
}

export const authApi = {
  login: (username: string, password: string) => api.post('/auth/login', new URLSearchParams({ username, password }), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  getCurrentUser: () => api.get('/auth/me'),
  getCurrentUserPermissions: () => api.get('/auth/me/permissions')
}

export const usersApi = {
  list: (params?: any) => api.get('/users/', { params }),  // 使用尾部斜杠
  get: (id: number) => api.get(`/users/${id}`),
  create: (data: any) => api.post('/users/', data),  // 使用尾部斜杠
  update: (id: number, data: any) => api.put(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`)
}

export const rolesApi = {
  list: () => api.get('/roles/'),  // 使用尾部斜杠
  get: (id: number) => api.get(`/roles/${id}`),
  create: (data: any) => api.post('/roles/', data),  // 使用尾部斜杠
  update: (id: number, data: any) => api.put(`/roles/${id}`, data),
  delete: (id: number) => api.delete(`/roles/${id}`),
  assign: (userId: number, roleIds: number[]) => api.post('/roles/assign', { user_id: userId, role_ids: roleIds }),
  getUserPermissions: (userId: number) => api.get(`/roles/user/${userId}/permissions`)
}

export const interceptionApi = {
  check: (request: any) => api.post('/interception/check', request),
  getWhitelist: () => api.get('/interception/whitelist'),
  addToWhitelist: (approvalId: number) => api.post(`/interception/whitelist/${approvalId}`),
  removeFromWhitelist: (approvalId: number) => api.delete(`/interception/whitelist/${approvalId}`),
  getBlacklist: () => api.get('/interception/blacklist'),
  addToBlacklist: (assetId: number, reason?: string) => api.post(`/interception/blacklist/${assetId}`, { reason }),
  removeFromBlacklist: (assetId: number) => api.delete(`/interception/blacklist/${assetId}`),
  desensitize: (request: any) => api.post('/interception/desensitize', request)
}

export const batchApi = {
  approveScenarios: (scenarioIds: number[], approverId: number, comment?: string) => 
    api.post('/batch/scenarios/approve', { scenario_ids: scenarioIds, approver_id: approverId, comment }),
  rejectScenarios: (scenarioIds: number[], approverId: number, reason: string) => 
    api.post('/batch/scenarios/reject', { scenario_ids: scenarioIds, approver_id: approverId, reason }),
  approveTransfers: (approvalIds: number[], approverId: number, comment?: string) => 
    api.post('/batch/approvals/approve', { approval_ids: approvalIds, approver_id: approverId, comment }),
  rejectTransfers: (approvalIds: number[], approverId: number, reason: string) => 
    api.post('/batch/approvals/reject', { approval_ids: approvalIds, approver_id: approverId, reason }),
  deleteDataAssets: (assetIds: number[]) => api.post('/batch/data-assets/delete', { asset_ids: assetIds })
}

export const notificationsApi = {
  list: (params?: any) => api.get('/notifications/', { params }),  // 使用尾部斜杠避免重定向
  get: (id: number) => api.get(`/notifications/${id}`),
  getStats: () => api.get('/notifications/stats'),
  markAsRead: (id: number) => api.put(`/notifications/${id}/read`),
  markAllAsRead: () => api.put('/notifications/read-all'),
  delete: (id: number) => api.delete(`/notifications/${id}`),
  create: (data: any) => api.post('/notifications', data)
}

export const systemConfigApi = {
  list: (params?: any) => api.get('/system-config/', { params }),  // 使用尾部斜杠避免重定向
  get: (id: number) => api.get(`/system-config/${id}`),
  getByKey: (key: string) => api.get(`/system-config/key/${key}`),
  getPublic: () => api.get('/system-config/public'),
  create: (data: any) => api.post('/system-config', data),
  update: (id: number, data: any) => api.put(`/system-config/${id}`, data),
  setValue: (key: string, value: string) => api.put(`/system-config/key/${key}/value`, null, { params: { value } }),
  delete: (id: number) => api.delete(`/system-config/${id}`)
}

export default api

