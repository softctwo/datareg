import React, { useState, useEffect } from 'react'
import {
  List,
  Card,
  Badge,
  Button,
  Space,
  Tag,
  message,
  Popconfirm,
  Empty,
  Statistic,
  Row,
  Col,
  Tabs,
  Select
} from 'antd'
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  ReloadOutlined,
  ReadOutlined
} from '@ant-design/icons'
import { notificationsApi } from '../services/api'
import dayjs from 'dayjs'
import { useNavigate } from 'react-router-dom'

const { Option } = Select

interface Notification {
  id: number
  type: string
  title: string
  content?: string
  status: string
  is_read: boolean
  resource_type?: string
  resource_id?: number
  action_url?: string
  priority: number
  created_at: string
  read_at?: string
}

interface NotificationStats {
  total: number
  unread: number
  read: number
  by_type: Record<string, number>
}

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [stats, setStats] = useState<NotificationStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
    loadStats()
  }, [filter, typeFilter])

  const loadData = async () => {
    setLoading(true)
    try {
      const params: any = {
        skip: 0,
        limit: 100
      }
      if (filter === 'unread') {
        params.is_read = false
      } else if (filter === 'read') {
        params.is_read = true
      }
      if (typeFilter !== 'all') {
        params.notification_type = typeFilter
      }
      const result = await notificationsApi.list(params)
      setNotifications(Array.isArray(result) ? result : [])
    } catch (error: any) {
      // 401/403错误会被拦截器处理，这里只处理其他错误
      const status = error.response?.status || error.status
      if (status !== 401 && status !== 403) {
        message.error('加载通知失败: ' + (error.detail || error.message || '未知错误'))
      } else if (status === 403) {
        message.error('权限不足，无法访问通知中心')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const result = await notificationsApi.getStats()
      setStats(result)
    } catch (error: any) {
      // 401/403错误会被拦截器处理，这里只记录其他错误
      if (error.response?.status !== 401 && error.response?.status !== 403) {
        console.error('加载统计失败:', error)
      }
    }
  }

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationsApi.markAsRead(id)
      message.success('已标记为已读')
      loadData()
      loadStats()
    } catch (error: any) {
      message.error('操作失败: ' + (error.message || '未知错误'))
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      const result: any = await notificationsApi.markAllAsRead()
      message.success(result.message || '已全部标记为已读')
      loadData()
      loadStats()
    } catch (error: any) {
      message.error('操作失败: ' + (error.message || '未知错误'))
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await notificationsApi.delete(id)
      message.success('已删除')
      loadData()
      loadStats()
    } catch (error: any) {
      message.error('删除失败: ' + (error.message || '未知错误'))
    }
  }

  const handleClick = (notification: Notification) => {
    // 标记为已读
    if (!notification.is_read) {
      handleMarkAsRead(notification.id)
    }
    
    // 如果有操作链接，跳转
    if (notification.action_url) {
      navigate(notification.action_url)
    }
  }

  const getTypeTag = (type: string) => {
    const colorMap: Record<string, string> = {
      '审批待办': 'blue',
      '阈值预警': 'orange',
      '异常告警': 'red',
      '系统通知': 'green',
      '提醒': 'default'
    }
    return <Tag color={colorMap[type] || 'default'}>{type}</Tag>
  }

  const getPriorityTag = (priority: number) => {
    if (priority === 2) {
      return <Tag color="red">紧急</Tag>
    } else if (priority === 1) {
      return <Tag color="orange">重要</Tag>
    }
    return null
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>通知中心</h1>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => { loadData(); loadStats() }} loading={loading}>
            刷新
          </Button>
          {stats && stats.unread > 0 && (
            <Button
              type="primary"
              icon={<ReadOutlined />}
              onClick={handleMarkAllAsRead}
            >
              全部标记为已读 ({stats.unread})
            </Button>
          )}
        </Space>
      </div>

      {stats && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总通知数"
                value={stats.total}
                prefix={<BellOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="未读通知"
                value={stats.unread}
                valueStyle={{ color: '#ff4d4f' }}
                prefix={<Badge status="error" />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="已读通知"
                value={stats.read}
                valueStyle={{ color: '#52c41a' }}
                prefix={<Badge status="success" />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="通知类型"
                value={Object.keys(stats.by_type || {}).length}
              />
            </Card>
          </Col>
        </Row>
      )}

      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Select
              value={filter}
              onChange={setFilter}
              style={{ width: 120 }}
            >
              <Option value="all">全部</Option>
              <Option value="unread">未读</Option>
              <Option value="read">已读</Option>
            </Select>
            <Select
              value={typeFilter}
              onChange={setTypeFilter}
              style={{ width: 150 }}
            >
              <Option value="all">全部类型</Option>
              <Option value="审批待办">审批待办</Option>
              <Option value="阈值预警">阈值预警</Option>
              <Option value="异常告警">异常告警</Option>
              <Option value="系统通知">系统通知</Option>
              <Option value="提醒">提醒</Option>
            </Select>
          </Space>
        </div>

        {notifications.length === 0 ? (
          <Empty description="暂无通知" />
        ) : (
          <List
            loading={loading}
            dataSource={notifications}
            renderItem={(item) => (
              <List.Item
                style={{
                  backgroundColor: item.is_read ? '#fff' : '#f0f7ff',
                  padding: '12px 16px',
                  marginBottom: 8,
                  borderRadius: 4,
                  cursor: 'pointer',
                  border: item.is_read ? '1px solid #d9d9d9' : '1px solid #1890ff'
                }}
                onClick={() => handleClick(item)}
                actions={[
                  !item.is_read && (
                    <Button
                      type="link"
                      icon={<CheckOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleMarkAsRead(item.id)
                      }}
                    >
                      标记已读
                    </Button>
                  ),
                  <Popconfirm
                    title="确定要删除这条通知吗？"
                    onConfirm={(e) => {
                      e?.stopPropagation()
                      handleDelete(item.id)
                    }}
                    onClick={(e) => e?.stopPropagation()}
                  >
                    <Button
                      type="link"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => e.stopPropagation()}
                    >
                      删除
                    </Button>
                  </Popconfirm>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Badge dot={!item.is_read}>
                      <BellOutlined style={{ fontSize: 20, color: item.is_read ? '#999' : '#1890ff' }} />
                    </Badge>
                  }
                  title={
                    <Space>
                      {getTypeTag(item.type)}
                      {getPriorityTag(item.priority)}
                      <span style={{ fontWeight: item.is_read ? 'normal' : 'bold' }}>
                        {item.title}
                      </span>
                    </Space>
                  }
                  description={
                    <div>
                      {item.content && <div style={{ marginBottom: 4 }}>{item.content}</div>}
                      <div style={{ fontSize: 12, color: '#999' }}>
                        {dayjs(item.created_at).format('YYYY-MM-DD HH:mm:ss')}
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  )
}

export default Notifications

