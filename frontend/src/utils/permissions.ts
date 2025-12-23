/**
 * 权限工具函数
 * 作者：张彦龙
 */

import { authApi } from '../services/api'

export interface Permission {
  value: string
  label: string
  group: string
}

export const PERMISSIONS: Permission[] = [
  // 数据资产权限
  { value: 'data_asset:read', label: '数据资产-查看', group: '数据资产' },
  { value: 'data_asset:write', label: '数据资产-编辑', group: '数据资产' },
  { value: 'data_asset:delete', label: '数据资产-删除', group: '数据资产' },
  { value: 'data_asset:scan', label: '数据资产-扫描', group: '数据资产' },
  { value: 'data_asset:export', label: '数据资产-导出', group: '数据资产' },
  
  // 场景权限
  { value: 'scenario:read', label: '场景-查看', group: '跨境场景' },
  { value: 'scenario:write', label: '场景-编辑', group: '跨境场景' },
  { value: 'scenario:delete', label: '场景-删除', group: '跨境场景' },
  { value: 'scenario:approve', label: '场景-审批', group: '跨境场景' },
  
  // 风险评估权限
  { value: 'risk:read', label: '风险评估-查看', group: '风险评估' },
  { value: 'risk:write', label: '风险评估-编辑', group: '风险评估' },
  { value: 'risk:calculate', label: '风险评估-计算', group: '风险评估' },
  
  // 审批权限
  { value: 'approval:read', label: '审批-查看', group: '传输审批' },
  { value: 'approval:write', label: '审批-创建', group: '传输审批' },
  { value: 'approval:approve', label: '审批-批准', group: '传输审批' },
  { value: 'approval:reject', label: '审批-拒绝', group: '传输审批' },
  
  // 审计权限
  { value: 'audit:read', label: '审计-查看', group: '审计日志' },
  { value: 'audit:export', label: '审计-导出', group: '审计日志' },
  
  // 用户权限
  { value: 'user:read', label: '用户-查看', group: '用户管理' },
  { value: 'user:write', label: '用户-编辑', group: '用户管理' },
  { value: 'user:delete', label: '用户-删除', group: '用户管理' },
  
  // 角色权限
  { value: 'role:read', label: '角色-查看', group: '角色管理' },
  { value: 'role:write', label: '角色-编辑', group: '角色管理' },
  { value: 'role:delete', label: '角色-删除', group: '角色管理' },
  { value: 'role:assign', label: '角色-分配', group: '角色管理' },
  
  // 仪表盘权限
  { value: 'dashboard:read', label: '仪表盘-查看', group: '监控仪表盘' },
  
  // 通知权限
  { value: 'notification:read', label: '通知-查看', group: '通知与提醒' },
  { value: 'notification:write', label: '通知-管理', group: '通知与提醒' },
  
  // 系统配置权限
  { value: 'config:read', label: '系统配置-查看', group: '系统配置管理' },
  { value: 'config:write', label: '系统配置-编辑', group: '系统配置管理' },
  { value: 'config:delete', label: '系统配置-删除', group: '系统配置管理' },
]

// 按组分类权限
export const PERMISSIONS_BY_GROUP = PERMISSIONS.reduce((acc, perm) => {
  if (!acc[perm.group]) {
    acc[perm.group] = []
  }
  acc[perm.group].push(perm)
  return acc
}, {} as Record<string, Permission[]>)

/**
 * 检查用户是否有指定权限
 */
export function hasPermission(userPermissions: string[], permission: string): boolean {
  if (!userPermissions || userPermissions.length === 0) {
    return false
  }
  // 超级用户拥有所有权限
  if (userPermissions.includes('*')) {
    return true
  }
  return userPermissions.includes(permission)
}

/**
 * 检查用户是否有任一权限
 */
export function hasAnyPermission(userPermissions: string[], permissions: string[]): boolean {
  if (!userPermissions || userPermissions.length === 0) {
    return false
  }
  if (userPermissions.includes('*')) {
    return true
  }
  return permissions.some(p => userPermissions.includes(p))
}

/**
 * 检查用户是否有所有权限
 */
export function hasAllPermissions(userPermissions: string[], permissions: string[]): boolean {
  if (!userPermissions || userPermissions.length === 0) {
    return false
  }
  if (userPermissions.includes('*')) {
    return true
  }
  return permissions.every(p => userPermissions.includes(p))
}

/**
 * 获取当前用户的权限列表
 */
export async function getUserPermissions(): Promise<string[]> {
  try {
    const permissions = await authApi.getCurrentUserPermissions()
    return permissions || []
  } catch (error) {
    console.error('获取用户权限失败:', error)
    return []
  }
}

