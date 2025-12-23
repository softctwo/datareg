import React, { useState, useEffect } from 'react'
import {
  Table,
  Space,
  Select,
  Button,
  Tag,
  message,
  Card,
  Row,
  Col,
  Statistic,
  Dropdown
} from 'antd'
import { ReloadOutlined, WarningOutlined, DownloadOutlined } from '@ant-design/icons'
import { auditApi, exportApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Option } = Select

interface AuditLog {
  id: number
  action: string
  resource_type?: string
  resource_id?: number
  user_id: number
  username?: string
  ip_address?: string
  transfer_volume?: number
  destination_country?: string
  transfer_status?: string
  is_anomaly: boolean
  anomaly_type?: string
  created_at: string
}

const AuditLogs: React.FC = () => {
  const [data, setData] = useState<AuditLog[]>([])
  const [statistics, setStatistics] = useState<any>(null)
  const [anomalies, setAnomalies] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    action: undefined,
    resource_type: undefined,
    is_anomaly: undefined
  })

  useEffect(() => {
    loadData()
    loadStatistics()
    loadAnomalies()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const result: any = await auditApi.list({ ...filters })
      setData(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载数据失败: ' + (error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const result: any = await auditApi.getStatistics({})
      setStatistics(result)
    } catch (error) {
      console.error('加载统计失败:', error)
    }
  }

  const loadAnomalies = async () => {
    try {
      const result: any = await auditApi.listAnomalies({ limit: 10 })
      setAnomalies(Array.isArray(result) ? result : [])
    } catch (error) {
      console.error('加载异常失败:', error)
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleSearch = () => {
    loadData()
  }

  const getActionTag = (action: string) => {
    const colorMap: Record<string, string> = {
      '创建': 'green',
      '更新': 'blue',
      '删除': 'red',
      '审批': 'orange',
      '拒绝': 'red',
      '传输': 'purple',
      '拦截': 'red'
    }
    return <Tag color={colorMap[action] || 'default'}>{action}</Tag>
  }

  const columns: ColumnsType<AuditLog> = [
    {
      title: '操作类型',
      dataIndex: 'action',
      key: 'action',
      width: 100,
      render: (action) => getActionTag(action)
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 120
    },
    {
      title: '资源ID',
      dataIndex: 'resource_id',
      key: 'resource_id',
      width: 100
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      width: 120
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150
    },
    {
      title: '目的国',
      dataIndex: 'destination_country',
      key: 'destination_country',
      width: 100
    },
    {
      title: '传输量',
      dataIndex: 'transfer_volume',
      key: 'transfer_volume',
      width: 120,
      render: (volume) => volume ? volume.toLocaleString() : '-'
    },
    {
      title: '传输状态',
      dataIndex: 'transfer_status',
      key: 'transfer_status',
      width: 100,
      render: (status) => {
        if (!status) return '-'
        const color = status === '成功' ? 'green' : status === '拦截' ? 'red' : 'orange'
        return <Tag color={color}>{status}</Tag>
      }
    },
    {
      title: '异常',
      dataIndex: 'is_anomaly',
      key: 'is_anomaly',
      width: 80,
      render: (isAnomaly) => isAnomaly ? <Tag color="red">是</Tag> : <Tag>否</Tag>
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss')
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>审计日志</h1>
        <Dropdown
          menu={{
            items: [
              {
                key: 'csv',
                label: '导出为CSV',
                onClick: async () => {
                  try {
                    const response = await fetch('/api/v1/export/audit-logs?format=csv', {
                      headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                      }
                    })
                    const blob = await response.blob()
                    const url = window.URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `audit_logs_${new Date().getTime()}.csv`
                    document.body.appendChild(a)
                    a.click()
                    window.URL.revokeObjectURL(url)
                    document.body.removeChild(a)
                    message.success('导出成功')
                  } catch (error: any) {
                    message.error('导出失败: ' + (error.message || '未知错误'))
                  }
                }
              },
              {
                key: 'json',
                label: '导出为JSON',
                onClick: async () => {
                  try {
                    const response = await fetch('/api/v1/export/audit-logs?format=json', {
                      headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                      }
                    })
                    const blob = await response.blob()
                    const url = window.URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `audit_logs_${new Date().getTime()}.json`
                    document.body.appendChild(a)
                    a.click()
                    window.URL.revokeObjectURL(url)
                    document.body.removeChild(a)
                    message.success('导出成功')
                  } catch (error: any) {
                    message.error('导出失败: ' + (error.message || '未知错误'))
                  }
                }
              }
            ]
          }}
        >
          <Button icon={<DownloadOutlined />}>
            导出数据
          </Button>
        </Dropdown>
      </div>

      {statistics && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总操作数"
                value={statistics.total_operations || 0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="异常操作"
                value={statistics.anomaly_count || 0}
                valueStyle={{ color: '#cf1322' }}
                prefix={<WarningOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总传输量"
                value={statistics.total_transfer_volume || 0}
                precision={0}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="目的国数量"
                value={Object.keys(statistics.country_statistics || {}).length}
              />
            </Card>
          </Col>
        </Row>
      )}

      {anomalies.length > 0 && (
        <Card
          title="最近异常行为"
          style={{ marginBottom: 16 }}
          extra={
            <Button type="link" onClick={loadAnomalies}>
              查看更多
            </Button>
          }
        >
          <Table
            columns={columns}
            dataSource={anomalies}
            rowKey="id"
            size="small"
            pagination={false}
          />
        </Card>
      )}

      <Card>
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="操作类型"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => handleFilterChange('action', value)}
          >
            <Option value="创建">创建</Option>
            <Option value="更新">更新</Option>
            <Option value="删除">删除</Option>
            <Option value="审批">审批</Option>
            <Option value="传输">传输</Option>
            <Option value="拦截">拦截</Option>
          </Select>
          <Select
            placeholder="资源类型"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => handleFilterChange('resource_type', value)}
          >
            <Option value="数据资产">数据资产</Option>
            <Option value="场景">场景</Option>
            <Option value="审批">审批</Option>
            <Option value="评估">评估</Option>
          </Select>
          <Select
            placeholder="异常筛选"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => handleFilterChange('is_anomaly', value)}
          >
            <Option value={true}>仅异常</Option>
            <Option value={false}>仅正常</Option>
          </Select>
          <Button type="primary" icon={<ReloadOutlined />} onClick={handleSearch}>
            查询
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`
          }}
        />
      </Card>
    </div>
  )
}

export default AuditLogs
